"""Database models for the Todo application."""

# Models are imported here for Alembic autodiscovery
from .user import User
from .task import Task

__all__ = ["User", "Task"]
