# Reusable Intelligence: AI Chatbot Patterns

**Feature**: 003-ai-chatbot
**Date**: 2026-02-05
**Constitution Reference**: Pillar 9 - Reusable Intelligence

> **Definition**: Solutions are captured as reusable patterns, skills, and blueprints.

This document captures reusable components from Phase III that can be leveraged in future phases or projects.

---

## 1. MCP Server Blueprint

**Location**: `backend/src/mcp/`

### Reusable Pattern: Stateless MCP Tool Server

```python
# backend/src/mcp/server.py - Reusable MCP Server Template

from mcp.server import Server
from mcp.types import Tool, TextContent
import asyncio

class MCPServerBlueprint:
    """
    Reusable MCP server pattern for any domain.

    Usage:
    1. Inherit from this blueprint
    2. Register domain-specific tools
    3. Connect to OpenAI Agents SDK
    """

    def __init__(self, name: str, description: str):
        self.server = Server(name)
        self.description = description
        self._register_tools()

    def _register_tools(self):
        """Override to register domain-specific tools"""
        raise NotImplementedError

    def get_tool_definitions(self) -> list[Tool]:
        """Returns tool definitions for agent configuration"""
        return self.server.list_tools()

    async def run(self):
        """Start the MCP server"""
        await self.server.run()
```

### Tool Registration Pattern

```python
# Reusable decorator pattern for MCP tools

def mcp_tool(name: str, description: str):
    """
    Decorator for registering MCP tools with consistent patterns.

    - Enforces user_id parameter for isolation
    - Standardizes return format
    - Adds error handling
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(user_id: str, **kwargs):
            try:
                result = await func(user_id=user_id, **kwargs)
                return {
                    "status": "success",
                    **result
                }
            except EntityNotFound as e:
                return {
                    "status": "error",
                    "error": "not_found",
                    "message": str(e),
                    "suggestion": "Would you like to see available items?"
                }
            except ValidationError as e:
                return {
                    "status": "error",
                    "error": "validation_error",
                    "message": str(e)
                }
        return wrapper
    return decorator
```

### Future Reuse

- **Phase IV**: Kubernetes deployment tools via MCP
- **Phase V**: Event publishing tools, reminder scheduling tools
- **Other Projects**: Any AI-agent-to-application interface

---

## 2. Conversation Persistence Blueprint

**Location**: `backend/src/models/`, `backend/src/services/`

### Reusable Pattern: Stateless Conversation Management

```python
# Reusable conversation persistence pattern

class ConversationManager:
    """
    Stateless conversation management for AI chat applications.

    Key Properties:
    - All state in database (server can restart)
    - User isolation enforced
    - Configurable context window
    - Works with any AI provider
    """

    def __init__(
        self,
        db_session,
        context_limit: int = 20,
        user_id_extractor: Callable = None
    ):
        self.db = db_session
        self.context_limit = context_limit
        self.user_id_extractor = user_id_extractor

    async def get_or_create_conversation(
        self,
        user_id: str,
        conversation_id: str | None = None
    ) -> Conversation:
        """Fetch existing or create new conversation"""
        if conversation_id:
            conv = await self._get_conversation(conversation_id, user_id)
            if not conv:
                raise ConversationNotFound(conversation_id)
            return conv
        return await self._create_conversation(user_id)

    async def get_context(
        self,
        conversation_id: str,
        limit: int = None
    ) -> list[dict]:
        """
        Load conversation history for AI context.
        Returns messages in chronological order.
        """
        limit = limit or self.context_limit
        messages = await self.db.query(Message)\
            .filter(Message.conversation_id == conversation_id)\
            .order_by(Message.created_at.desc())\
            .limit(limit)\
            .all()
        return [
            {"role": m.role.value, "content": m.content}
            for m in reversed(messages)
        ]

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str
    ) -> Message:
        """Store a message (user or assistant)"""
        message = Message(
            conversation_id=conversation_id,
            role=MessageRole(role),
            content=content
        )
        self.db.add(message)
        await self.db.commit()
        return message
```

