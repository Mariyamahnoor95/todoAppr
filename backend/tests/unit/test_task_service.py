"""
Unit tests for TaskService.

Tests task CRUD operations, validation, and user isolation.
"""

import pytest
from uuid import uuid4

from sqlmodel import Session

from src.models.task import Task
from src.models.user import User
from src.services.task_service import (
    TaskService,
    TaskNotFoundError,
    ValidationError,
)


@pytest.fixture
def task_service():
    """Fixture to provide TaskService instance."""
    return TaskService()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Fixture to provide a test user."""
    user = User(email="test@example.com", password_hash="hashed_password")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="another_user")
def another_user_fixture(session: Session):
    """Fixture to provide another test user for isolation tests."""
    user = User(email="another@example.com", password_hash="hashed_password")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# Tests for get_tasks


def test_get_tasks_returns_empty_list_for_new_user(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that get_tasks returns empty list for user with no tasks."""
    tasks = task_service.get_tasks(session, test_user.id)
    assert tasks == []


def test_get_tasks_returns_user_tasks(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that get_tasks returns tasks for specific user."""
    # Create tasks
    task1 = Task(user_id=test_user.id, title="Task 1")
    task2 = Task(user_id=test_user.id, title="Task 2")
    session.add(task1)
    session.add(task2)
    session.commit()

    tasks = task_service.get_tasks(session, test_user.id)
    assert len(tasks) == 2
    task_titles = {task.title for task in tasks}
    assert task_titles == {"Task 1", "Task 2"}


def test_get_tasks_user_isolation(
    task_service: TaskService, session: Session, test_user: User, another_user: User
):
    """Test that get_tasks only returns tasks for the specified user."""
    # Create tasks for different users
    task1 = Task(user_id=test_user.id, title="User 1 Task")
    task2 = Task(user_id=another_user.id, title="User 2 Task")
    session.add(task1)
    session.add(task2)
    session.commit()

    # Get tasks for test_user
    tasks = task_service.get_tasks(session, test_user.id)
    assert len(tasks) == 1
    assert tasks[0].title == "User 1 Task"


def test_get_tasks_pagination(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that get_tasks supports pagination."""
    # Create 5 tasks
    for i in range(5):
        task = Task(user_id=test_user.id, title=f"Task {i}")
        session.add(task)
    session.commit()

    # Get first page (skip=0, limit=2)
    page1 = task_service.get_tasks(session, test_user.id, skip=0, limit=2)
    assert len(page1) == 2

    # Get second page (skip=2, limit=2)
    page2 = task_service.get_tasks(session, test_user.id, skip=2, limit=2)
    assert len(page2) == 2

    # Get third page (skip=4, limit=2)
    page3 = task_service.get_tasks(session, test_user.id, skip=4, limit=2)
    assert len(page3) == 1


def test_get_tasks_filter_by_completed(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that get_tasks can filter by completion status."""
    # Create completed and incomplete tasks
    task1 = Task(user_id=test_user.id, title="Completed Task", completed=True)
    task2 = Task(user_id=test_user.id, title="Incomplete Task", completed=False)
    task3 = Task(user_id=test_user.id, title="Another Completed", completed=True)
    session.add(task1)
    session.add(task2)
    session.add(task3)
    session.commit()

    # Get only completed tasks
    completed = task_service.get_tasks(session, test_user.id, completed=True)
    assert len(completed) == 2
    assert all(task.completed for task in completed)

    # Get only incomplete tasks
    incomplete = task_service.get_tasks(session, test_user.id, completed=False)
    assert len(incomplete) == 1
    assert not incomplete[0].completed


# Tests for get_task_by_id


def test_get_task_by_id_returns_task(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that get_task_by_id returns the correct task."""
    task = Task(user_id=test_user.id, title="Test Task")
    session.add(task)
    session.commit()
    session.refresh(task)

    retrieved = task_service.get_task_by_id(session, task.id, test_user.id)
    assert retrieved.id == task.id
    assert retrieved.title == "Test Task"


def test_get_task_by_id_raises_error_for_nonexistent_task(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that get_task_by_id raises error for non-existent task."""
    fake_id = uuid4()
    with pytest.raises(TaskNotFoundError):
        task_service.get_task_by_id(session, fake_id, test_user.id)


def test_get_task_by_id_raises_error_for_other_user_task(
    task_service: TaskService, session: Session, test_user: User, another_user: User
):
    """Test that get_task_by_id raises error when trying to access another user's task."""
    task = Task(user_id=test_user.id, title="User 1 Task")
    session.add(task)
    session.commit()
    session.refresh(task)

    # Try to access with another_user's ID
    with pytest.raises(TaskNotFoundError):
        task_service.get_task_by_id(session, task.id, another_user.id)


# Tests for create_task


def test_create_task_success(
    task_service: TaskService, session: Session, test_user: User
):
    """Test successful task creation."""
    task = task_service.create_task(
        session, test_user.id, "New Task", "Task description"
    )

    assert task.id is not None
    assert task.user_id == test_user.id
    assert task.title == "New Task"
    assert task.description == "Task description"
    assert task.completed is False


def test_create_task_without_description(
    task_service: TaskService, session: Session, test_user: User
):
    """Test creating task without description."""
    task = task_service.create_task(session, test_user.id, "No description task")

    assert task.title == "No description task"
    assert task.description is None


def test_create_task_trims_whitespace(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that create_task trims whitespace from title and description."""
    task = task_service.create_task(
        session, test_user.id, "  Trimmed Title  ", "  Trimmed Description  "
    )

    assert task.title == "Trimmed Title"
    assert task.description == "Trimmed Description"


def test_create_task_empty_title_raises_error(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that creating task with empty title raises ValidationError."""
    with pytest.raises(ValidationError, match="Title is required"):
        task_service.create_task(session, test_user.id, "")


def test_create_task_whitespace_only_title_raises_error(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that creating task with whitespace-only title raises ValidationError."""
    with pytest.raises(ValidationError, match="Title is required"):
        task_service.create_task(session, test_user.id, "   ")


def test_create_task_title_too_long_raises_error(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that creating task with title exceeding 200 chars raises ValidationError."""
    long_title = "A" * 201
    with pytest.raises(ValidationError, match="must not exceed 200 characters"):
        task_service.create_task(session, test_user.id, long_title)


def test_create_task_description_too_long_raises_error(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that creating task with description exceeding 1000 chars raises ValidationError."""
    long_desc = "A" * 1001
    with pytest.raises(ValidationError, match="must not exceed 1000 characters"):
        task_service.create_task(session, test_user.id, "Title", long_desc)


# Tests for update_task


def test_update_task_title(
    task_service: TaskService, session: Session, test_user: User
):
    """Test updating task title."""
    task = Task(user_id=test_user.id, title="Original Title")
    session.add(task)
    session.commit()
    session.refresh(task)

    updated = task_service.update_task(
        session, task.id, test_user.id, title="Updated Title"
    )

    assert updated.title == "Updated Title"


def test_update_task_description(
    task_service: TaskService, session: Session, test_user: User
):
    """Test updating task description."""
    task = Task(user_id=test_user.id, title="Task", description="Original")
    session.add(task)
    session.commit()
    session.refresh(task)

    updated = task_service.update_task(
        session, task.id, test_user.id, description="Updated description"
    )

    assert updated.description == "Updated description"


def test_update_task_completed_status(
    task_service: TaskService, session: Session, test_user: User
):
    """Test updating task completion status."""
    task = Task(user_id=test_user.id, title="Task", completed=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    updated = task_service.update_task(session, task.id, test_user.id, completed=True)

    assert updated.completed is True


def test_update_task_multiple_fields(
    task_service: TaskService, session: Session, test_user: User
):
    """Test updating multiple fields at once."""
    task = Task(user_id=test_user.id, title="Original", description="Desc", completed=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    updated = task_service.update_task(
        session,
        task.id,
        test_user.id,
        title="New Title",
        description="New Desc",
        completed=True,
    )

    assert updated.title == "New Title"
    assert updated.description == "New Desc"
    assert updated.completed is True


def test_update_task_empty_title_raises_error(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that updating task with empty title raises ValidationError."""
    task = Task(user_id=test_user.id, title="Original")
    session.add(task)
    session.commit()
    session.refresh(task)

    with pytest.raises(ValidationError, match="Title cannot be empty"):
        task_service.update_task(session, task.id, test_user.id, title="  ")


def test_update_task_raises_error_for_other_user(
    task_service: TaskService, session: Session, test_user: User, another_user: User
):
    """Test that updating another user's task raises TaskNotFoundError."""
    task = Task(user_id=test_user.id, title="User 1 Task")
    session.add(task)
    session.commit()
    session.refresh(task)

    with pytest.raises(TaskNotFoundError):
        task_service.update_task(session, task.id, another_user.id, title="Hacked")


# Tests for toggle_completion


def test_toggle_completion_from_false_to_true(
    task_service: TaskService, session: Session, test_user: User
):
    """Test toggling task from incomplete to complete."""
    task = Task(user_id=test_user.id, title="Task", completed=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    updated = task_service.toggle_completion(session, task.id, test_user.id)

    assert updated.completed is True


def test_toggle_completion_from_true_to_false(
    task_service: TaskService, session: Session, test_user: User
):
    """Test toggling task from complete to incomplete."""
    task = Task(user_id=test_user.id, title="Task", completed=True)
    session.add(task)
    session.commit()
    session.refresh(task)

    updated = task_service.toggle_completion(session, task.id, test_user.id)

    assert updated.completed is False


def test_toggle_completion_raises_error_for_other_user(
    task_service: TaskService, session: Session, test_user: User, another_user: User
):
    """Test that toggling another user's task raises TaskNotFoundError."""
    task = Task(user_id=test_user.id, title="User 1 Task", completed=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    with pytest.raises(TaskNotFoundError):
        task_service.toggle_completion(session, task.id, another_user.id)


# Tests for delete_task


def test_delete_task_success(
    task_service: TaskService, session: Session, test_user: User
):
    """Test successful task deletion."""
    task = Task(user_id=test_user.id, title="To Delete")
    session.add(task)
    session.commit()
    task_id = task.id

    task_service.delete_task(session, task_id, test_user.id)

    # Verify task is deleted
    deleted_task = session.get(Task, task_id)
    assert deleted_task is None


def test_delete_task_raises_error_for_nonexistent_task(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that deleting non-existent task raises TaskNotFoundError."""
    fake_id = uuid4()
    with pytest.raises(TaskNotFoundError):
        task_service.delete_task(session, fake_id, test_user.id)


def test_delete_task_raises_error_for_other_user(
    task_service: TaskService, session: Session, test_user: User, another_user: User
):
    """Test that deleting another user's task raises TaskNotFoundError."""
    task = Task(user_id=test_user.id, title="User 1 Task")
    session.add(task)
    session.commit()
    task_id = task.id

    with pytest.raises(TaskNotFoundError):
        task_service.delete_task(session, task_id, another_user.id)


# Tests for get_task_count


def test_get_task_count_returns_zero_for_new_user(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that get_task_count returns 0 for user with no tasks."""
    count = task_service.get_task_count(session, test_user.id)
    assert count == 0


def test_get_task_count_returns_correct_count(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that get_task_count returns correct number of tasks."""
    for i in range(5):
        task = Task(user_id=test_user.id, title=f"Task {i}")
        session.add(task)
    session.commit()

    count = task_service.get_task_count(session, test_user.id)
    assert count == 5


def test_get_task_count_with_completed_filter(
    task_service: TaskService, session: Session, test_user: User
):
    """Test that get_task_count can filter by completion status."""
    task1 = Task(user_id=test_user.id, title="Complete", completed=True)
    task2 = Task(user_id=test_user.id, title="Incomplete", completed=False)
    task3 = Task(user_id=test_user.id, title="Another Complete", completed=True)
    session.add(task1)
    session.add(task2)
    session.add(task3)
    session.commit()

    completed_count = task_service.get_task_count(session, test_user.id, completed=True)
    assert completed_count == 2

    incomplete_count = task_service.get_task_count(session, test_user.id, completed=False)
    assert incomplete_count == 1
