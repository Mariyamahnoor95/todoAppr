"""
Conversation service for managing chat conversations and messages.

Handles conversation creation, retrieval, message storage, and history loading.
Enforces user isolation - users can only access their own conversations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Session, func, select

from ..models.conversation import Conversation, ConversationSummary
from ..models.message import Message, MessageRole


class ConversationNotFoundError(Exception):
    """Raised when a conversation is not found or user doesn't have access."""

    pass


class ConversationService:
    """
    Service for conversation CRUD operations.

    All methods enforce user isolation - conversations are scoped to the authenticated user.
    """

    def __init__(self, history_limit: int = 20):
        """
        Initialize conversation service.

        Args:
            history_limit: Maximum number of messages to load for context
        """
        self.history_limit = history_limit

    def get_or_create_conversation(
        self,
        session: Session,
        user_id: str,
        conversation_id: Optional[UUID] = None,
    ) -> Conversation:
        """
        Get existing conversation or create a new one.

        Args:
            session: Database session
            user_id: User ID who owns the conversation
            conversation_id: Optional existing conversation ID

        Returns:
            Conversation object

        Raises:
            ConversationNotFoundError: If conversation_id provided but not found/owned
        """
        if conversation_id:
            conversation = self.get_conversation(session, conversation_id, user_id)
            if not conversation:
                raise ConversationNotFoundError(
                    f"Conversation {conversation_id} not found"
                )
            return conversation

        return self.create_conversation(session, user_id)

    def create_conversation(self, session: Session, user_id: str) -> Conversation:
        """
        Create a new conversation.

        Args:
            session: Database session
            user_id: User ID who owns the conversation

        Returns:
            Created Conversation object
        """
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    def get_conversation(
        self,
        session: Session,
        conversation_id: UUID,
        user_id: str,
    ) -> Optional[Conversation]:
        """
        Get a conversation by ID with user ownership verification.

        Args:
            session: Database session
            conversation_id: Conversation ID to retrieve
            user_id: User ID for ownership verification

        Returns:
            Conversation if found and owned by user, None otherwise
        """
        query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        return session.exec(query).first()

    def get_conversations(
        self,
        session: Session,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[ConversationSummary]:
        """
        Get user's conversations with summary info.

        Args:
            session: Database session
            user_id: User ID to filter conversations
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            List of ConversationSummary objects ordered by last update
        """
        # Get conversations ordered by updated_at
        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        conversations = session.exec(query).all()

        # Build summaries with message counts
        summaries = []
        for conv in conversations:
            # Count messages
            count_query = (
                select(func.count())
                .select_from(Message)
                .where(Message.conversation_id == conv.id)
            )
            message_count = session.exec(count_query).one()

            # Get last message preview
            last_msg_query = (
                select(Message)
                .where(Message.conversation_id == conv.id)
                .order_by(Message.created_at.desc())
                .limit(1)
            )
            last_message = session.exec(last_msg_query).first()
            preview = None
            if last_message:
                preview = (
                    last_message.content[:100]
                    if len(last_message.content) > 100
                    else last_message.content
                )

            summaries.append(
                ConversationSummary(
                    id=conv.id,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    message_count=message_count,
                    last_message_preview=preview,
                )
            )

        return summaries

    def get_conversation_count(self, session: Session, user_id: str) -> int:
        """
        Get total count of conversations for a user.

        Args:
            session: Database session
            user_id: User ID to count conversations for

        Returns:
            Total number of conversations
        """
        query = (
            select(func.count())
            .select_from(Conversation)
            .where(Conversation.user_id == user_id)
        )
        return session.exec(query).one()

    def delete_conversation(
        self,
        session: Session,
        conversation_id: UUID,
        user_id: str,
    ) -> None:
        """
        Delete a conversation and all its messages.

        Args:
            session: Database session
            conversation_id: Conversation ID to delete
            user_id: User ID for ownership verification

        Raises:
            ConversationNotFoundError: If conversation not found/owned
        """
        conversation = self.get_conversation(session, conversation_id, user_id)
        if not conversation:
            raise ConversationNotFoundError(
                f"Conversation {conversation_id} not found"
            )

        session.delete(conversation)
        session.commit()

    def add_message(
        self,
        session: Session,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            session: Database session
            conversation_id: Conversation to add message to
            role: Message role (user or assistant)
            content: Message content

        Returns:
            Created Message object
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        return message

    def get_conversation_history(
        self,
        session: Session,
        conversation_id: UUID,
        limit: Optional[int] = None,
    ) -> list[dict[str, str]]:
        """
        Get conversation history for AI context.

        Args:
            session: Database session
            conversation_id: Conversation to load history from
            limit: Maximum messages to return (defaults to history_limit)

        Returns:
            List of message dicts with role and content, in chronological order
        """
        limit = limit or self.history_limit

        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(session.exec(query).all())

        # Return in chronological order (oldest first)
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in reversed(messages)
        ]

    def get_messages(
        self,
        session: Session,
        conversation_id: UUID,
        user_id: str,
        limit: int = 50,
    ) -> list[Message]:
        """
        Get messages for a conversation with user verification.

        Args:
            session: Database session
            conversation_id: Conversation to get messages from
            user_id: User ID for ownership verification
            limit: Maximum messages to return

        Returns:
            List of Message objects in chronological order

        Raises:
            ConversationNotFoundError: If conversation not found/owned
        """
        # Verify user owns conversation
        conversation = self.get_conversation(session, conversation_id, user_id)
        if not conversation:
            raise ConversationNotFoundError(
                f"Conversation {conversation_id} not found"
            )

        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        return list(session.exec(query).all())