### Database Schema Template

```sql
-- Reusable conversation schema for any chat application

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    metadata JSONB DEFAULT '{}',  -- Extensible metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tool_calls JSONB DEFAULT NULL,  -- Store tool invocations
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for common query patterns
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at DESC);
```

### Future Reuse

- **Phase V**: Multi-agent conversations, event-driven chat
- **Other Projects**: Customer support bots, documentation assistants

---

## 3. AI Agent Instructions Template

**Location**: `backend/src/mcp/agent_instructions.py`

### Reusable Pattern: Structured Agent Behavior

```python
# Reusable agent instructions template

AGENT_INSTRUCTIONS_TEMPLATE = """
You are a helpful {domain} assistant. You help users {primary_action} through conversation.

## Available Tools

{tool_descriptions}

## Intent Mapping

When a user wants to:
{intent_mappings}

## Response Guidelines

1. **Confirm Actions**: After performing an action, confirm what you did.
   {confirmation_examples}

2. **Handle Errors**: If something goes wrong, offer alternatives.
   {error_handling_examples}

3. **Clarify Ambiguity**: If the user's intent is unclear, ask for clarification.
   {clarification_examples}

4. **Format Output**: Present information clearly.
   {formatting_examples}

## Important Notes

- Always use the user_id provided (from authentication)
- Never expose internal errors to users
- Be conversational but efficient
{additional_notes}
"""

def build_agent_instructions(
    domain: str,
    primary_action: str,
    tools: list[dict],
    intent_mappings: list[tuple[str, str]],
    examples: dict
) -> str:
    """
    Build agent instructions from template.

    Args:
        domain: e.g., "todo", "calendar", "expense"
        primary_action: e.g., "manage their tasks", "schedule meetings"
        tools: List of tool definitions with name and description
        intent_mappings: List of (intent, tool) pairs
        examples: Dict with confirmation, error, clarification, formatting examples

    Returns:
        Formatted agent instructions string
    """
    tool_desc = "\n".join([
        f"- **{t['name']}**: {t['description']}"
        for t in tools
    ])

    intent_map = "\n".join([
        f"- {intent} → use {tool} tool"
        for intent, tool in intent_mappings
    ])

    return AGENT_INSTRUCTIONS_TEMPLATE.format(
        domain=domain,
        primary_action=primary_action,
        tool_descriptions=tool_desc,
        intent_mappings=intent_map,
        confirmation_examples=examples.get("confirmation", ""),
        error_handling_examples=examples.get("error", ""),
        clarification_examples=examples.get("clarification", ""),
        formatting_examples=examples.get("formatting", ""),
        additional_notes=examples.get("notes", "")
    )
```

### Todo Bot Instructions (Concrete Example)

```python
TODO_AGENT_INSTRUCTIONS = build_agent_instructions(
    domain="todo",
    primary_action="manage their tasks",
    tools=[
        {"name": "add_task", "description": "Create a new task"},
        {"name": "list_tasks", "description": "View tasks with optional filter"},
        {"name": "complete_task", "description": "Mark a task as done"},
        {"name": "delete_task", "description": "Remove a task"},
        {"name": "update_task", "description": "Modify task details"},
    ],
    intent_mappings=[
        ("Add/create/remember something", "add_task"),
        ("See/show/list tasks", "list_tasks"),
        ("Complete/finish/done with", "complete_task"),
        ("Delete/remove/cancel", "delete_task"),
        ("Change/update/rename", "update_task"),
    ],
    examples={
        "confirmation": '"I\'ve added \'Buy groceries\' to your tasks."',
        "error": '"I couldn\'t find task 5. Would you like to see your current tasks?"',
        "clarification": '"I found multiple tasks with \'meeting\'. Which one did you mean?"',
        "formatting": '"Here are your tasks:\\n1. Buy groceries (pending)\\n2. Call mom (completed)"',
    }
)
```

### Future Reuse

