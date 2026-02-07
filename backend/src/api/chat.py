"""
Chat API endpoints for AI-powered task management.

Provides the POST /api/{user_id}/chat endpoint for natural language
task management through the AI chatbot.
"""

import os
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, status

from .deps import SessionDep, UserIdDep
from .schemas import ChatRequest, ChatResponse, ToolCallResponse
from ..services.chat_service import ChatService
from ..services.conversation_service import ConversationNotFoundError


router = APIRouter(tags=["Chat"])

# Lazy initialization of chat service
_chat_service = None


def get_chat_service() -> ChatService:
    """Get or create the chat service instance."""
    global _chat_service
    if _chat_service is None:
        history_limit = int(os.getenv("CONVERSATION_HISTORY_LIMIT", "20"))
        _chat_service = ChatService(history_limit=history_limit)
    return _chat_service


def reset_chat_service():
    """Reset chat service for testing purposes."""
    global _chat_service
    _chat_service = None


@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send message to AI chatbot",
    description="""
Send a natural language message to the AI chatbot and receive a response.
The chatbot can manage tasks through MCP tools based on user intent.

**Example messages:**
- "Add a task to buy groceries"
- "Show me all my tasks"
- "Mark task 3 as complete"
- "Delete the meeting task"
    """,
)
async def send_chat_message(
    session: SessionDep,
    auth_user_id: UserIdDep,
    user_id: str = Path(..., description="User ID (must match authenticated user)"),
    request: ChatRequest = ...,
) -> ChatResponse:
    """
    Process a chat message and return AI response.

    Args:
        session: Database session
        auth_user_id: Authenticated user ID from JWT
        user_id: User ID from path (must match auth_user_id)
        request: Chat request with message and optional conversation_id

    Returns:
        ChatResponse with conversation_id, response, and tool_calls

    Raises:
        HTTPException 403: If user_id doesn't match authenticated user
        HTTPException 404: If conversation_id provided but not found
        HTTPException 400: If message is empty
    """
    # Verify user is accessing their own chat
    if user_id != auth_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own chat",
        )

    # Validate message
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )

    try:
        # Process message through chat service
        chat_service = get_chat_service()
        result = await chat_service.process_message(
            session=session,
            user_id=user_id,
            message=request.message.strip(),
            conversation_id=request.conversation_id,
        )

        return ChatResponse(
            conversation_id=UUID(result["conversation_id"]),
            response=result["response"],
            tool_calls=[
                ToolCallResponse(tool=tc["tool"], result=tc["result"])
                for tc in result["tool_calls"]
            ],
        )

    except ConversationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    except Exception as e:
        # Log error in production
        print(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your request",
        )
