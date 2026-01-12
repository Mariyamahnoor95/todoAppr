# CLI Interface Contract

**Feature**: 001-console-todo-app
**Module**: `src/cli/menu.py`
**Date**: 2026-01-06

## Overview

This document defines the user-facing CLI interface contract, including menu structure, user inputs, outputs, and interaction flows.

## Menu Interface

### Main Menu

**Display Format**:
```
========================================
         Todo List Application
========================================
Note: Tasks are stored in memory and will be lost when the application exits.

1. Add Task
2. View All Tasks
3. Update Task
4. Delete Task
5. Mark Task Complete/Incomplete
6. Exit

Select option (1-6):
```

**User Input**: Single character (1-6)

**Error Handling**: Invalid input (non-numeric, out of range) displays error and re-prompts

---

## Operation 1: Add Task

### User Flow

**Prompts**:
```
Enter task title (1-200 characters): [user input]
Enter task description (optional, max 1000 characters): [user input]
```

**Success Output**:
```
✓ Task added successfully!
  ID: 1
  Title: Buy groceries
  Description: Milk, eggs, bread
  Status: Incomplete
```

**Error Outputs**:

| Error Condition | User Message |
|-----------------|--------------|
| Empty title | `Error: Title cannot be empty` |
| Title > 200 chars | `Error: Title must be 200 characters or less` |
| Description > 1000 chars | `Error: Description must be 1000 characters or less` |

**Spec Reference**: FR-001, FR-009, FR-011, User Story 1

---

## Operation 2: View All Tasks

### User Flow

**No Prompts**: Operation executes immediately

**Success Output (with tasks)**:
```
========================================
              Task List
========================================
ID | Status | Title                | Description
---+--------+----------------------+-------------------
1  | [ ]    | Buy groceries        | Milk, eggs, bread
2  | [X]    | Call mom             |
3  | [ ]    | Finish homework      | Math chapter 5

Total: 3 tasks (1 completed, 2 incomplete)
```

**Success Output (empty list)**:
```
No tasks found.
```

**Status Indicators**:
- `[ ]` = Incomplete
- `[X]` = Complete

**Column Widths**:
- ID: Auto-fit
- Status: 6 chars
- Title: Truncate at 20 chars with "..." if longer (full title in detailed view)
- Description: Truncate at 30 chars with "..." if longer

**Spec Reference**: FR-003, FR-013, User Story 1

---

## Operation 3: Update Task

### User Flow

**Prompts**:
```
Enter task ID to update: [user input]
Enter new title (leave empty to keep current): [user input]
Enter new description (leave empty to keep current): [user input]
```

**Success Output**:
```
✓ Task updated successfully!
  ID: 1
  Title: Buy groceries (updated)
  Description: Milk, eggs, bread, butter
  Status: Incomplete
```

**Error Outputs**:

| Error Condition | User Message |
|-----------------|--------------|
| Non-numeric ID | `Error: Invalid task ID format. Please enter a number.` |
| Task not found | `Error: Task not found` |
| Both inputs empty | `Error: At least one field must be updated` |
| Title > 200 chars | `Error: Title must be 200 characters or less` |
| Description > 1000 chars | `Error: Description must be 1000 characters or less` |

**Spec Reference**: FR-006, FR-011, User Story 3

---

## Operation 4: Delete Task

### User Flow

**Prompts**:
```
Enter task ID to delete: [user input]
Are you sure you want to delete this task? (y/n): [user input]
```

**Success Output**:
```
✓ Task deleted successfully!
```

**Cancellation Output**:
```
Task deletion cancelled.
```

**Error Outputs**:

| Error Condition | User Message |
|-----------------|--------------|
| Non-numeric ID | `Error: Invalid task ID format. Please enter a number.` |
| Task not found | `Error: Task not found` |

**Spec Reference**: FR-007, FR-011, User Story 4

---

## Operation 5: Mark Complete/Incomplete

### User Flow

**Prompts**:
```
Enter task ID to toggle completion: [user input]
```

**Success Output (marked complete)**:
```
✓ Task marked as complete!
  ID: 1
  Title: Buy groceries
  Status: Complete
```

**Success Output (marked incomplete)**:
```
✓ Task marked as incomplete!
  ID: 1
  Title: Buy groceries
  Status: Incomplete
```

**Error Outputs**:

| Error Condition | User Message |
|-----------------|--------------|
| Non-numeric ID | `Error: Invalid task ID format. Please enter a number.` |
| Task not found | `Error: Task not found` |

