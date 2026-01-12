"""Unit tests for Task model."""

import pytest
from pydantic import ValidationError
from src.models.task import Task


def test_task_creation_with_all_fields():
    """Test creating a task with all fields provided."""
    task = Task(id=1, title="Buy groceries", description="Milk, eggs, bread", completed=False)
    assert task.id == 1
    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs, bread"
    assert task.completed is False


def test_task_creation_default_completed():
    """Test that completed defaults to False."""
    task = Task(id=1, title="Test task")
    assert task.completed is False


def test_task_creation_default_description():
    """Test that description defaults to empty string."""
    task = Task(id=1, title="Test task")
    assert task.description == ""


def test_task_validation_empty_title():
    """Test that empty title raises ValidationError."""
    with pytest.raises(ValidationError, match="Title cannot be empty"):
        Task(id=1, title="   ")


def test_task_validation_title_too_long():
    """Test that title > 200 chars raises ValidationError."""
    long_title = "a" * 201
    with pytest.raises(ValidationError):
        Task(id=1, title=long_title)


def test_task_validation_description_too_long():
    """Test that description > 1000 chars raises ValidationError."""
    long_description = "a" * 1001
    with pytest.raises(ValidationError):
        Task(id=1, title="Valid title", description=long_description)


def test_task_validation_title_exactly_200_chars():
    """Test boundary: title with exactly 200 chars is valid."""
    title_200 = "a" * 200
    task = Task(id=1, title=title_200)
    assert len(task.title) == 200


def test_task_validation_description_exactly_1000_chars():
    """Test boundary: description with exactly 1000 chars is valid."""
    desc_1000 = "b" * 1000
    task = Task(id=1, title="Valid title", description=desc_1000)
    assert len(task.description) == 1000


def test_task_title_whitespace_stripped():
    """Test that title whitespace is stripped."""
    task = Task(id=1, title="  Test task  ")
    assert task.title == "Test task"


def test_task_description_whitespace_stripped():
    """Test that description whitespace is stripped."""
    task = Task(id=1, title="Test", description="  Test description  ")
    assert task.description == "Test description"
