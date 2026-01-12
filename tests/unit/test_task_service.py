"""Unit tests for task service."""

import pytest
from pydantic import ValidationError
from src.models.task import Task
from src.services import task_service
from src.services.task_service import TaskNotFoundError


# Fixture to reset task service state before each test
@pytest.fixture(autouse=True)
def reset_task_service():
    """Reset task service state before each test."""
    task_service._tasks = []
    task_service._next_id = 1
    yield
    task_service._tasks = []
    task_service._next_id = 1


# Tests for add_task
def test_add_task_with_description():
    """Test adding a task with title and description."""
    task = task_service.add_task("Buy groceries", "Milk, eggs, bread")
    assert task.id == 1
    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs, bread"
    assert task.completed is False


def test_add_task_without_description():
    """Test adding a task with title only."""
    task = task_service.add_task("Call mom")
    assert task.id == 1
    assert task.title == "Call mom"
    assert task.description == ""
    assert task.completed is False


def test_add_task_assigns_sequential_ids():
    """Test that add_task assigns sequential IDs."""
    task1 = task_service.add_task("Task 1")
    task2 = task_service.add_task("Task 2")
    task3 = task_service.add_task("Task 3")
    assert task1.id == 1
    assert task2.id == 2
    assert task3.id == 3


def test_add_task_appends_to_list():
    """Test that add_task appends task to the list."""
    task_service.add_task("Task 1")
    task_service.add_task("Task 2")
    assert len(task_service._tasks) == 2


def test_add_task_empty_title_raises_validation_error():
    """Test that empty title raises ValidationError."""
    with pytest.raises(ValidationError):
        task_service.add_task("   ")


# Tests for get_all_tasks
def test_get_all_tasks_empty_list():
    """Test get_all_tasks returns empty list when no tasks."""
    tasks = task_service.get_all_tasks()
    assert tasks == []


def test_get_all_tasks_returns_all_tasks():
    """Test get_all_tasks returns all tasks."""
    task_service.add_task("Task 1", "Description 1")
    task_service.add_task("Task 2", "Description 2")
    tasks = task_service.get_all_tasks()
    assert len(tasks) == 2
    assert tasks[0].title == "Task 1"
    assert tasks[1].title == "Task 2"


def test_get_all_tasks_returns_copy():
    """Test get_all_tasks returns a copy, not the original list."""
    task_service.add_task("Task 1")
    tasks = task_service.get_all_tasks()
    tasks.append(Task(id=999, title="Fake task"))
    # Original list should not be modified
    assert len(task_service._tasks) == 1


# Tests for get_task_by_id
def test_get_task_by_id_found():
    """Test get_task_by_id returns task when found."""
    task = task_service.add_task("Test task")
    found = task_service.get_task_by_id(task.id)
    assert found == task
    assert found.title == "Test task"


def test_get_task_by_id_not_found():
    """Test get_task_by_id returns None when not found."""
    task_service.add_task("Task 1")
    found = task_service.get_task_by_id(999)
    assert found is None


# Tests for toggle_task_completion
def test_toggle_task_completion_false_to_true():
    """Test toggling task from incomplete to complete."""
    task = task_service.add_task("Task to complete")
    assert task.completed is False
    updated = task_service.toggle_task_completion(task.id)
    assert updated.completed is True


def test_toggle_task_completion_true_to_false():
    """Test toggling task from complete to incomplete."""
    task = task_service.add_task("Task to toggle")
    task.completed = True
    updated = task_service.toggle_task_completion(task.id)
    assert updated.completed is False


def test_toggle_task_completion_invalid_id():
    """Test toggle_task_completion raises TaskNotFoundError for invalid ID."""
    with pytest.raises(TaskNotFoundError, match="Task with ID 999 not found"):
        task_service.toggle_task_completion(999)


# Tests for update_task
def test_update_task_both_fields():
    """Test updating both title and description."""
    task = task_service.add_task("Old title", "Old description")
    updated = task_service.update_task(task.id, title="New title", description="New description")
    assert updated.title == "New title"
    assert updated.description == "New description"


def test_update_task_title_only():
    """Test updating title only."""
    task = task_service.add_task("Old title", "Keep description")
    updated = task_service.update_task(task.id, title="New title")
    assert updated.title == "New title"
    assert updated.description == "Keep description"


def test_update_task_description_only():
    """Test updating description only."""
    task = task_service.add_task("Keep title", "Old description")
    updated = task_service.update_task(task.id, description="New description")
    assert updated.title == "Keep title"
    assert updated.description == "New description"


def test_update_task_invalid_id():
    """Test update_task raises TaskNotFoundError for invalid ID."""
    with pytest.raises(TaskNotFoundError, match="Task with ID 999 not found"):
        task_service.update_task(999, title="New title")


def test_update_task_validates_constraints():
    """Test update_task validates title/description constraints."""
    task = task_service.add_task("Valid title")
    long_title = "a" * 201
    with pytest.raises(ValidationError):
        task_service.update_task(task.id, title=long_title)


# Tests for delete_task
def test_delete_task_removes_from_list():
    """Test delete_task removes task from list."""
    task = task_service.add_task("Task to delete")
    task_service.delete_task(task.id)
    assert len(task_service._tasks) == 0


def test_delete_task_keeps_other_tasks():
    """Test delete_task only removes specified task."""
    task1 = task_service.add_task("Task 1")
    task2 = task_service.add_task("Task 2")
    task3 = task_service.add_task("Task 3")
    task_service.delete_task(task2.id)
    tasks = task_service.get_all_tasks()
    assert len(tasks) == 2
    assert task1 in tasks
    assert task3 in tasks
    assert task2 not in tasks


def test_delete_task_invalid_id():
    """Test delete_task raises TaskNotFoundError for invalid ID."""
    with pytest.raises(TaskNotFoundError, match="Task with ID 999 not found"):
        task_service.delete_task(999)