**Spec Reference**: FR-004, FR-005, FR-011, User Story 2

---

## Operation 6: Exit

### User Flow

**No Prompts**: Exits immediately

**Output**:
```
Goodbye! All tasks will be lost.
```

**Behavior**: Application terminates with exit code 0

---

## Input Validation Contract

### CLI-Level Validation (Pre-Service)

**Purpose**: Provide user-friendly error messages before calling service layer

**Validations**:

| Input Type | Validation | Error Message |
|------------|------------|---------------|
| Task ID | Must be numeric | `Error: Invalid task ID format. Please enter a number.` |
| Task ID | Must be positive | `Error: Task ID must be a positive number.` |
| Title (add) | Must not be empty (after strip) | `Error: Title cannot be empty` |
| Title (update) | If provided, must not be empty | `Error: Title cannot be empty` |
| Menu choice | Must be 1-6 | `Error: Invalid option. Please select 1-6.` |
| Confirmation | Must be 'y' or 'n' | `Error: Please enter 'y' for yes or 'n' for no.` |

### Service-Level Validation (Pydantic)

**Purpose**: Enforce business rules and constraints

**Validations**:
- Title length: 1-200 characters
- Description length: 0-1000 characters
- Type correctness (handled by Pydantic)

**Error Translation**: CLI catches `pydantic.ValidationError` and displays friendly message

---

## Display Formatting Contract

### Task Display

**Function**: `display_task(task: Task) -> None`

**Format**:
```
ID: 1
Title: Buy groceries
Description: Milk, eggs, bread
Status: Incomplete
```

**Status Values**:
- `Incomplete` when `task.completed == False`
- `Complete` when `task.completed == True`

---

### Task List Display

**Function**: `display_task_list(tasks: list[Task]) -> None`

**Format**: See "Operation 2: View All Tasks" above

**Empty List Behavior**: Display "No tasks found."

---

## Error Handling Contract

### Exception Handling

**Pattern**:
```python
try:
    # Call service operation
    result = task_service.some_operation()
except TaskNotFoundError:
    print("Error: Task not found")
except ValidationError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

**User-Facing Errors**:
- All error messages start with "Error: "
- No stack traces displayed to user
- Technical errors logged (future: to file or stderr)

---

## Navigation Flow

```
[Start Application]
    ↓
[Display Startup Warning]
    ↓
[Display Main Menu] ←──────┐
    ↓                       │
[User Selects Option]       │
    ↓                       │
[Execute Operation]         │
    ↓                       │
[Display Result]            │
    ↓                       │
[Return to Main Menu] ──────┘
    ↑
    │ (except Exit)
    ↓
[Exit Application]
```

---

## Success Criteria Mapping

**From Spec Success Criteria**:

| SC ID | Requirement | CLI Contract Support |
|-------|-------------|---------------------|
| SC-001 | Add task in <10 seconds | Simple prompts, immediate feedback |
| SC-002 | View list in <2 seconds | No user input required for view |
| SC-003 | Mark complete in <5 seconds | Single ID prompt, immediate toggle |
| SC-004 | Update task in <15 seconds | Two prompts (ID, fields), immediate feedback |
| SC-005 | Delete task in <5 seconds | ID prompt + confirmation, immediate feedback |
| SC-006 | 100% invalid inputs show errors | All validation cases covered with clear messages |
| SC-007 | Full workflow in <45 seconds | Efficient menu navigation, minimal prompts |

---

## Testing Requirements

### Integration Test Coverage

**File**: `tests/integration/test_cli_interactions.py`

**Required Test Cases**:
1. Main menu displays correctly
2. Each menu option (1-6) navigates correctly
3. Invalid menu input displays error and re-prompts
4. Add task: valid input, empty title, long title, long description
5. View tasks: empty list, with tasks
6. Update task: both fields, title only, description only, invalid ID
7. Delete task: valid deletion, cancellation, invalid ID
8. Toggle completion: incomplete → complete, complete → incomplete, invalid ID
9. Exit: application terminates cleanly

**Testing Strategy**:
- Mock `input()` function for automated testing
- Capture `print()` output for assertion
- Test error paths and edge cases

---

## Future Extensions (Phase II+)

### Phase II Additions:
- Login prompt before main menu
- "Logout" option in main menu
- Task filtering by completion status
- Pagination for large task lists

**Contract Stability**: Menu structure designed to accommodate new options without breaking existing flows.
