# Task Service Contract

**Feature**: 001-console-todo-app
**Module**: `src/services/task_service.py`
**Date**: 2026-01-06

## Overview

This document defines the contract for the Task Service, which provides all business logic operations for task management. The service acts as the boundary between the CLI interface and the in-memory data store.

## Service Interface

### Function: `add_task`

**Purpose**: Create a new task and add it to the task list

**Signature**:
```python
def add_task(title: str, description: str = "") -> Task
```

**Inputs**:
| Parameter | Type | Required | Constraints |
|-----------|------|----------|-------------|
| `title` | `str` | Yes | 1-200 characters, not empty after strip |
| `description` | `str` | No | 0-1000 characters |

**Outputs**:
| Type | Description |
|------|-------------|
| `Task` | The newly created task with auto-assigned ID |

**Side Effects**:
- Appends task to internal `_tasks` list
- Increments internal `_next_id` counter

**Errors**:
| Exception | Condition |
|-----------|-----------|
| `pydantic.ValidationError` | Title empty, title > 200 chars, or description > 1000 chars |

**Examples**:
```python
# Valid: Full task
task = add_task("Buy groceries", "Milk, eggs, bread")
assert task.id == 1
assert task.title == "Buy groceries"
assert task.description == "Milk, eggs, bread"
assert task.completed == False

# Valid: Title only
task = add_task("Call mom")
assert task.description == ""

# Invalid: Empty title
try:
    add_task("   ")
except ValidationError:
    pass  # Expected
```

**Spec Reference**: FR-001, FR-002, User Story 1

---

### Function: `get_all_tasks`

**Purpose**: Retrieve all tasks in the task list

**Signature**:
```python
def get_all_tasks() -> list[Task]
```

**Inputs**: None

**Outputs**:
| Type | Description |
|------|-------------|
| `list[Task]` | List of all tasks (empty list if no tasks) |

**Side Effects**: None (read-only)

**Errors**: None

**Examples**:
```python
# Empty list
tasks = get_all_tasks()
assert tasks == []

# With tasks
add_task("Task 1", "Description 1")
add_task("Task 2", "Description 2")
tasks = get_all_tasks()
assert len(tasks) == 2
```

**Spec Reference**: FR-003, User Story 1

---

### Function: `get_task_by_id`

**Purpose**: Retrieve a single task by its ID

**Signature**:
```python
def get_task_by_id(task_id: int) -> Task | None
```

**Inputs**:
| Parameter | Type | Required | Constraints |
|-----------|------|----------|-------------|
| `task_id` | `int` | Yes | Positive integer |

**Outputs**:
| Type | Description |
|------|-------------|
| `Task` | The task with matching ID |
| `None` | If no task found with that ID |

**Side Effects**: None (read-only)

**Errors**: None (returns None instead of raising exception)

**Examples**:
```python
task = add_task("Test task")
found = get_task_by_id(task.id)
assert found == task

not_found = get_task_by_id(999)
assert not_found is None
```

**Spec Reference**: Helper for FR-004, FR-005, FR-006, FR-007

---

### Function: `update_task`

**Purpose**: Update the title and/or description of an existing task

**Signature**:
```python
def update_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None
) -> Task
```

**Inputs**:
| Parameter | Type | Required | Constraints |
|-----------|------|----------|-------------|
| `task_id` | `int` | Yes | Must reference existing task |
| `title` | `str \| None` | No | 1-200 characters if provided |
| `description` | `str \| None` | No | 0-1000 characters if provided |

**Outputs**:
| Type | Description |
|------|-------------|
| `Task` | The updated task |

**Side Effects**:
- Modifies task in `_tasks` list in-place
- Only updates fields that are provided (partial update)

**Errors**:
| Exception | Condition |
|-----------|-----------|
| `TaskNotFoundError` | No task with given ID |
| `pydantic.ValidationError` | Title/description violates constraints |

**Examples**:
```python
task = add_task("Old title", "Old description")

# Update both
updated = update_task(task.id, title="New title", description="New description")
assert updated.title == "New title"
assert updated.description == "New description"

# Update title only
updated = update_task(task.id, title="Newer title")
assert updated.title == "Newer title"
assert updated.description == "New description"  # Unchanged

# Update description only
updated = update_task(task.id, description="Newer description")
assert updated.title == "Newer title"  # Unchanged
assert updated.description == "Newer description"

# Invalid ID
try:
    update_task(999, title="Test")
except TaskNotFoundError:
    pass  # Expected
```

**Spec Reference**: FR-006, User Story 3

---

### Function: `delete_task`

**Purpose**: Remove a task from the task list

**Signature**:
```python
def delete_task(task_id: int) -> None
```

**Inputs**:
| Parameter | Type | Required | Constraints |
|-----------|------|----------|-------------|
| `task_id` | `int` | Yes | Must reference existing task |