- **Phase V**: Reminder bot, recurring task bot
- **Other Projects**: Any conversational AI with tool calling

---

## 4. Chat Service Pattern

**Location**: `backend/src/services/chat_service.py`

### Reusable Pattern: AI Chat Orchestration

```python
# Reusable chat service pattern

class ChatService:
    """
    Orchestrates AI chat with tool calling.

    Responsibilities:
    - Manage conversation context
    - Run AI agent with tools
    - Store messages
    - Handle errors gracefully
    """

    def __init__(
        self,
        agent_config: dict,
        conversation_manager: ConversationManager,
        mcp_server: MCPServerBlueprint
    ):
        self.agent = self._create_agent(agent_config, mcp_server)
        self.conversations = conversation_manager

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: str | None = None
    ) -> ChatResponse:
        """
        Process a user message and return AI response.

        Flow:
        1. Get/create conversation
        2. Load context from database
        3. Store user message
        4. Run agent with context + tools
        5. Store assistant response
        6. Return response with tool calls
        """
        # 1. Get conversation
        conversation = await self.conversations.get_or_create_conversation(
            user_id, conversation_id
        )

        # 2. Load context
        context = await self.conversations.get_context(conversation.id)

        # 3. Store user message
        await self.conversations.add_message(
            conversation.id, "user", message
        )

        # 4. Run agent
        result = await self._run_agent(
            user_id=user_id,
            message=message,
            context=context
        )

        # 5. Store assistant response
        await self.conversations.add_message(
            conversation.id, "assistant", result.response
        )

        # 6. Return response
        return ChatResponse(
            conversation_id=str(conversation.id),
            response=result.response,
            tool_calls=result.tool_calls
        )
```

### Future Reuse

- **Any AI chat feature**: Plug in different agents and tools
- **Multi-agent systems**: Orchestrate multiple specialized agents

---

## 5. Frontend Chat Component Blueprint

**Location**: `frontend/src/components/Chat.tsx`

### Reusable Pattern: Chat UI Wrapper

```typescript
// Reusable chat component pattern

interface ChatConfig {
  apiEndpoint: string;
  userId: string;
  conversationId?: string;
  placeholder?: string;
  welcomeMessage?: string;
}

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: Error | null;
  sendMessage: (content: string) => Promise<void>;
  clearChat: () => void;
}

function useChat(config: ChatConfig): UseChatReturn {
  /**
   * Reusable chat state management hook.
   *
   * Features:
   * - Message history state
   * - Loading/error states
   * - API integration
   * - Optimistic updates
   */
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const sendMessage = async (content: string) => {
    // Optimistic update
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      createdAt: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        userId: config.userId,
        conversationId: config.conversationId,
        message: content,
      });

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.response,
        createdAt: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, isLoading, error, sendMessage, clearChat };
}
```

### Future Reuse

- **Any chat interface**: Customer support, documentation bot, etc.
- **Phase V**: Multi-conversation UI with conversation list

---

## 6. Claude Code Skills (Workflows)

**Location**: `.specify/skills/`

### Skill: Chat Feature Implementation

```yaml
# .specify/skills/implement-chat-feature.skill.yaml

name: implement-chat-feature
description: Implement AI chat feature with MCP tools
triggers:
  - "add chat feature"
  - "implement chatbot"
  - "create AI assistant"

steps:
  - name: setup
    actions:
      - "Install openai-agents and mcp dependencies"
      - "Add environment variables for OPENAI_API_KEY"

  - name: models
    actions:
      - "Create Conversation model with user_id, timestamps"
      - "Create Message model with role enum, content"
      - "Run database migration"

  - name: mcp-tools
    actions:
      - "Create MCP server with Official MCP SDK"
      - "Implement domain-specific tools"
      - "Add user isolation to all tools"

  - name: chat-service
    actions:
      - "Create ConversationManager for persistence"
      - "Create ChatService for AI orchestration"
      - "Configure agent instructions"

  - name: api
    actions:
      - "Create POST /chat endpoint"
      - "Create conversation management endpoints"
      - "Add authentication middleware"

  - name: frontend
    actions:
      - "Create useChat hook"
      - "Create Chat component with ChatKit"
      - "Add chat page route"
```

