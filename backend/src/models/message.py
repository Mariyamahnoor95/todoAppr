"""Message model for AI chatbot conversation messages."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class MessageRole(str, Enum):
    """Enum for message sender role."""

    USER = "user"
    ASSISTANT = "assistant"


class MessageBase(SQLModel):
    """Base message model with shared attributes."""

    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False, index=True)
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False)


class Message(MessageBase, table=True):
    """Message database model representing a single chat message."""

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MessageCreate(SQLModel):
    """Schema for creating a new message."""

    role: MessageRole
    content: str


class MessageRead(SQLModel):
    """Schema for reading a message."""

    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    created_at: datetime
