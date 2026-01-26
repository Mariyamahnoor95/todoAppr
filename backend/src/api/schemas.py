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
    user_id: UUID = Field(..., description="Owner user ID")
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
