# Data Model: Phase I - Console Todo App

**Feature**: 001-console-todo-app
**Date**: 2026-01-06
**Phase**: 1 - Design & Contracts

## Overview

Phase I uses a simple in-memory data model with a single entity: **Task**. The data model is intentionally minimalist to establish the foundation for future phases while adhering to the Progressive Elaboration principle.

## Entities

### Task

Represents a single todo item in the user's task list.

**Attributes**:

| Field | Type | Required | Constraints | Default | Description |
|-------|------|----------|-------------|---------|-------------|
| `id` | `int` | Yes | Positive integer, unique, auto-assigned | N/A | Unique identifier for the task |
| `title` | `str` | Yes | 1-200 characters | N/A | Short description of the task |
| `description` | `str` | No | 0-1000 characters | `""` (empty string) | Detailed information about the task |
| `completed` | `bool` | Yes | True or False | `False` | Completion status of the task |

**Business Rules**:

1. **ID Assignment**: IDs are auto-generated sequentially starting from 1. Users cannot manually set IDs.
2. **Title Requirement**: Title is mandatory and must not be empty after stripping whitespace.
3. **Length Validation**:
   - Title: Minimum 1 character (after strip), maximum 200 characters
   - Description: Maximum 1000 characters (can be empty)
4. **Completion Default**: All new tasks start as incomplete (`completed=False`)
5. **Immutable ID**: Once assigned, a task's ID never changes (even if other tasks are deleted)

**State Transitions**:

```
[New Task]
    ↓
completed=False (default)
    ↓
    ↔ (toggle operation)
    ↓
completed=True
```

Tasks can toggle between `completed=False` and `completed=True` multiple times.

**Validation Rules**:

Implemented via Pydantic field validators:

```python
from pydantic import BaseModel, Field, field_validator

class Task(BaseModel):
    id: int = Field(gt=0, description="Unique task identifier")
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: str = Field(default="", max_length=1000, description="Task description")
    completed: bool = Field(default=False, description="Completion status")

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Title cannot be empty or whitespace only")
        return stripped

    @field_validator('description')
    @classmethod
    def strip_description(cls, v: str) -> str:
        return v.strip()
```

---

## Data Storage

### In-Memory Storage

**Implementation**: Module-level list in `task_service.py`

```python
# Global state (in-memory)
_tasks: list[Task] = []
_next_id: int = 1
```

**Rationale**:
- Simple and fast for Phase I requirements
- No persistence needed (per spec constraints)
- Easy to reset between sessions
- Sufficient for 100+ tasks without performance degradation

**Lifecycle**:
- **Initialization**: Empty list on application start
- **Runtime**: Tasks added to list, IDs auto-increment
- **Termination**: All data lost when application exits (user warned on startup)

---

## Relationships

**Phase I**: No relationships (single entity)

**Future Phases**:
- Phase II: Task → User (many-to-one) when multi-user support added
- Phase V: Task → Tags (many-to-many), Task → Category (many-to-one) if advanced features added

---

## Data Operations

All operations correspond to functional requirements:

| Operation | Method | Input | Output | Mutates State |
|-----------|--------|-------|--------|---------------|
| Create | `add_task(title, description)` | title: str, description: str | Task | Yes (appends to list) |
| Read All | `get_all_tasks()` | None | list[Task] | No |
| Read One | `get_task_by_id(task_id)` | task_id: int | Task or None | No |
| Update | `update_task(task_id, title?, description?)` | task_id: int, optional fields | Task | Yes (modifies in place) |
| Delete | `delete_task(task_id)` | task_id: int | None | Yes (removes from list) |
| Toggle Complete | `toggle_task_completion(task_id)` | task_id: int | Task | Yes (modifies in place) |

---

## Data Integrity

### ID Uniqueness

**Guarantee**: Sequential ID assignment ensures uniqueness within a session.

**Implementation**:
```python
def add_task(title: str, description: str = "") -> Task:
    global _next_id
    task = Task(id=_next_id, title=title, description=description)
    _tasks.append(task)
    _next_id += 1
    return task
```

**Edge Case**: If user deletes task ID 5, the next new task gets ID 6 (not 5). IDs are never reused within a session.

### Validation Enforcement

**Where**: Two layers
1. **CLI Layer** (`cli/menu.py`): Pre-validation for user-friendly errors
   - Check title not empty before calling service
   - Check ID is numeric
2. **Service Layer** (`services/task_service.py`): Pydantic validation
   - Enforce length constraints
   - Type checking
   - Business rule validation

**Error Handling**:
- CLI catches `ValidationError` from Pydantic and displays friendly message
- Service layer raises `TaskNotFoundError` for invalid IDs
- All errors propagate to CLI for user display (no silent failures)

---

## Data Access Patterns

### Sequential Scan (View All)

**Operation**: Display all tasks

**Pattern**: Iterate entire list
```python
def get_all_tasks() -> list[Task]:
    return _tasks.copy()  # Return copy to prevent external mutation
```

**Performance**: O(n) where n = number of tasks. Acceptable for n < 1000.

### Linear Search (Get by ID)

**Operation**: Find, update, delete, toggle task

**Pattern**: List comprehension or iteration
```python
def get_task_by_id(task_id: int) -> Task | None:
    return next((task for task in _tasks if task.id == task_id), None)
```

**Performance**: O(n) worst case. Acceptable for n < 100 (spec requirement).

**Future Optimization** (Phase II): Use dictionary `{id: Task}` for O(1) lookup when database added.

---

## Data Migration Plan

### Phase I → Phase II

When persistence is added in Phase II:

1. **Task entity evolution**:
   - Add `created_at: datetime` field
   - Add `updated_at: datetime` field
   - Add `user_id: int` field (foreign key to User)

2. **Storage migration**:
   - In-memory list → PostgreSQL table
   - Pydantic model → SQLModel (Pydantic + SQLAlchemy)
   - Add database migrations with Alembic

3. **Backward compatibility**:
   - Core fields (id, title, description, completed) unchanged
   - New fields nullable or with defaults for smooth transition

---

## Testing Considerations

### Unit Tests

**File**: `tests/unit/test_task_model.py`

**Test Cases**:
1. Valid task creation with all fields
2. Valid task creation with title only (description defaults to "")
3. Invalid: empty title → ValidationError
4. Invalid: title > 200 chars → ValidationError
5. Invalid: description > 1000 chars → ValidationError
6. Valid: title exactly 200 chars (boundary test)
7. Valid: description exactly 1000 chars (boundary test)
8. Default: completed=False on new task
9. State transition: toggle completed False → True → False

### Integration Tests

**File**: `tests/integration/test_full_workflow.py`

**Test Scenarios** (from spec acceptance criteria):
1. Add task with title and description → verify in list
2. Add task with title only → verify description is empty
3. View empty task list → verify "No tasks found" message
4. Mark task complete → verify status changed
5. Update task title → verify only title changed
6. Update task description → verify only description changed
7. Delete task → verify removed from list
8. Delete non-existent task → verify error message

---

## Summary

The Phase I data model is intentionally simple:
- **Single entity**: Task
- **Four fields**: id, title, description, completed
- **In-memory storage**: Python list
- **Type-safe**: Pydantic validation
- **Foundation for growth**: Designed for easy extension in Phase II (persistence, users, timestamps)

All design decisions align with the Progressive Elaboration principle: start simple, add complexity only when needed.
