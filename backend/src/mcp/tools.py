"""MCP tools for task management via AI chatbot.

These tools are stateless and designed to be called by the OpenAI Agents SDK.
Each tool requires a user_id parameter to enforce user isolation.
"""

from typing import Any, Optional
from uuid import UUID

from sqlmodel import Session

from ..services.task_service import TaskService, TaskNotFoundError, ValidationError


# Singleton task service instance
_task_service = TaskService()


def get_mcp_tools() -> list[dict[str, Any]]:
    """Return list of MCP tool definitions for OpenAI Agents SDK."""
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task for the user. Use this when the user mentions adding, creating, remembering, or needing to do something.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Title of the task to create (1-200 characters)",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description for the task (max 1000 characters)",
                        },
                    },
                    "required": ["title"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "Retrieve the user's tasks. Use this when the user wants to see, show, list, or view their tasks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter tasks by status. 'all' returns everything, 'pending' returns incomplete tasks, 'completed' returns finished tasks.",
                            "default": "all",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as complete. Use this when the user says they finished, completed, or are done with a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "ID of the task to complete (UUID format)",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task from the user's list. Use this when the user wants to remove, delete, or cancel a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "ID of the task to delete (UUID format)",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update a task's title or description. Use this when the user wants to change, update, rename, or modify a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "ID of the task to update (UUID format)",
                        },
                        "title": {
                            "type": "string",
                            "description": "New title for the task (optional)",
                        },
                        "description": {
                            "type": "string",
                            "description": "New description for the task (optional)",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
    ]


def add_task(
    session: Session,
    user_id: str,
    title: str,
    description: Optional[str] = None,
) -> dict[str, Any]:
    """
    Create a new task for the user.

    Args:
        session: Database session
        user_id: Authenticated user's ID
        title: Task title
        description: Optional task description

    Returns:
        Dict with task_id, status, and title
    """
    try:
        task = _task_service.create_task(
            session=session,
            user_id=user_id,
            title=title,
            description=description,
        )
        return {
            "task_id": str(task.id),
            "status": "created",
            "title": task.title,
        }
    except ValidationError as e:
        return {
            "error": "validation_error",
            "message": str(e),
        }


def list_tasks(
    session: Session,
    user_id: str,
    status: str = "all",
) -> dict[str, Any]:
    """
    Retrieve user's tasks with optional filtering.

    Args:
        session: Database session
        user_id: Authenticated user's ID
        status: Filter by "all", "pending", or "completed"

    Returns:
        Dict with tasks array and count
    """
    # Map status to completed filter
    completed_filter: Optional[bool] = None
    if status == "pending":
        completed_filter = False
    elif status == "completed":
        completed_filter = True

    tasks = _task_service.get_tasks(
        session=session,
        user_id=user_id,
        completed=completed_filter,
        limit=100,
    )

    return {
        "tasks": [
            {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
            }
            for task in tasks
        ],
        "count": len(tasks),
    }


def complete_task(
    session: Session,
    user_id: str,
    task_id: str,
) -> dict[str, Any]:
    """
    Mark a task as complete.

    Args:
        session: Database session
        user_id: Authenticated user's ID
        task_id: ID of task to complete

    Returns:
        Dict with task_id, status, and title
    """
    try:
        task_uuid = UUID(task_id)
        task = _task_service.get_task_by_id(session, task_uuid, user_id)

        # Update to completed
        updated_task = _task_service.update_task(
            session=session,
            task_id=task_uuid,
            user_id=user_id,
            completed=True,
        )

        return {
            "task_id": str(updated_task.id),
            "status": "completed",
            "title": updated_task.title,
        }
    except TaskNotFoundError:
        return {
            "error": "task_not_found",
            "message": f"Task {task_id} not found",
            "suggestion": "Would you like to see your current tasks?",
        }
    except ValueError:
        return {
            "error": "invalid_task_id",
            "message": f"Invalid task ID format: {task_id}",
            "suggestion": "Task IDs should be in UUID format.",
        }


def delete_task(
    session: Session,
    user_id: str,
    task_id: str,
) -> dict[str, Any]:
    """
    Delete a task from the user's list.

    Args:
        session: Database session
        user_id: Authenticated user's ID
        task_id: ID of task to delete

    Returns:
        Dict with task_id, status, and title
    """
    try:
        task_uuid = UUID(task_id)
        task = _task_service.get_task_by_id(session, task_uuid, user_id)
        task_title = task.title

        _task_service.delete_task(
            session=session,
            task_id=task_uuid,
            user_id=user_id,
        )

        return {
            "task_id": task_id,
            "status": "deleted",
            "title": task_title,
        }
    except TaskNotFoundError:
        return {
            "error": "task_not_found",
            "message": f"Task {task_id} not found",
            "suggestion": "Would you like to see your current tasks?",
        }
    except ValueError:
        return {
            "error": "invalid_task_id",
            "message": f"Invalid task ID format: {task_id}",
            "suggestion": "Task IDs should be in UUID format.",
        }


def update_task(
    session: Session,
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> dict[str, Any]:
    """
    Update a task's title or description.

    Args:
        session: Database session
        user_id: Authenticated user's ID
        task_id: ID of task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Dict with task_id, status, and title
    """
    try:
        task_uuid = UUID(task_id)

        updated_task = _task_service.update_task(
            session=session,
            task_id=task_uuid,
            user_id=user_id,
            title=title,
            description=description,
        )

        return {
            "task_id": str(updated_task.id),
            "status": "updated",
            "title": updated_task.title,
        }
    except TaskNotFoundError:
        return {
            "error": "task_not_found",
            "message": f"Task {task_id} not found",
            "suggestion": "Would you like to see your current tasks?",
        }
    except ValidationError as e:
        return {
            "error": "validation_error",
            "message": str(e),
        }
    except ValueError:
        return {
            "error": "invalid_task_id",
            "message": f"Invalid task ID format: {task_id}",
            "suggestion": "Task IDs should be in UUID format.",
        }
