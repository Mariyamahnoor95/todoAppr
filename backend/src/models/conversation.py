"""Conversation model for AI chatbot conversations."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class ConversationBase(SQLModel):
    """Base conversation model with shared attributes."""

    user_id: str = Field(index=True, nullable=False)


class Conversation(ConversationBase, table=True):
    """Conversation database model representing a chat session."""

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation."""

    pass


class ConversationRead(ConversationBase):
    """Schema for reading a conversation."""

    id: UUID
    created_at: datetime
    updated_at: datetime


class ConversationSummary(SQLModel):
    """Schema for conversation list with summary info."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message_preview: Optional[str] = None
