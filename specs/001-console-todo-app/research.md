# Research: Phase I - Console Todo App

**Feature**: 001-console-todo-app
**Date**: 2026-01-06
**Phase**: 0 - Outline & Research

## Purpose

This document resolves all technical unknowns and establishes best practices for Phase I implementation. Since Phase I is intentionally simple (in-memory console app with Python standard library), most decisions are straightforward.

## Research Areas

### 1. Data Storage Strategy

**Decision**: Use Python list to store Task objects in memory

**Rationale**:
- Simplest data structure for sequential ID assignment
- Natural fit for "view all tasks" operation
- Easy to search by ID with list comprehension
- No persistence requirement in Phase I

**Alternatives Considered**:
- **Dictionary with ID keys**: More complex for sequential ID generation; no performance benefit at <100 tasks scale
- **Named tuples**: Less flexible than Pydantic models; no validation built-in
- **Dataclasses**: Viable but Pydantic provides better validation and type safety

**Implementation**:
```python
tasks: list[Task] = []  # Module-level in task_service.py
next_id: int = 1        # Auto-increment counter
```

---

### 2. Task Data Model

**Decision**: Use Pydantic BaseModel for Task entity

**Rationale**:
- Built-in validation (length constraints, required fields)
- Type safety with automatic type checking
- Serialization support for future phases (JSON in Phase II)
- Aligns with constitution requirement for typed data structures
- No external dependency (Pydantic is part of standard modern Python usage)

**Alternatives Considered**:
- **Plain dataclass**: No built-in validation; would need separate validation logic
- **Dict**: No type safety; error-prone; violates constitution type safety requirement
- **NamedTuple**: Immutable (problematic for updates); no validation

**Implementation**:
```python
from pydantic import BaseModel, Field, field_validator

class Task(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    completed: bool = False
```

---

### 3. Input Validation Strategy

**Decision**: Two-layer validation approach

**Rationale**:
- **Layer 1 - CLI input validation**: Catch format errors early (non-numeric IDs, empty strings)
- **Layer 2 - Pydantic model validation**: Enforce business rules (length constraints)
- Separation of concerns: CLI handles user interaction, models handle business rules
- Clear error messages at appropriate layer

**Alternatives Considered**:
- **Validation only in Pydantic**: User gets technical validation errors instead of friendly CLI messages
- **Validation only in CLI**: Duplicates logic; models lose self-validation capability
- **Third-party validation library (Cerberus, etc.)**: Unnecessary dependency for simple constraints

**Implementation**:
- CLI validates: non-empty input, numeric IDs, basic format
- Pydantic validates: length constraints, type correctness, business rules

---

### 4. CLI Architecture

**Decision**: Menu-driven loop with command dispatch pattern

**Rationale**:
- User-friendly for non-technical users
- Clear numbered options (1-6: operations, 7: exit)
- Single entry point with switch/dispatch to operation handlers
- Easy to test each operation independently

**Alternatives Considered**:
- **Argument-based CLI (argparse)**: More complex for interactive session; better for single commands
- **REPL-style commands**: Requires command parsing; less discoverable for users
- **Wizard-style sequential prompts**: Too rigid; user can't choose operation order

**Implementation**:
```python
while True:
    display_menu()
    choice = input("Select option: ")
    match choice:
        case "1": add_task()
        case "2": view_tasks()
        # ... etc
        case "7": break
```

---

### 5. Error Handling Best Practices

**Decision**: Custom exception types with user-friendly error messages

**Rationale**:
- Distinguish business errors (TaskNotFound) from technical errors (ValidationError)
- Catch and translate exceptions at CLI boundary
- User sees friendly messages, not stack traces
- Aligns with FR-011 requirement for clear error messages

**Alternatives Considered**:
- **Return codes/tuples**: Less Pythonic; harder to propagate errors through call stack
- **Generic exceptions**: Harder to handle specific error cases
- **No custom exceptions**: Would need to catch ValueError, KeyError, etc. separately

**Implementation**:
```python
class TaskNotFoundError(Exception): pass
class ValidationError(Exception): pass

# In CLI:
try:
    task_service.delete_task(task_id)
except TaskNotFoundError:
    print("Error: Task not found")
except ValidationError as e:
    print(f"Validation error: {e}")
```

---

### 6. Testing Strategy

**Decision**: Pytest with unit tests for services, integration tests for workflows

**Rationale**:
- Pytest is Python standard for testing
- Unit tests: Fast, isolated tests for task_service operations
- Integration tests: Full workflow tests (add → view → update → delete → mark complete)
- 90%+ coverage requirement from constitution
- No mocking needed (in-memory state is easy to set up and tear down)

**Alternatives Considered**:
- **unittest (stdlib)**: More verbose; pytest is more Pythonic and powerful
- **doctest**: Good for examples but insufficient for comprehensive testing
- **Only integration tests**: Slower; harder to isolate failures

**Test Structure**:
- `tests/unit/test_task_service.py`: Test each CRUD operation independently
- `tests/unit/test_validation.py`: Test validation rules
- `tests/integration/test_full_workflow.py`: Test complete user journeys from spec

---

### 7. Package Management

**Decision**: UV with pyproject.toml

**Rationale**:
- Constitution mandates UV for all phases
- pyproject.toml is modern Python standard (PEP 621)
- Minimal dependencies: pytest, pytest-cov for testing only

**Dependencies**:
```toml
[project]
name = "todo-console"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["pydantic>=2.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=4.0"]
```

---

### 8. Display Formatting

**Decision**: Simple text-based table format with status indicators

**Rationale**:
- Clear visual distinction between complete/incomplete tasks
- ASCII-art box drawing is overkill for Phase I
- Focus on functionality over aesthetics
- Meets FR-013 requirement for readable format

**Format**:
```
ID | Status | Title                | Description
---+--------+----------------------+-------------------
1  | [ ]    | Buy groceries        | Milk, eggs, bread
2  | [X]    | Call mom             |
```

**Alternatives Considered**:
- **Rich library (colored terminal)**: External dependency; nice-to-have not must-have
- **ASCII table libraries (tabulate)**: External dependency; easy to implement manually
- **JSON output**: Not user-friendly for interactive CLI

---

## Technology Stack Summary

**Language**: Python 3.13+
**Core Dependencies**:
- pydantic (data validation)

**Dev Dependencies**:
- pytest (testing framework)
- pytest-cov (coverage reporting)

**Standard Library Usage**:
- typing (type hints)
- sys (exit handling)
- No file I/O, no networking, no external APIs

---

## Unknowns Resolution Status

All technical unknowns from plan.md Technical Context have been resolved:

✅ Language/Version: Python 3.13+ (confirmed)
✅ Primary Dependencies: Pydantic only (confirmed)
✅ Storage: Python list (confirmed)
✅ Testing: pytest (confirmed)
✅ Target Platform: Local machine with Python 3.13+ (confirmed)
✅ Project Type: Single console app (confirmed)
✅ Performance Goals: Defined in spec success criteria (confirmed)
✅ Constraints: In-memory, no external libs except dev (confirmed)
✅ Scale/Scope: 5 operations, 100+ tasks capability (confirmed)

**Status**: ✅ All research complete. Ready for Phase 1 design.