### Skill: MCP Tool Implementation

```yaml
# .specify/skills/implement-mcp-tool.skill.yaml

name: implement-mcp-tool
description: Add new MCP tool to existing server
triggers:
  - "add mcp tool"
  - "create new tool"

steps:
  - name: define
    actions:
      - "Define tool input/output schemas"
      - "Add tool description for agent"

  - name: implement
    actions:
      - "Implement tool function with user_id parameter"
      - "Add error handling with suggestions"
      - "Register tool with MCP server"

  - name: test
    actions:
      - "Write unit test for tool"
      - "Test tool via chat interface"

  - name: document
    actions:
      - "Update agent instructions with new intent mapping"
      - "Add tool to contracts/mcp-tools.yaml"
```

---

## 7. Reusable Test Patterns

**Location**: `backend/tests/`

### Pattern: MCP Tool Testing

```python
# Reusable test pattern for MCP tools

import pytest
from unittest.mock import AsyncMock, MagicMock

class MCPToolTestBase:
    """
    Base class for MCP tool tests.

    Provides:
    - Mock database session
    - Mock task service
    - Standard test cases
    """

    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.fixture
    def mock_task_service(self, mock_db):
        service = MagicMock()
        service.create_task = AsyncMock()
        service.get_tasks = AsyncMock()
        service.update_task = AsyncMock()
        service.delete_task = AsyncMock()
        return service

    async def assert_user_isolation(self, tool_func, user_id: str):
        """Verify tool enforces user isolation"""
        result = await tool_func(user_id="different_user")
        assert "error" in result or result.get("tasks", []) == []

    async def assert_not_found_handling(self, tool_func, user_id: str):
        """Verify tool handles not found gracefully"""
        result = await tool_func(user_id=user_id, task_id="nonexistent")
        assert result.get("error") == "not_found"
        assert "suggestion" in result
```

### Pattern: Chat API Testing

```python
# Reusable test pattern for chat API

class ChatAPITestBase:
    """
    Base class for chat API tests.

    Provides:
    - Test client setup
    - Auth token generation
    - Common assertions
    """

    @pytest.fixture
    def auth_headers(self, test_user):
        token = generate_test_token(test_user.id)
        return {"Authorization": f"Bearer {token}"}

    async def assert_chat_response_format(self, response):
        """Verify chat response has required fields"""
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "response" in data
        assert "tool_calls" in data
        assert isinstance(data["tool_calls"], list)

    async def assert_conversation_persisted(
        self,
        conversation_id: str,
        expected_messages: int
    ):
        """Verify messages stored in database"""
        messages = await get_messages(conversation_id)
        assert len(messages) == expected_messages
```

---

## Summary: Reusable Components

| Component | Location | Future Use |
|-----------|----------|------------|
| MCP Server Blueprint | `backend/src/mcp/` | Any AI-to-app interface |
| Conversation Manager | `backend/src/services/` | Any chat application |
| Agent Instructions Template | `backend/src/mcp/` | Any conversational AI |
| Chat Service Pattern | `backend/src/services/` | Multi-agent systems |
| Chat UI Hook | `frontend/src/hooks/` | Any chat interface |
| MCP Tool Test Base | `backend/tests/` | Testing new tools |
| Chat API Test Base | `backend/tests/` | Testing chat endpoints |
| Claude Code Skills | `.specify/skills/` | Workflow automation |

---

## Integration with Constitution

These patterns fulfill **Pillar 9: Reusable Intelligence**:

- **Claude Code Skills**: Captured in `.specify/skills/` for common workflows
- **MCP servers**: Standardized tool interfaces reusable across phases
- **Blueprints**: Patterns documented for future implementation
- **Constitution**: This document extends governance with implementation patterns
