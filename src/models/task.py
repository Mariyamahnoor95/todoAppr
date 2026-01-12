"""Task model for todo application."""

from pydantic import BaseModel, Field, field_validator


class Task(BaseModel):
    """Represents a single todo item.

    Attributes:
        id: Unique identifier for the task (auto-assigned)
        title: Short description of the task (1-200 characters, required)
        description: Detailed information about the task (0-1000 characters, optional)
        completed: Completion status (default: False)
    """

    id: int = Field(gt=0, description="Unique task identifier")
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: str = Field(default="", max_length=1000, description="Task description")
    completed: bool = Field(default=False, description="Completion status")

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Validate that title is not empty or whitespace only."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Title cannot be empty or whitespace only")
        return stripped

    @field_validator('description')
    @classmethod
    def strip_description(cls, v: str) -> str:
        """Strip whitespace from description."""
        return v.strip()
