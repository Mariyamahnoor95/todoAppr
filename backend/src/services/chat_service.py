"""
Chat service for AI-powered task management conversations.

Orchestrates conversation management, AI agent execution, and MCP tool calls.
Implements stateless architecture - all state is stored in the database.

Supports multiple AI providers via OpenAI-compatible API:
- OpenAI (default)
- Groq (free tier available)
- Ollama (local, free)
- OpenRouter (many free models)

Configure via environment variables:
- OPENAI_API_KEY: API key for the provider
- OPENAI_API_BASE: Base URL (optional, for alternative providers)
- CHAT_MODEL: Model name (default: gpt-4o)
"""

import json
import os
from typing import Any, Optional
from uuid import UUID

from openai import OpenAI
from sqlmodel import Session

from ..models.message import MessageRole
from ..mcp.tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    get_mcp_tools,
)
from .conversation_service import ConversationService, ConversationNotFoundError


# Agent instructions for the todo assistant
AGENT_INSTRUCTIONS = """You are a helpful todo assistant. You help users manage their tasks through natural conversation.

## Available Tools

You have access to 5 tools for task management:
- add_task: Create a new task
- list_tasks: View tasks with optional filter (all, pending, completed)
- complete_task: Mark a task as done
- delete_task: Remove a task
- update_task: Modify task details

## Intent Mapping

When a user wants to:
- Add/create/remember something → use add_task tool
- See/show/list tasks → use list_tasks tool
- Complete/finish/done with → use complete_task tool
- Delete/remove/cancel → use delete_task tool
- Change/update/rename → use update_task tool

## Response Guidelines

1. **Confirm Actions**: After performing an action, confirm what you did.
   - "I've added 'Buy groceries' to your tasks."
   - "Done! I've marked 'Call mom' as complete."
   - "I've deleted 'Old meeting' from your tasks."

2. **Handle Errors**: If something goes wrong, offer alternatives.
   - "I couldn't find that task. Would you like to see your current tasks?"

3. **Clarify Ambiguity**: If the user's intent is unclear, ask for clarification.
   - "I'm not sure which task you mean. Can you give me more details?"

4. **Format Lists**: When showing tasks, use a clear format.
   - Show task ID, title, and status
   - Group by status if helpful

## Important Notes

- Always be helpful and conversational
- Never expose internal errors to users
- If a task isn't found, suggest viewing the task list
"""


class ChatService:
    """
    Service for AI chat orchestration.

    Manages conversations, executes OpenAI agent with MCP tools,
    and stores messages for stateless operation.
    """

    def __init__(
        self,
        history_limit: int = 20,
    ):
        """
        Initialize chat service.

        Args:
            history_limit: Maximum messages to include in context

        Environment variables:
            OPENAI_API_KEY: API key for the AI provider
            OPENAI_API_BASE: Base URL for alternative providers (optional)
            CHAT_MODEL: Model to use (default: gpt-4o)
        """
        self.conversation_service = ConversationService(history_limit=history_limit)
        self.model = os.getenv("CHAT_MODEL", "gpt-4o")

        # Support alternative AI providers via OpenAI-compatible API
        api_base = os.getenv("OPENAI_API_BASE")
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=api_base if api_base else None,
        )
        self.tools = get_mcp_tools()

    async def process_message(
        self,
        session: Session,
        user_id: str,
        message: str,
        conversation_id: Optional[UUID] = None,
    ) -> dict[str, Any]:
        """
        Process a user message and return AI response.

        Flow:
        1. Get/create conversation
        2. Load context from database
        3. Store user message
        4. Run agent with context + tools
        5. Store assistant response
        6. Return response with tool calls

        Args:
            session: Database session
            user_id: Authenticated user's ID
            message: User's message
            conversation_id: Optional existing conversation ID

        Returns:
            Dict with conversation_id, response, and tool_calls
        """
        # 1. Get or create conversation
        conversation = self.conversation_service.get_or_create_conversation(
            session=session,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        # 2. Load conversation history
        history = self.conversation_service.get_conversation_history(
            session=session,
            conversation_id=conversation.id,
        )

        # 3. Store user message
        self.conversation_service.add_message(
            session=session,
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=message,
        )

        # 4. Build messages for OpenAI
        messages = [
            {"role": "system", "content": AGENT_INSTRUCTIONS},
            *history,
            {"role": "user", "content": message},
        ]

        # 5. Run agent with tools
        tool_calls_results = []
        response_text = ""

        try:
            # Initial completion with tools
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
            )

            assistant_message = response.choices[0].message

            # Handle tool calls if any
            while assistant_message.tool_calls:
                # Process each tool call
                tool_results = []
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Execute the tool
                    result = self._execute_tool(
                        session=session,
                        user_id=user_id,
                        tool_name=tool_name,
                        tool_args=tool_args,
                    )

                    tool_calls_results.append({
                        "tool": tool_name,
                        "result": result,
                    })

                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    })

                # Add assistant message and tool results to conversation
                messages.append(assistant_message.model_dump())
                messages.extend(tool_results)

                # Get next response
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                )
                assistant_message = response.choices[0].message

            response_text = assistant_message.content or "I processed your request."

        except Exception as e:
            # Graceful error handling
            response_text = (
                "I'm having trouble processing your request right now. "
                "Please try again in a moment."
            )
            # Log the error in production
            print(f"Chat error: {e}")

        # 6. Store assistant response
        self.conversation_service.add_message(
            session=session,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=response_text,
        )

        return {
            "conversation_id": str(conversation.id),
            "response": response_text,
            "tool_calls": tool_calls_results,
        }

    def _execute_tool(
        self,
        session: Session,
        user_id: str,
        tool_name: str,
        tool_args: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute an MCP tool.

        Args:
            session: Database session
            user_id: Authenticated user's ID
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool

        Returns:
            Tool execution result
        """
        tool_map = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task,
            "delete_task": delete_task,
            "update_task": update_task,
        }

        tool_func = tool_map.get(tool_name)
        if not tool_func:
            return {"error": "unknown_tool", "message": f"Unknown tool: {tool_name}"}

        return tool_func(session=session, user_id=user_id, **tool_args)
