"""Main entry point for the console todo application."""

from src.cli.menu import (
    display_main_menu,
    add_task_menu,
    view_tasks_menu,
    update_task_menu,
    delete_task_menu,
    toggle_completion_menu,
    ERROR_OPTION_INVALID
)


def main() -> None:
    """Run the main application loop."""
    # Display startup warning
    print("\n" + "=" * 80)
    print("Note: Tasks are stored in memory and will be lost when the application exits.")
    print("=" * 80)

    while True:
        display_main_menu()
        choice = input("\nSelect option (1-6): ").strip()

        if choice == "1":
            add_task_menu()
        elif choice == "2":
            view_tasks_menu()
        elif choice == "3":
            update_task_menu()
        elif choice == "4":
            delete_task_menu()
        elif choice == "5":
            toggle_completion_menu()
        elif choice == "6":
            print("\nGoodbye! All tasks will be lost.")
            break
        else:
            print(ERROR_OPTION_INVALID)


if __name__ == "__main__":
    main()