**Outputs**: None

**Side Effects**:
- Removes task from `_tasks` list
- Does NOT reuse the deleted task's ID

**Errors**:
| Exception | Condition |
|-----------|-----------|
| `TaskNotFoundError` | No task with given ID |

**Examples**:
```python
task = add_task("To delete")
delete_task(task.id)

tasks = get_all_tasks()
assert task not in tasks

# Invalid ID
try:
    delete_task(999)
except TaskNotFoundError:
    pass  # Expected
```

**Spec Reference**: FR-007, User Story 4

---

### Function: `toggle_task_completion`

**Purpose**: Toggle the completion status of a task (complete ↔ incomplete)

**Signature**:
```python
def toggle_task_completion(task_id: int) -> Task
```

**Inputs**:
| Parameter | Type | Required | Constraints |
|-----------|------|----------|-------------|
| `task_id` | `int` | Yes | Must reference existing task |

**Outputs**:
| Type | Description |
|------|-------------|
| `Task` | The updated task with toggled completion status |

**Side Effects**:
- Modifies `completed` field in `_tasks` list in-place

**Errors**:
| Exception | Condition |
|-----------|-----------|
| `TaskNotFoundError` | No task with given ID |

**Examples**:
```python
task = add_task("Task to complete")
assert task.completed == False

# Mark complete
updated = toggle_task_completion(task.id)
assert updated.completed == True

# Mark incomplete
updated = toggle_task_completion(task.id)
assert updated.completed == False

# Invalid ID
try:
    toggle_task_completion(999)
except TaskNotFoundError:
    pass  # Expected
```

**Spec Reference**: FR-004, FR-005, User Story 2

---

## Custom Exceptions

### `TaskNotFoundError`

**Purpose**: Indicates that an operation was attempted on a non-existent task ID

**Definition**:
```python
class TaskNotFoundError(Exception):
    """Raised when a task with the given ID cannot be found."""
    pass
```

**Usage**:
```python
def get_task_or_raise(task_id: int) -> Task:
    task = get_task_by_id(task_id)
    if task is None:
        raise TaskNotFoundError(f"Task with ID {task_id} not found")
    return task
```

---

## Service State

### Module-Level Variables

**Definition**:
```python
_tasks: list[Task] = []
_next_id: int = 1
```

**Visibility**: Private (module-level, not exposed)

**Lifecycle**:
- **Initialization**: Empty list, ID counter at 1
- **Runtime**: Modified by add/update/delete operations
- **Termination**: Lost when application exits (no persistence)

**Thread Safety**: Not required (single-threaded console application)

---

## Contract Guarantees

### Idempotency

**Non-idempotent operations**:
- `add_task`: Creates new task with new ID each call
- `delete_task`: Succeeds once, raises error on retry

**Idempotent operations**:
- `get_all_tasks`: Always returns current state
- `get_task_by_id`: Always returns same result for same ID (until modified)
- `toggle_task_completion`: Multiple calls toggle state back and forth (not truly idempotent)

### Data Consistency

**Guarantees**:
1. ID uniqueness: No two tasks ever have the same ID within a session
2. ID monotonicity: IDs always increase (never reused)
3. Referential integrity: Operations on invalid IDs fail with `TaskNotFoundError`
4. Validation enforcement: All tasks in `_tasks` list are valid per Pydantic model

---

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| `add_task` | O(1) | O(1) per task |
| `get_all_tasks` | O(n) | O(n) (returns copy) |
| `get_task_by_id` | O(n) | O(1) |
| `update_task` | O(n) | O(1) |
| `delete_task` | O(n) | O(1) |
| `toggle_task_completion` | O(n) | O(1) |

Where n = number of tasks. All operations meet spec performance requirements for n < 100.

---

## Testing Requirements

### Unit Test Coverage

**File**: `tests/unit/test_task_service.py`

**Required Test Cases**:
1. `add_task`: valid with description, valid without description, invalid empty title, invalid long title/description
2. `get_all_tasks`: empty list, with tasks
3. `get_task_by_id`: found, not found
4. `update_task`: update both fields, update title only, update description only, invalid ID, invalid constraints
5. `delete_task`: valid deletion, invalid ID, verify not in list after
6. `toggle_task_completion`: False → True, True → False, invalid ID

**Coverage Target**: 90%+ (per constitution)

---

## Future Extensions (Phase II+)

When transitioning to Phase II:

1. **Persistence Layer**:
   - Replace in-memory list with database repository
   - Service interface remains unchanged (same function signatures)
   - Add transaction support

2. **Multi-User Support**:
   - Add `user_id` parameter to operations
   - Filter tasks by user in `get_all_tasks`

3. **Async Support**:
   - Convert functions to `async def`
   - Add `await` for database operations

**Contract Stability**: Service interface designed to remain stable across phases. CLI code should not need changes when persistence is added.
