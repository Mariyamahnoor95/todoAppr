"""Integration tests for full user workflows."""

import pytest
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


# User Story 1: Add and View Tasks
def test_add_task_with_full_details_and_view():
    """Test adding a task with title and description, then viewing it."""
    # Add task
    task = task_service.add_task("Buy groceries", "Milk, eggs, bread")

    # Verify task in list
    tasks = task_service.get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0].id == task.id
    assert tasks[0].title == "Buy groceries"
    assert tasks[0].description == "Milk, eggs, bread"
    assert tasks[0].completed is False


def test_add_task_with_title_only_and_view():
    """Test adding a task with title only, then viewing it."""
    # Add task
    task = task_service.add_task("Call mom")

    # Verify task in list
    tasks = task_service.get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Call mom"
    assert tasks[0].description == ""


def test_view_empty_list():
    """Test viewing an empty task list."""
    tasks = task_service.get_all_tasks()
    assert tasks == []


def test_view_multiple_tasks():
    """Test viewing multiple tasks."""
    task_service.add_task("Task 1", "Description 1")
    task_service.add_task("Task 2", "Description 2")
    task_service.add_task("Task 3")

    tasks = task_service.get_all_tasks()
    assert len(tasks) == 3


# User Story 2: Mark Tasks Complete
def test_mark_incomplete_task_complete():
    """Test marking an incomplete task as complete."""
    task = task_service.add_task("Task to complete")
    assert task.completed is False

    # Mark complete
    task_service.toggle_task_completion(task.id)

    # Verify in list
    tasks = task_service.get_all_tasks()
    assert tasks[0].completed is True


def test_mark_complete_task_incomplete():
    """Test marking a complete task as incomplete."""
    task = task_service.add_task("Task to toggle")
    task.completed = True

    # Mark incomplete
    task_service.toggle_task_completion(task.id)

    # Verify in list
    tasks = task_service.get_all_tasks()
    assert tasks[0].completed is False


def test_mark_complete_invalid_id_error():
    """Test marking non-existent task shows error."""
    with pytest.raises(TaskNotFoundError):
        task_service.toggle_task_completion(999)


def test_view_tasks_with_mixed_completion_status():
    """Test viewing tasks with mixed completion status."""
    task1 = task_service.add_task("Incomplete task")
    task2 = task_service.add_task("Complete task")
    task_service.toggle_task_completion(task2.id)

    tasks = task_service.get_all_tasks()
    assert len(tasks) == 2
    assert tasks[0].completed is False
    assert tasks[1].completed is True


# User Story 3: Update Task Details
def test_update_both_title_and_description():
    """Test updating both title and description."""
    task = task_service.add_task("Buy grocries", "Milk")

    # Update both
    task_service.update_task(task.id, title="Buy groceries", description="Milk, eggs, bread")

    # Verify
    tasks = task_service.get_all_tasks()
    assert tasks[0].title == "Buy groceries"
    assert tasks[0].description == "Milk, eggs, bread"


def test_update_title_only():
    """Test updating only title, keeping description unchanged."""
    task = task_service.add_task("Old title", "Keep this description")

    # Update title only
    task_service.update_task(task.id, title="New title")

    # Verify
    tasks = task_service.get_all_tasks()
    assert tasks[0].title == "New title"
    assert tasks[0].description == "Keep this description"


def test_update_description_only():
    """Test updating only description, keeping title unchanged."""
    task = task_service.add_task("Keep this title", "Old description")

    # Update description only
    task_service.update_task(task.id, description="New description")

    # Verify
    tasks = task_service.get_all_tasks()
    assert tasks[0].title == "Keep this title"
    assert tasks[0].description == "New description"


def test_update_invalid_id_error():
    """Test updating non-existent task shows error."""
    with pytest.raises(TaskNotFoundError):
        task_service.update_task(999, title="New title")


# User Story 4: Delete Unwanted Tasks
def test_delete_task_removes_from_list():
    """Test deleting a task removes it from the list."""
    task = task_service.add_task("Task to delete")

    # Delete task
    task_service.delete_task(task.id)

    # Verify not in list
    tasks = task_service.get_all_tasks()
    assert len(tasks) == 0


def test_delete_task_keeps_others():
    """Test deleting one task keeps others in the list."""
    task1 = task_service.add_task("Task 1")
    task2 = task_service.add_task("Task 2")
    task3 = task_service.add_task("Task 3")

    # Delete task 2
    task_service.delete_task(task2.id)

    # Verify task 1 and 3 remain
    tasks = task_service.get_all_tasks()
    assert len(tasks) == 2
    assert tasks[0].id == task1.id
    assert tasks[1].id == task3.id


def test_delete_invalid_id_error():
    """Test deleting non-existent task shows error."""
    with pytest.raises(TaskNotFoundError):
        task_service.delete_task(999)


def test_delete_then_access_by_id_error():
    """Test accessing deleted task by ID shows error."""
    task = task_service.add_task("Task to delete")
    task_service.delete_task(task.id)

    # Try to access deleted task
    with pytest.raises(TaskNotFoundError):
        task_service.update_task(task.id, title="Update deleted")


# Full workflow test
def test_complete_workflow():
    """Test complete workflow: add → view → complete → update → delete."""
    # Add tasks
    task1 = task_service.add_task("Buy groceries", "Milk, eggs")
    task2 = task_service.add_task("Call mom")

    # View
    tasks = task_service.get_all_tasks()
    assert len(tasks) == 2

    # Mark complete
    task_service.toggle_task_completion(task1.id)
    assert task_service.get_task_by_id(task1.id).completed is True

    # Update
    task_service.update_task(task1.id, description="Milk, eggs, bread")
    assert task_service.get_task_by_id(task1.id).description == "Milk, eggs, bread"

    # Delete
    task_service.delete_task(task2.id)
    tasks = task_service.get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0].id == task1.id
