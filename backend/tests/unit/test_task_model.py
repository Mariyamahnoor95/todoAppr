"""
Unit tests for Task model.

Tests task model validation, relationships, and database constraints.
"""

import pytest
from datetime import datetime
from uuid import UUID

from sqlmodel import Session, select

from src.models.task import Task
from src.models.user import User


def test_task_model_has_required_fields(session: Session):
    """Test that Task model has all required fields."""
    # Create a test user first
    user = User(email="test@example.com", password_hash="hashed_password")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create a task
    task = Task(
        user_id=user.id,
        title="Test Task",
        description="Test description",
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    assert isinstance(task.id, UUID)
    assert task.user_id == user.id
    assert task.title == "Test Task"
    assert task.description == "Test description"
    assert task.completed is False  # Default value
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_model_title_validation(session: Session):
    """Test that task title has length constraints."""
    user = User(email="test@example.com", password_hash="hashed_password")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Test minimum length (should accept 1 character)
    task = Task(user_id=user.id, title="A")
    session.add(task)
    session.commit()
    session.refresh(task)
    assert task.title == "A"

    # Test maximum length (200 characters)
    long_title = "A" * 200
    task2 = Task(user_id=user.id, title=long_title)
    session.add(task2)
    session.commit()
    session.refresh(task2)
    assert len(task2.title) == 200


def test_task_model_description_optional(session: Session):
    """Test that task description is optional."""
    user = User(email="test@example.com", password_hash="hashed_password")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Task without description
    task = Task(user_id=user.id, title="No description task")
    session.add(task)
    session.commit()
    session.refresh(task)

    assert task.description is None


def test_task_model_description_max_length(session: Session):
    """Test that task description has maximum length constraint."""
    user = User(email="test@example.com", password_hash="hashed_password")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Maximum length (1000 characters)
    long_desc = "A" * 1000
    task = Task(user_id=user.id, title="Long desc", description=long_desc)
    session.add(task)
    session.commit()
    session.refresh(task)

    assert len(task.description) == 1000


def test_task_model_foreign_key_relationship(session: Session):
    """Test that task has proper foreign key to user."""
    user = User(email="test@example.com", password_hash="hashed_password")
    session.add(user)
    session.commit()
    session.refresh(user)

    task = Task(user_id=user.id, title="Test Task")
    session.add(task)
    session.commit()
    session.refresh(task)

    # Verify foreign key relationship
    assert task.user_id == user.id

    # Retrieve user and verify relationship
    retrieved_user = session.get(User, user.id)
    assert retrieved_user is not None


def test_task_model_completed_default_false(session: Session):
    """Test that task completed field defaults to False."""
    user = User(email="test@example.com", password_hash="hashed_password")
    session.add(user)
    session.commit()
    session.refresh(user)

    task = Task(user_id=user.id, title="Test Task")
    session.add(task)
    session.commit()
    session.refresh(task)

    assert task.completed is False


def test_task_model_completed_can_be_set(session: Session):
    """Test that task completed field can be set to True."""
    user = User(email="test@example.com", password_hash="hashed_password")
    session.add(user)
    session.commit()
    session.refresh(user)

    task = Task(user_id=user.id, title="Completed Task", completed=True)
    session.add(task)
    session.commit()
    session.refresh(task)

    assert task.completed is True


def test_task_model_timestamps(session: Session):
    """Test that task has created_at and updated_at timestamps."""
    user = User(email="test@example.com", password_hash="hashed_password")
    session.add(user)
    session.commit()
    session.refresh(user)

    task = Task(user_id=user.id, title="Test Task")
    session.add(task)
    session.commit()
    session.refresh(task)

    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)
    # Both should be approximately the same on creation
    assert abs((task.created_at - task.updated_at).total_seconds()) < 1


def test_task_model_database_persistence(session: Session):
    """Test that task persists to database and can be retrieved."""
    user = User(email="test@example.com", password_hash="hashed_password")
    session.add(user)
    session.commit()
    session.refresh(user)

    task = Task(
        user_id=user.id,
        title="Persistent Task",
        description="This task should persist",
        completed=True,
    )
    session.add(task)
    session.commit()
    task_id = task.id

    # Clear session and retrieve task
    session.expire_all()
    retrieved_task = session.get(Task, task_id)

    assert retrieved_task is not None
    assert retrieved_task.title == "Persistent Task"
    assert retrieved_task.description == "This task should persist"
    assert retrieved_task.completed is True


def test_task_model_multiple_tasks_per_user(session: Session):
    """Test that a user can have multiple tasks."""
    user = User(email="test@example.com", password_hash="hashed_password")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create multiple tasks
    task1 = Task(user_id=user.id, title="Task 1")
    task2 = Task(user_id=user.id, title="Task 2")
    task3 = Task(user_id=user.id, title="Task 3")

    session.add(task1)
    session.add(task2)
    session.add(task3)
    session.commit()

    # Retrieve all tasks for user
    statement = select(Task).where(Task.user_id == user.id)
    tasks = session.exec(statement).all()

    assert len(tasks) == 3
    task_titles = {task.title for task in tasks}
    assert task_titles == {"Task 1", "Task 2", "Task 3"}
