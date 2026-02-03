"""
Task model for todo items.

Represents a todo task with title, description, completion status,
and timestamps. Each task belongs to a specific user.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """
    Task model for todo items.

    Attributes:
        id: Unique task identifier (UUID)
        user_id: Better Auth user ID (string)
        title: Task title (1-200 characters, required)
        description: Optional task description (max 1000 characters)
        completed: Completion status (default False)
        created_at: Task creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "tasks"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(nullable=False, index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
