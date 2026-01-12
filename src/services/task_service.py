"""Task service for managing todo tasks."""

from typing import Optional
from src.models.task import Task


# Custom Exceptions
class TaskNotFoundError(Exception):
    """Raised when a task with the given ID cannot be found."""
    pass


# Module-level storage (in-memory)
_tasks: list[Task] = []
_next_id: int = 1


def add_task(title: str, description: str = "") -> Task:
    """Create a new task and add it to the task list.

    Args:
        title: Task title (1-200 characters, required)
        description: Task description (0-1000 characters, optional)

    Returns:
        The newly created task with auto-assigned ID

    Raises:
        pydantic.ValidationError: If title/description violates constraints
    """
    global _next_id
    task = Task(id=_next_id, title=title, description=description)
    _tasks.append(task)
    _next_id += 1
    return task


def get_all_tasks() -> list[Task]:
    """Retrieve all tasks in the task list.

    Returns:
        List of all tasks (empty list if no tasks)
    """
    return _tasks.copy()


def get_task_by_id(task_id: int) -> Optional[Task]:
    """Retrieve a single task by its ID.

    Args:
        task_id: The ID of the task to retrieve

    Returns:
        The task with matching ID, or None if not found
    """
    return next((task for task in _tasks if task.id == task_id), None)


def toggle_task_completion(task_id: int) -> Task:
    """Toggle the completion status of a task (complete ↔ incomplete).

    Args:
        task_id: The ID of the task to toggle

    Returns:
        The updated task with toggled completion status

    Raises:
        TaskNotFoundError: If no task with the given ID exists
    """
    task = get_task_by_id(task_id)
    if task is None:
        raise TaskNotFoundError(f"Task with ID {task_id} not found")
    task.completed = not task.completed
    return task


def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Task:
    """Update the title and/or description of an existing task.

    Args:
        task_id: The ID of the task to update
        title: New title (optional, keeps current if None)
        description: New description (optional, keeps current if None)

    Returns:
        The updated task

    Raises:
        TaskNotFoundError: If no task with the given ID exists
        pydantic.ValidationError: If title/description violates constraints
    """
    task = get_task_by_id(task_id)
    if task is None:
        raise TaskNotFoundError(f"Task with ID {task_id} not found")

    # Update only provided fields
    if title is not None:
        task.title = Task(id=task.id, title=title, description=task.description, completed=task.completed).title
    if description is not None:
        task.description = Task(id=task.id, title=task.title, description=description, completed=task.completed).description

    return task


def delete_task(task_id: int) -> None:
    """Remove a task from the task list.

    Args:
        task_id: The ID of the task to delete

    Raises:
        TaskNotFoundError: If no task with the given ID exists
    """
    task = get_task_by_id(task_id)
    if task is None:
        raise TaskNotFoundError(f"Task with ID {task_id} not found")
    _tasks.remove(task)
