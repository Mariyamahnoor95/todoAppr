"""Display utilities for CLI output."""

from src.models.task import Task


def display_task_list(tasks: list[Task]) -> None:
    """Display a list of tasks in table format.

    Args:
        tasks: List of tasks to display
    """
    if not tasks:
        print("\nNo tasks found.")
        return

    print("\n" + "=" * 80)
    print("                              Task List")
    print("=" * 80)
    print(f"{'ID':<4} | {'Status':<6} | {'Title':<30} | {'Description':<30}")
    print("-" * 4 + "+" + "-" * 8 + "+" + "-" * 32 + "+" + "-" * 30)

    for task in tasks:
        status = "[X]" if task.completed else "[ ]"
        # Truncate title and description if too long
        title = task.title[:27] + "..." if len(task.title) > 30 else task.title
        description = task.description[:27] + "..." if len(task.description) > 30 else task.description

        print(f"{task.id:<4} | {status:<6} | {title:<30} | {description:<30}")

    # Summary
    completed_count = sum(1 for task in tasks if task.completed)
    incomplete_count = len(tasks) - completed_count
    print("\n" + "=" * 80)
    print(f"Total: {len(tasks)} tasks ({completed_count} completed, {incomplete_count} incomplete)")
    print("=" * 80 + "\n")


def display_task(task: Task) -> None:
    """Display a single task with full details.

    Args:
        task: The task to display
    """
    status = "Complete" if task.completed else "Incomplete"
    print(f"\n{'=' * 40}")
    print(f"ID: {task.id}")
    print(f"Title: {task.title}")
    print(f"Description: {task.description}")
    print(f"Status: {status}")
    print(f"{'=' * 40}\n")
