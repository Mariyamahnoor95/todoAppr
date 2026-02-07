"""
Pydantic schemas for API request and response validation.

Defines data transfer objects (DTOs) for authentication and task endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# Auth Schemas


class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=100, description="User's password")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "SecurePassword123!",
                }
            ]
        }
    }


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "SecurePassword123!",
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """Response schema for user data."""

    id: UUID = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "created_at": "2024-01-15T10:30:00Z",
                }
            ]
        }
    }


class AuthResponse(BaseModel):
    """Response schema for authentication endpoints."""

    user: UserResponse = Field(..., description="Authenticated user data")
    message: str = Field(..., description="Success message")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                        "created_at": "2024-01-15T10:30:00Z",
                    },
                    "message": "Login successful",
                }
            ]
        }
    }


class MessageResponse(BaseModel):
    """Generic message response schema."""

    message: str = Field(..., description="Response message")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Operation completed successfully",
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str = Field(..., description="Error message")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "Invalid credentials",
                }
            ]
        }
    }


# Task Schemas


class TaskCreateRequest(BaseModel):
    """Request schema for creating a task."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(
        None, max_length=1000, description="Optional task description"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread, and vegetables",
                }
            ]
        }
    }


class TaskUpdateRequest(BaseModel):
    """Request schema for updating a task."""

    title: str | None = Field(
        None, min_length=1, max_length=200, description="New task title"
    )
    description: str | None = Field(
        None, max_length=1000, description="New task description"
    )
    completed: bool | None = Field(None, description="New completion status")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Buy groceries and cook dinner",
                    "completed": True,
                }
            ]
        }
    }


class TaskResponse(BaseModel):
    """Response schema for task data."""

    id: UUID = Field(..., description="Task unique identifier")
    user_id: str = Field(..., description="Owner user ID")
    title: str = Field(..., description="Task title")
    description: str | None = Field(None, description="Task description")
    completed: bool = Field(..., description="Completion status")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174001",
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                    "completed": False,
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z",
                }
            ]
        },
    }


class TaskListResponse(BaseModel):
    """Response schema for paginated task list."""

    tasks: list[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks matching criteria")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tasks": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174001",
                            "user_id": "123e4567-e89b-12d3-a456-426614174000",
                            "title": "Buy groceries",
                            "description": "Milk, eggs, bread",
                            "completed": False,
                            "created_at": "2024-01-15T10:30:00Z",
                            "updated_at": "2024-01-15T10:30:00Z",
                        }
                    ],
                    "total": 1,
                    "skip": 0,
                    "limit": 100,
                }
            ]
        }
    }


# Chat Schemas (Phase III)


class ToolCallResponse(BaseModel):
    """Response schema for MCP tool call results."""

    tool: str = Field(..., description="Name of the MCP tool invoked")
    result: dict = Field(..., description="Result from the tool execution")


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    conversation_id: UUID | None = Field(
        None, description="Existing conversation ID. If not provided, a new conversation is created."
    )
    message: str = Field(
        ..., min_length=1, max_length=1000, description="User's natural language message"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Add a task to buy groceries",
                },
                {
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "message": "Show me all my tasks",
                },
            ]
        }
    }


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    conversation_id: UUID = Field(..., description="The conversation ID (new or existing)")
    response: str = Field(..., description="AI assistant's response message")
    tool_calls: list[ToolCallResponse] = Field(
        default_factory=list, description="List of MCP tools invoked during processing"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "response": "I've added 'Buy groceries' to your tasks.",
                    "tool_calls": [
                        {
                            "tool": "add_task",
                            "result": {
                                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                                "status": "created",
                                "title": "Buy groceries",
                            },
                        }
                    ],
                }
            ]
        }
    }


class ConversationMessageResponse(BaseModel):
    """Response schema for a conversation message."""

    id: UUID = Field(..., description="Message unique identifier")
    role: str = Field(..., description="Message sender role (user or assistant)")
    content: str = Field(..., description="Message content")
    created_at: datetime = Field(..., description="Message creation timestamp")

    model_config = {"from_attributes": True}


class ConversationSummaryResponse(BaseModel):
    """Response schema for conversation list item."""

    id: UUID = Field(..., description="Conversation unique identifier")
    created_at: datetime = Field(..., description="Conversation creation timestamp")
    updated_at: datetime = Field(..., description="Conversation last update timestamp")
    message_count: int = Field(default=0, description="Number of messages in conversation")
    last_message_preview: str | None = Field(
        None, description="Preview of last message (max 100 chars)"
    )


class ConversationListResponse(BaseModel):
    """Response schema for conversation list."""

    conversations: list[ConversationSummaryResponse] = Field(
        ..., description="List of conversations"
    )
    total: int = Field(..., description="Total number of conversations")
    limit: int = Field(..., description="Maximum number returned")
    offset: int = Field(..., description="Number of conversations skipped")


class ConversationDetailResponse(BaseModel):
    """Response schema for conversation with messages."""

    id: UUID = Field(..., description="Conversation unique identifier")
    created_at: datetime = Field(..., description="Conversation creation timestamp")
    updated_at: datetime = Field(..., description="Conversation last update timestamp")
    messages: list[ConversationMessageResponse] = Field(
        ..., description="Messages in the conversation"
    )
