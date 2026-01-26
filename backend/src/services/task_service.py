"""
Task service for CRUD operations on todo items.

Handles task creation, retrieval, updates, deletion, and completion toggling.
Enforces user isolation - users can only access their own tasks.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Session, select, func

from ..models.task import Task


# Custom exceptions
class TaskNotFoundError(Exception):
    """Raised when a task is not found or user doesn't have access."""

    pass


class ValidationError(Exception):
    """Raised when task data fails validation."""

    pass


class TaskService:
    """
    Service for task CRUD operations.

    All methods enforce user isolation - tasks are scoped to the authenticated user.
    """

    def get_tasks(
        self,
        session: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        completed: Optional[bool] = None,
    ) -> list[Task]:
        """
        Get paginated list of tasks for a user.

        Args:
            session: Database session
            user_id: User ID to filter tasks
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            completed: Optional filter by completion status

        Returns:
            List of Task objects ordered by creation date (newest first)
        """
        query = select(Task).where(Task.user_id == user_id)

        if completed is not None:
            query = query.where(Task.completed == completed)

        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)

        return list(session.exec(query).all())

    def get_task_by_id(self, session: Session, task_id: UUID, user_id: UUID) -> Task:
        """
        Get a single task by ID with user ownership verification.

        Args:
            session: Database session
            task_id: Task ID to retrieve
            user_id: User ID for ownership verification

        Returns:
            Task object if found and owned by user

        Raises:
            TaskNotFoundError: If task doesn't exist or user doesn't own it
        """
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            raise TaskNotFoundError(f"Task {task_id} not found")

        return task

    def create_task(
        self,
        session: Session,
        user_id: UUID,
        title: str,
        description: Optional[str] = None,
    ) -> Task:
        """
        Create a new task.

        Args:
            session: Database session
            user_id: User ID who owns the task
            title: Task title (1-200 characters)
            description: Optional description (max 1000 characters)

        Returns:
            Created Task object

        Raises:
            ValidationError: If title or description fail validation
        """
        # Validate title
        if not title or not title.strip():
            raise ValidationError("Title is required")

        title = title.strip()
        if len(title) > 200:
            raise ValidationError("Title must not exceed 200 characters")

        # Validate description
        if description:
            description = description.strip()
            if len(description) > 1000:
                raise ValidationError("Description must not exceed 1000 characters")
            if not description:  # Empty after strip
                description = None

        # Create task
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    def update_task(
        self,
        session: Session,
        task_id: UUID,
        user_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> Task:
        """
        Update task fields.

        Args:
            session: Database session
            task_id: Task ID to update
            user_id: User ID for ownership verification
            title: New title (optional)
            description: New description (optional)
            completed: New completion status (optional)

        Returns:
            Updated Task object

        Raises:
            TaskNotFoundError: If task doesn't exist or user doesn't own it
            ValidationError: If new values fail validation
        """
        task = self.get_task_by_id(session, task_id, user_id)

        # Update title if provided
        if title is not None:
            title = title.strip()
            if not title:
                raise ValidationError("Title cannot be empty")
            if len(title) > 200:
                raise ValidationError("Title must not exceed 200 characters")
            task.title = title

        # Update description if provided
        if description is not None:
            description = description.strip()
            if len(description) > 1000:
                raise ValidationError("Description must not exceed 1000 characters")
            task.description = description if description else None

        # Update completion status if provided
        if completed is not None:
            task.completed = completed

        # Update timestamp
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    def toggle_completion(self, session: Session, task_id: UUID, user_id: UUID) -> Task:
        """
        Toggle task completion status.

        Args:
            session: Database session
            task_id: Task ID to toggle
            user_id: User ID for ownership verification

        Returns:
            Updated Task object with toggled completion status

        Raises:
            TaskNotFoundError: If task doesn't exist or user doesn't own it
        """
        task = self.get_task_by_id(session, task_id, user_id)
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    def delete_task(self, session: Session, task_id: UUID, user_id: UUID) -> None:
        """
        Delete a task.

        Args:
            session: Database session
            task_id: Task ID to delete
            user_id: User ID for ownership verification

        Raises:
            TaskNotFoundError: If task doesn't exist or user doesn't own it
        """
        task = self.get_task_by_id(session, task_id, user_id)

        session.delete(task)
        session.commit()

    def get_task_count(
        self, session: Session, user_id: UUID, completed: Optional[bool] = None
    ) -> int:
        """
        Get total count of tasks for a user.

        Args:
            session: Database session
            user_id: User ID to count tasks for
            completed: Optional filter by completion status

        Returns:
            Total number of tasks matching criteria
        """
        query = select(func.count()).select_from(Task).where(Task.user_id == user_id)

        if completed is not None:
            query = query.where(Task.completed == completed)

        return session.exec(query).one()
