# Data Model: Phase II Web Application

**Feature**: 002-web-todo-app
**Date**: 2026-01-12
**Status**: Complete

## Overview

This document defines the data entities, relationships, and validation rules for Phase II. All models are implemented using SQLModel (Pydantic + SQLAlchemy) for type safety and database ORM.

---

## Entity Relationship Diagram

```
┌─────────────────────┐
│       User          │
├─────────────────────┤
│ id: int (PK)        │
│ email: str (unique) │
│ password_hash: str  │
│ created_at: datetime│
└──────────┬──────────┘
           │
           │ 1:N (one user has many tasks)
           │
           ▼
┌─────────────────────┐
│       Task          │
├─────────────────────┤
│ id: int (PK)        │
│ user_id: int (FK)   │ ──→ references User.id
│ title: str          │
│ description: str    │
│ completed: bool     │
│ created_at: datetime│
│ updated_at: datetime│
└─────────────────────┘
```

---

## Entity Definitions

### Entity 1: User

**Purpose**: Represents an authenticated user with ownership of tasks.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `int` | Primary Key, Auto-increment | Unique user identifier |
| `email` | `str` | Unique, Not Null, Max 255 chars | User's email address (used for login) |
| `password_hash` | `str` | Not Null, Max 255 chars | Bcrypt hashed password (never store plaintext) |
| `created_at` | `datetime` | Not Null, Default: now() | Account creation timestamp (UTC) |

**Validation Rules**:
- **Email format**: Must match email regex pattern (handled by Pydantic `EmailStr`)
- **Email uniqueness**: Must be unique across all users (database constraint + API validation)
- **Password**: Minimum 8 characters before hashing (validated at API layer, not in model)
- **Password hash**: Bcrypt with cost factor 12

**Relationships**:
- **1:N with Task**: One user owns many tasks (`tasks` relationship)

**Indexes**:
- Primary key index on `id` (automatic)
- Unique index on `email` (for fast lookup during login)

**SQLModel Example**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List, Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=255, index=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    tasks: List["Task"] = Relationship(back_populates="user", cascade_delete=True)
```

**State Transitions**:
- Created → Active (immediate upon registration)
- Active → Deleted (soft delete or hard delete - Phase II uses hard delete)

---

### Entity 2: Task

**Purpose**: Represents a todo item owned by a user.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `int` | Primary Key, Auto-increment | Unique task identifier |
| `user_id` | `int` | Foreign Key → User.id, Not Null, Indexed | Owner of the task |
| `title` | `str` | Not Null, Min 1, Max 200 chars | Task title/summary |
| `description` | `str` | Default: "", Max 1000 chars | Optional detailed description |
| `completed` | `bool` | Not Null, Default: False | Completion status |
| `created_at` | `datetime` | Not Null, Default: now() | Task creation timestamp (UTC) |
| `updated_at` | `datetime` | Not Null, Default: now(), Auto-update | Last modification timestamp (UTC) |

**Validation Rules** (from spec FR-006, FR-007):
- **Title**:
  - Required (not null, not empty string)
  - Minimum 1 character (after stripping whitespace)
  - Maximum 200 characters
  - Must contain at least one non-whitespace character
- **Description**:
  - Optional (can be empty string)
  - Maximum 1000 characters
  - Empty string is valid default
- **Completed**:
  - Boolean only (True/False)
  - Default: False
- **User ID**:
  - Must reference existing user
  - Foreign key constraint enforced at database level

**Relationships**:
- **N:1 with User**: Many tasks belong to one user (`user` relationship)

**Indexes**:
- Primary key index on `id` (automatic)
- Foreign key index on `user_id` (for fast filtering by user)
- Composite index on `(user_id, created_at DESC)` (for efficient task list queries)

**SQLModel Example**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: Optional[User] = Relationship(back_populates="tasks")
```

**State Transitions**:
```
Created (completed=False)
    ↓
    ↓ [User marks complete]
    ↓
Completed (completed=True)
    ↓
    ↓ [User marks incomplete]
    ↓
Created (completed=False)  ← cycle repeats
    ↓
    ↓ [User deletes]
    ↓
Deleted (hard delete, removed from DB)
```

**State Validation**:
- No invalid states (completed can be toggled freely)
- Deletion is permanent (no soft delete in Phase II)

---

## Database Schema (PostgreSQL)

### Table: users

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

