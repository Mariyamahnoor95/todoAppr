"""CLI menu and user interaction."""

from pydantic import ValidationError
from src.services import task_service
from src.services.task_service import TaskNotFoundError
from src.cli.display import display_task_list, display_task


# Error message constants
ERROR_TASK_NOT_FOUND = "Error: Task not found"
ERROR_INVALID_ID = "Error: Invalid task ID format. Please enter a number."
ERROR_TITLE_REQUIRED = "Error: Title cannot be empty"
ERROR_OPTION_INVALID = "Error: Invalid option. Please select 1-6."
ERROR_CONFIRMATION_INVALID = "Error: Please enter 'y' for yes or 'n' for no."


def validate_numeric_id(id_str: str) -> int | None:
    """Validate that input is a positive numeric ID.

    Args:
        id_str: String input from user

    Returns:
        Integer ID if valid, None otherwise
    """
    try:
        task_id = int(id_str)
        if task_id <= 0:
            print("Error: Task ID must be a positive number.")
            return None
        return task_id
    except ValueError:
        print(ERROR_INVALID_ID)
        return None


def validate_non_empty_string(text: str, field_name: str) -> str | None:
    """Validate that input is not empty after stripping whitespace.

    Args:
        text: String input from user
        field_name: Name of the field for error message

    Returns:
        Stripped string if valid, None otherwise
    """
    stripped = text.strip()
    if not stripped:
        print(f"Error: {field_name} cannot be empty")
        return None
    return stripped


def add_task_menu() -> None:
    """Handle adding a new task via CLI menu."""
    print("\n--- Add New Task ---")

    # Prompt for title
    title_input = input("Enter task title (1-200 characters): ").strip()
    if not title_input:
        print(ERROR_TITLE_REQUIRED)
        return

    # Prompt for description
    description_input = input("Enter task description (optional, max 1000 characters): ").strip()

    try:
        task = task_service.add_task(title_input, description_input)
        print("\n✓ Task added successfully!")
        display_task(task)
    except ValidationError as e:
        # Extract user-friendly error message
        errors = e.errors()
        for error in errors:
            field = error['loc'][0] if error['loc'] else 'field'
            msg = error['msg']
            if 'at least 1 characters' in msg or 'at most 200 characters' in msg:
                print(f"Error: Title must be between 1 and 200 characters")
            elif 'at most 1000 characters' in msg:
                print(f"Error: Description must be 1000 characters or less")
            elif 'empty' in msg.lower():
                print(ERROR_TITLE_REQUIRED)
            else:
                print(f"Validation error: {msg}")


def view_tasks_menu() -> None:
    """Handle viewing all tasks via CLI menu."""
    tasks = task_service.get_all_tasks()
    display_task_list(tasks)


def update_task_menu() -> None:
    """Handle updating a task via CLI menu."""
    print("\n--- Update Task ---")

    # Prompt for task ID
    id_input = input("Enter task ID to update: ").strip()
    task_id = validate_numeric_id(id_input)
    if task_id is None:
        return

    # Prompt for new title
    title_input = input("Enter new title (leave empty to keep current): ").strip()
    new_title = title_input if title_input else None

    # Prompt for new description
    description_input = input("Enter new description (leave empty to keep current): ").strip()
    new_description = description_input if description_input else None

    # Check if at least one field is being updated
    if new_title is None and new_description is None:
        print("Error: At least one field must be updated")
        return

    try:
        task = task_service.update_task(task_id, title=new_title, description=new_description)
        print("\n✓ Task updated successfully!")
        display_task(task)
    except TaskNotFoundError:
        print(ERROR_TASK_NOT_FOUND)
    except ValidationError as e:
        errors = e.errors()
        for error in errors:
            msg = error['msg']
            if 'at least 1 characters' in msg or 'at most 200 characters' in msg:
                print(f"Error: Title must be between 1 and 200 characters")
            elif 'at most 1000 characters' in msg:
                print(f"Error: Description must be 1000 characters or less")
            else:
                print(f"Validation error: {msg}")


def delete_task_menu() -> None:
    """Handle deleting a task via CLI menu."""
    print("\n--- Delete Task ---")

    # Prompt for task ID
    id_input = input("Enter task ID to delete: ").strip()
    task_id = validate_numeric_id(id_input)
    if task_id is None:
        return

    # Confirm deletion
    confirm = input("Are you sure you want to delete this task? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        if confirm in ['n', 'no']:
            print("Task deletion cancelled.")
        else:
            print(ERROR_CONFIRMATION_INVALID)
        return

    try:
        task_service.delete_task(task_id)
        print("\n✓ Task deleted successfully!")
    except TaskNotFoundError:
        print(ERROR_TASK_NOT_FOUND)


def toggle_completion_menu() -> None:
    """Handle toggling task completion via CLI menu."""
    print("\n--- Mark Task Complete/Incomplete ---")

    # Prompt for task ID
    id_input = input("Enter task ID to toggle completion: ").strip()
    task_id = validate_numeric_id(id_input)
    if task_id is None:
        return

    try:
        task = task_service.toggle_task_completion(task_id)
        if task.completed:
            print("\n✓ Task marked as complete!")
        else:
            print("\n✓ Task marked as incomplete!")
        display_task(task)
    except TaskNotFoundError:
        print(ERROR_TASK_NOT_FOUND)


def display_main_menu() -> None:
    """Display the main menu options."""
    print("\n" + "=" * 40)
    print("         Todo List Application")
    print("=" * 40)
    print("1. Add Task")
    print("2. View All Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Task Complete/Incomplete")
    print("6. Exit")
    print("=" * 40)
