"""
Task API endpoints.

Provides REST API for task CRUD operations:
- GET /api/{user_id}/tasks - List tasks
- GET /api/{user_id}/tasks/{id} - Get task details
- POST /api/{user_id}/tasks - Create new task
- PUT /api/{user_id}/tasks/{id} - Update task
- PATCH /api/{user_id}/tasks/{id}/complete - Toggle completion
- DELETE /api/{user_id}/tasks/{id} - Delete task
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session

from ..api.deps import UserIdDep, SessionDep
from ..api.schemas import (
    MessageResponse,
    TaskCreateRequest,
    TaskListResponse,
    TaskResponse,
    TaskUpdateRequest,
)
from ..services.task_service import TaskNotFoundError, TaskService, ValidationError

router = APIRouter(prefix="/{user_id}/tasks", tags=["tasks"])
task_service = TaskService()


def verify_user_id(user_id: str, jwt_user_id: str) -> None:
    """Verify URL user_id matches JWT user_id."""
    if user_id != jwt_user_id:
        raise HTTPException(status_code=403, detail="Access denied")


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    user_id: str,
    jwt_user_id: UserIdDep,
    session: SessionDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
) -> TaskListResponse:
    """Get paginated list of tasks for authenticated user."""
    verify_user_id(user_id, jwt_user_id)

    tasks = task_service.get_tasks(
        session=session,
        user_id=user_id,
        skip=skip,
        limit=limit,
        completed=completed,
    )

    total = task_service.get_task_count(
        session=session, user_id=user_id, completed=completed
    )

    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: UUID,
    jwt_user_id: UserIdDep,
    session: SessionDep,
) -> TaskResponse:
    """Get a single task by ID."""
    verify_user_id(user_id, jwt_user_id)
    try:
        task = task_service.get_task_by_id(
            session=session, task_id=task_id, user_id=user_id
        )
        return TaskResponse.model_validate(task)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    user_id: str,
    task_data: TaskCreateRequest,
    jwt_user_id: UserIdDep,
    session: SessionDep,
) -> TaskResponse:
    """Create a new task."""
    verify_user_id(user_id, jwt_user_id)
    try:
        task = task_service.create_task(
            session=session,
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
        )
        return TaskResponse.model_validate(task)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: UUID,
    task_data: TaskUpdateRequest,
    jwt_user_id: UserIdDep,
    session: SessionDep,
) -> TaskResponse:
    """Update task fields."""
    verify_user_id(user_id, jwt_user_id)
    try:
        task = task_service.update_task(
            session=session,
            task_id=task_id,
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed,
        )
        return TaskResponse.model_validate(task)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    task_id: UUID,
    jwt_user_id: UserIdDep,
    session: SessionDep,
) -> TaskResponse:
    """Toggle task completion status."""
    verify_user_id(user_id, jwt_user_id)
    try:
        task = task_service.toggle_completion(
            session=session, task_id=task_id, user_id=user_id
        )
        return TaskResponse.model_validate(task)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{task_id}", response_model=MessageResponse)
async def delete_task(
    user_id: str,
    task_id: UUID,
    jwt_user_id: UserIdDep,
    session: SessionDep,
) -> MessageResponse:
    """Delete a task."""
    verify_user_id(user_id, jwt_user_id)
    try:
        task_service.delete_task(session=session, task_id=task_id, user_id=user_id)
        return MessageResponse(message="Task deleted successfully")
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
