# Data Model: AI Chatbot for Todo Management

**Feature**: 003-ai-chatbot
**Date**: 2026-02-05
**Spec**: [spec.md](./spec.md)

## Entity Overview

Phase III introduces two new entities to support conversation persistence:

```
┌─────────────────────────────────────────────────────────────────┐
│                         PHASE III DATA MODEL                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐         ┌──────────────────┐                 │
│   │    User      │         │   Conversation   │                 │
│   │  (Better     │◄────────│                  │                 │
│   │   Auth)      │  user_id│  - id            │                 │
│   └──────────────┘         │  - user_id       │                 │
│          │                 │  - created_at    │                 │
│          │                 │  - updated_at    │                 │
│          │                 └────────┬─────────┘                 │
│          │                          │                           │
│          │                          │ 1:N                       │
│          │                          │                           │
│          │                 ┌────────▼─────────┐                 │
│          │                 │     Message      │                 │
│          │                 │                  │                 │
│          │                 │  - id            │                 │
│          │                 │  - conversation_ │                 │
│          │                 │    id            │                 │
│          │                 │  - role          │                 │
│          │                 │  - content       │                 │
│          │                 │  - created_at    │                 │
│          │                 └──────────────────┘                 │
│          │                                                      │
│          │ user_id                                              │
│          │                                                      │
│   ┌──────▼───────┐                                              │
│   │    Task      │  (Existing from Phase II)                    │
│   │              │                                              │
│   │  - id        │                                              │
│   │  - user_id   │                                              │
│   │  - title     │                                              │
│   │  - desc      │                                              │
│   │  - completed │                                              │
│   │  - created_at│                                              │
│   │  - updated_at│                                              │
│   └──────────────┘                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Entities

### Conversation (New)

Represents a chat session between a user and the AI assistant.

**Table**: `conversations`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique conversation identifier |
| `user_id` | VARCHAR(255) | NOT NULL, INDEX | Better Auth user ID (foreign reference) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | When conversation started |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | When conversation last updated |

**Indexes**:
- `idx_conversations_user_id` on `(user_id)`
- `idx_conversations_user_updated` on `(user_id, updated_at DESC)` - for listing recent conversations

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Message (New)

Represents a single message in a conversation (user or assistant).

**Table**: `messages`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique message identifier |
| `conversation_id` | UUID | NOT NULL, FOREIGN KEY, INDEX | Parent conversation |
| `role` | VARCHAR(20) | NOT NULL, CHECK (role IN ('user', 'assistant')) | Message sender |
| `content` | TEXT | NOT NULL | Message content |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | When message was sent |

**Indexes**:
- `idx_messages_conversation_id` on `(conversation_id)`
- `idx_messages_conversation_created` on `(conversation_id, created_at DESC)` - for loading history

**Foreign Keys**:
- `conversation_id` → `conversations(id)` ON DELETE CASCADE

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False, index=True)
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Task (Existing - No Changes)

Existing from Phase II. No schema changes required.

**Table**: `tasks`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique task identifier |
| `user_id` | VARCHAR(255) | NOT NULL, INDEX | Better Auth user ID |
| `title` | VARCHAR(200) | NOT NULL | Task title (1-200 chars) |
| `description` | VARCHAR(1000) | NULL | Task description (0-1000 chars) |
| `completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| `created_at` | TIMESTAMP | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

## Relationships

### User → Conversation (1:N)
- One user can have many conversations
- Each conversation belongs to exactly one user
- User isolation: queries filter by `user_id`

### Conversation → Message (1:N)
- One conversation can have many messages
- Each message belongs to exactly one conversation
- ON DELETE CASCADE: Deleting conversation removes all messages

### User → Task (1:N) - Existing
- No changes from Phase II
- Tasks accessed via MCP tools, not directly in chat

## Validation Rules

### Conversation
- `user_id`: Required, non-empty string
- `created_at`: Auto-generated, immutable
- `updated_at`: Auto-updated on any modification

### Message
- `conversation_id`: Required, must exist in conversations table
- `role`: Required, must be 'user' or 'assistant'
- `content`: Required, non-empty, max 10000 characters
- `created_at`: Auto-generated, immutable

### Task (Existing)
- `title`: Required, 1-200 characters
- `description`: Optional, 0-1000 characters
- `user_id`: Required, validated against JWT

## State Transitions

### Conversation States

```
┌─────────────────────────────────────────────────────────────┐
│                    CONVERSATION LIFECYCLE                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   [NEW REQUEST]                                             │
│        │                                                    │
│        ▼                                                    │
│   ┌─────────────┐    no conversation_id                     │
│   │   CREATE    │◄────────────────────────                  │
│   │ CONVERSATION│                                           │
│   └──────┬──────┘                                           │
│          │                                                  │
│          │         conversation_id provided                 │
│          ▼                  │                               │
│   ┌──────────────┐         │                                │
│   │    ACTIVE    │◄────────┘                                │
│   │ CONVERSATION │                                          │
│   └──────┬───────┘                                          │
│          │                                                  │
│          │ add message, update timestamp                    │
│          ▼                                                  │
│   ┌──────────────┐                                          │
│   │   UPDATED    │ ──► (ready for next message)             │
│   │ CONVERSATION │                                          │
│   └──────────────┘                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Message Creation Flow

```
User Message → Store in DB → Load Context → Run Agent →
              Assistant Response → Store in DB → Return Response
```

## Migration Script

```sql
-- Phase III Migration: Add Conversation and Message tables
-- File: migrations/003_add_chat_tables.sql

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for conversations
CREATE INDEX IF NOT EXISTS idx_conversations_user_id
    ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_updated
    ON conversations(user_id, updated_at DESC);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for messages
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
    ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
    ON messages(conversation_id, created_at DESC);

-- Add trigger to update updated_at on conversations
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET updated_at = NOW()
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_timestamp();
```

## Query Patterns

### Get User's Recent Conversations
```sql
SELECT id, created_at, updated_at
FROM conversations
WHERE user_id = :user_id
ORDER BY updated_at DESC
LIMIT 10;
```

### Get Conversation History (for AI context)
```sql
SELECT role, content, created_at
FROM messages
WHERE conversation_id = :conversation_id
ORDER BY created_at DESC
LIMIT 20;
```

### Create New Conversation with First Message
```sql
-- Transaction
BEGIN;

INSERT INTO conversations (id, user_id)
VALUES (:conversation_id, :user_id)
RETURNING id;

INSERT INTO messages (conversation_id, role, content)
VALUES (:conversation_id, 'user', :content);

COMMIT;
```

### Verify User Owns Conversation
```sql
SELECT id FROM conversations
WHERE id = :conversation_id AND user_id = :user_id;
```

## Data Integrity

### Constraints Enforced
1. **Referential Integrity**: Message → Conversation (CASCADE delete)
2. **User Isolation**: All queries filter by user_id
3. **Role Validation**: CHECK constraint on message.role
4. **Non-Empty Content**: NOT NULL on message.content

### Soft Delete Consideration
- For Phase III: Hard delete (CASCADE) is acceptable
- Phase V may introduce soft delete for audit trails
- Current design allows easy migration to soft delete later

## Compatibility Notes

### With Existing Phase II
- No changes to `tasks` table
- No changes to `users` table (Better Auth managed)
- New tables are additive, not breaking

### With Phase IV/V
- Schema supports future multi-conversation features
- Conversation metadata extensible (add columns later)
- Message content supports tool_calls serialization if needed