### Table: tasks

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000) NOT NULL DEFAULT '',
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
```

**Migration Strategy**:
- Alembic for schema versioning
- Auto-generate migrations from SQLModel changes
- Review migrations before applying
- Rollback plan: Alembic downgrade commands

---

## Data Integrity Rules

### Foreign Key Constraints

1. **tasks.user_id → users.id**:
   - Enforced at database level
   - `ON DELETE CASCADE`: When user is deleted, all their tasks are deleted
   - `ON UPDATE CASCADE`: If user ID changes (unlikely), update task references

### Unique Constraints

1. **users.email**: Must be unique across all users
   - Database constraint prevents duplicates
   - API layer provides user-friendly error message

### Check Constraints (optional, can be added later)

1. **tasks.title length**: `LENGTH(title) >= 1 AND LENGTH(title) <= 200`
2. **tasks.description length**: `LENGTH(description) <= 1000`

---

## Pagination Strategy

For task lists exceeding 50 items (FR-019):

**Query Pattern**:
```sql
SELECT * FROM tasks
WHERE user_id = :user_id
ORDER BY created_at DESC
LIMIT :limit OFFSET :offset;
```

**Parameters**:
- `limit`: Default 50, max 100
- `offset`: Calculated as `(page - 1) * limit`

**Response Metadata**:
```json
{
  "items": [...],
  "page": 1,
  "limit": 50,
  "total": 237,
  "pages": 5
}
```

---

## Data Access Patterns

### Query 1: Get all tasks for a user (paginated)

```python
# SQLModel query
tasks = session.exec(
    select(Task)
    .where(Task.user_id == user_id)
    .order_by(Task.created_at.desc())
    .limit(limit)
    .offset(offset)
).all()
```

**Performance**: Indexed on `(user_id, created_at DESC)` - O(log n) lookup

### Query 2: Get single task by ID (with user verification)

```python
# SQLModel query
task = session.exec(
    select(Task)
    .where(Task.id == task_id, Task.user_id == user_id)
).first()
```

**Performance**: Indexed on `id` (primary key) - O(1) lookup

### Query 3: Create new task

```python
# SQLModel insert
task = Task(
    user_id=user_id,
    title=title,
    description=description,
    completed=False
)
session.add(task)
session.commit()
session.refresh(task)
```

**Performance**: O(1) insert with auto-increment ID

### Query 4: Update task

```python
# SQLModel update
task.title = new_title
task.description = new_description
task.updated_at = datetime.utcnow()
session.add(task)
session.commit()
```

**Performance**: O(1) update with primary key lookup

### Query 5: Toggle completion

```python
# SQLModel update
task.completed = not task.completed
task.updated_at = datetime.utcnow()
session.add(task)
session.commit()
```

**Performance**: O(1) update

### Query 6: Delete task

```python
# SQLModel delete
session.delete(task)
session.commit()
```

**Performance**: O(1) delete with cascade

---

## Performance Considerations

### Expected Data Volumes

- **Users**: 100-10,000 (Phase II scope)
- **Tasks per user**: 1-10,000 (typical: 10-100)
- **Total tasks**: 1,000-100,000

### Index Strategy

1. **Primary keys** (automatic): Fast lookups by ID
2. **users.email** (unique index): Fast login lookups
3. **tasks.user_id** (foreign key index): Fast filtering by user
4. **tasks(user_id, created_at DESC)** (composite index): Fast paginated queries

### Query Optimization

- Use `select()` instead of `session.query()` for async support
- Eager load relationships only when needed (avoid N+1 queries)
- Use pagination for large result sets
- Add `EXPLAIN ANALYZE` for slow queries during testing

---

## Security Considerations

### Password Storage

- **Never store plaintext passwords**
- Use bcrypt with cost factor 12 (balance security and performance)
- Example: `password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))`

### User Isolation

- **Always filter by user_id** in task queries
- Enforce at service layer (not just UI)
- Example: `WHERE user_id = :current_user_id`

### SQL Injection Prevention

- Use SQLModel parameterized queries (automatic)
- Never concatenate user input into SQL strings

### Input Validation

- Validate at API layer (Pydantic models)
- Validate at database layer (constraints)
- Sanitize user input (escape HTML entities if rendered)

---

## Migration Plan from Phase I

### Data Migration Strategy

**Phase I → Phase II**:
- Phase I has no persistent data (in-memory only)
- No data migration required
- Fresh database start

**If Phase I data needed** (optional):
1. Export Phase I in-memory tasks to JSON
2. Import JSON into Phase II database
3. Associate tasks with default user account
4. Run data validation script

---

## Future Extensions (Phase III+)

### Potential Schema Additions

- **Priorities**: `priority` field (enum: low, medium, high)
- **Tags**: Many-to-many relationship with `tags` table
- **Categories**: Foreign key to `categories` table
- **Due dates**: `due_date` timestamp field
- **Recurring tasks**: `recurrence_rule` JSON field
- **Attachments**: Foreign key to `attachments` table

### Indexing for Search (Phase V)

- Full-text search index on `title` and `description`
- PostgreSQL `tsvector` column with GIN index
- Or external search service (Elasticsearch, Meilisearch)

---

## Validation Summary

| Entity | Field | Validation | Enforced At |
|--------|-------|------------|-------------|
| User | email | Unique, email format | DB + API |
| User | password | Min 8 chars | API only |
| User | password_hash | Bcrypt hash | API only |
| Task | title | 1-200 chars, not empty | DB + API |
| Task | description | 0-1000 chars | DB + API |
| Task | completed | Boolean | DB + API |
| Task | user_id | Foreign key exists | DB only |

---

## Constitution Alignment

- [x] SQLModel for all models (Database Standards)
- [x] Type hints on all fields (Python Standards, Pillar 5)
- [x] Pydantic validation (Python Standards)
- [x] Foreign key constraints (Database Standards)
- [x] Timestamps on all tables (Database Standards)
- [x] Indexed on frequently queried columns (Database Standards)
- [x] Password hashing with bcrypt (Security Standards)
- [x] User isolation enforced (Security Standards)

**Status**: ✅ All database standards satisfied
