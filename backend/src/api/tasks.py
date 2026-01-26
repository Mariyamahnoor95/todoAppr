"""
Task API endpoints.

Provides REST API for task CRUD operations:
- GET /tasks - List tasks with pagination and filtering
- GET /tasks/{id} - Get single task
- POST /tasks - Create new task
- PUT /tasks/{id} - Update task
- PATCH /tasks/{id}/toggle - Toggle completion status
- DELETE /tasks/{id} - Delete task
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session

from ..api.deps import CurrentUserDep, SessionDep
from ..api.schemas import (
    MessageResponse,
    TaskCreateRequest,
    TaskListResponse,
    TaskResponse,
    TaskUpdateRequest,
)
from ..services.task_service import TaskNotFoundError, TaskService, ValidationError

router = APIRouter(prefix="/tasks", tags=["tasks"])
task_service = TaskService()


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    current_user: CurrentUserDep,
    session: SessionDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
) -> TaskListResponse:
    """
    Get paginated list of tasks for authenticated user.

    Query Parameters:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return (1-100)
        completed: Optional filter by completion status

    Returns:
        TaskListResponse with tasks array and metadata
    """
    tasks = task_service.get_tasks(
        session=session,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        completed=completed,
    )

    total = task_service.get_task_count(
        session=session, user_id=current_user.id, completed=completed
    )

    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TaskResponse:
    """
    Get a single task by ID.

    Args:
        task_id: Task UUID

    Returns:
        TaskResponse with task details

    Raises:
        404: Task not found or user doesn't have access
    """
    try:
        task = task_service.get_task_by_id(
            session=session, task_id=task_id, user_id=current_user.id
        )
        return TaskResponse.model_validate(task)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreateRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TaskResponse:
    """
    Create a new task.

    Request Body:
        title: Task title (1-200 characters, required)
        description: Optional description (max 1000 characters)

    Returns:
        TaskResponse with created task details

    Raises:
        400: Validation error (invalid title or description)
    """
    try:
        task = task_service.create_task(
            session=session,
            user_id=current_user.id,
            title=task_data.title,
            description=task_data.description,
        )
        return TaskResponse.model_validate(task)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdateRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TaskResponse:
    """
    Update task fields.

    Args:
        task_id: Task UUID

    Request Body (all optional):
        title: New task title (1-200 characters)
        description: New description (max 1000 characters)
        completed: New completion status

    Returns:
        TaskResponse with updated task details

    Raises:
        400: Validation error
        404: Task not found or user doesn't have access
    """
    try:
        task = task_service.update_task(
            session=session,
            task_id=task_id,
            user_id=current_user.id,
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed,
        )
        return TaskResponse.model_validate(task)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{task_id}/toggle", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TaskResponse:
    """
    Toggle task completion status.

    Args:
        task_id: Task UUID

    Returns:
        TaskResponse with updated task (toggled completion status)

    Raises:
        404: Task not found or user doesn't have access
    """
    try:
        task = task_service.toggle_completion(
            session=session, task_id=task_id, user_id=current_user.id
        )
        return TaskResponse.model_validate(task)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{task_id}", response_model=MessageResponse)
async def delete_task(
    task_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> MessageResponse:
    """
    Delete a task.

    Args:
        task_id: Task UUID

    Returns:
        MessageResponse with success message

    Raises:
        404: Task not found or user doesn't have access
    """
    try:
        task_service.delete_task(session=session, task_id=task_id, user_id=current_user.id)
        return MessageResponse(message="Task deleted successfully")
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
