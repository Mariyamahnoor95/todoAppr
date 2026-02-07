"""
Unit tests for ConversationService.

Tests conversation CRUD operations and message management
with user isolation enforcement.
"""

import pytest
from uuid import uuid4

from sqlmodel import Session

from src.models.message import MessageRole
from src.services.conversation_service import (
    ConversationService,
    ConversationNotFoundError,
)


# Test user IDs
TEST_USER_ID = "test-user-123"
OTHER_USER_ID = "other-user-456"


@pytest.fixture
def service():
    """Create a ConversationService instance."""
    return ConversationService(history_limit=20)


class TestCreateConversation:
    """Tests for create_conversation."""

    def test_creates_conversation(self, session: Session, service: ConversationService):
        """Should create a new conversation for user."""
        conversation = service.create_conversation(session, TEST_USER_ID)

        assert conversation.id is not None
        assert conversation.user_id == TEST_USER_ID
        assert conversation.created_at is not None
        assert conversation.updated_at is not None

    def test_creates_unique_ids(self, session: Session, service: ConversationService):
        """Each conversation should have unique ID."""
        conv1 = service.create_conversation(session, TEST_USER_ID)
        conv2 = service.create_conversation(session, TEST_USER_ID)

        assert conv1.id != conv2.id


class TestGetConversation:
    """Tests for get_conversation."""

    def test_returns_existing_conversation(
        self, session: Session, service: ConversationService
    ):
        """Should return conversation when found."""
        created = service.create_conversation(session, TEST_USER_ID)

        fetched = service.get_conversation(session, created.id, TEST_USER_ID)

        assert fetched is not None
        assert fetched.id == created.id

    def test_returns_none_for_wrong_user(
        self, session: Session, service: ConversationService
    ):
        """Should return None if user doesn't own conversation."""
        created = service.create_conversation(session, OTHER_USER_ID)

        fetched = service.get_conversation(session, created.id, TEST_USER_ID)

        assert fetched is None

    def test_returns_none_for_nonexistent(
        self, session: Session, service: ConversationService
    ):
        """Should return None for non-existent conversation."""
        fake_id = uuid4()

        fetched = service.get_conversation(session, fake_id, TEST_USER_ID)

        assert fetched is None


class TestGetOrCreateConversation:
    """Tests for get_or_create_conversation."""

    def test_creates_when_no_id(self, session: Session, service: ConversationService):
        """Should create new conversation when no ID provided."""
        conversation = service.get_or_create_conversation(
            session, TEST_USER_ID, conversation_id=None
        )

        assert conversation is not None
        assert conversation.user_id == TEST_USER_ID

    def test_returns_existing(self, session: Session, service: ConversationService):
        """Should return existing conversation when ID provided."""
        created = service.create_conversation(session, TEST_USER_ID)

        fetched = service.get_or_create_conversation(
            session, TEST_USER_ID, conversation_id=created.id
        )

        assert fetched.id == created.id

    def test_raises_for_not_found(self, session: Session, service: ConversationService):
        """Should raise error when conversation ID not found."""
        fake_id = uuid4()

        with pytest.raises(ConversationNotFoundError):
            service.get_or_create_conversation(
                session, TEST_USER_ID, conversation_id=fake_id
            )

    def test_raises_for_wrong_user(
        self, session: Session, service: ConversationService
    ):
        """Should raise error when user doesn't own conversation."""
        created = service.create_conversation(session, OTHER_USER_ID)

        with pytest.raises(ConversationNotFoundError):
            service.get_or_create_conversation(
                session, TEST_USER_ID, conversation_id=created.id
            )


class TestAddMessage:
    """Tests for add_message."""

    def test_adds_user_message(self, session: Session, service: ConversationService):
        """Should add a user message to conversation."""
        conv = service.create_conversation(session, TEST_USER_ID)

        message = service.add_message(
            session, conv.id, MessageRole.USER, "Hello, bot!"
        )

        assert message.id is not None
        assert message.conversation_id == conv.id
        assert message.role == MessageRole.USER
        assert message.content == "Hello, bot!"

    def test_adds_assistant_message(
        self, session: Session, service: ConversationService
    ):
        """Should add an assistant message to conversation."""
        conv = service.create_conversation(session, TEST_USER_ID)

        message = service.add_message(
            session, conv.id, MessageRole.ASSISTANT, "Hello! How can I help?"
        )

        assert message.role == MessageRole.ASSISTANT


class TestGetConversationHistory:
    """Tests for get_conversation_history."""

    def test_returns_empty_for_new_conversation(
        self, session: Session, service: ConversationService
    ):
        """Should return empty list for conversation with no messages."""
        conv = service.create_conversation(session, TEST_USER_ID)

        history = service.get_conversation_history(session, conv.id)

        assert history == []

    def test_returns_messages_in_order(
        self, session: Session, service: ConversationService
    ):
        """Should return messages in chronological order."""
        conv = service.create_conversation(session, TEST_USER_ID)
        service.add_message(session, conv.id, MessageRole.USER, "First")
        service.add_message(session, conv.id, MessageRole.ASSISTANT, "Second")
        service.add_message(session, conv.id, MessageRole.USER, "Third")

        history = service.get_conversation_history(session, conv.id)

        assert len(history) == 3
        assert history[0]["content"] == "First"
        assert history[1]["content"] == "Second"
        assert history[2]["content"] == "Third"

    def test_respects_limit(self, session: Session):
        """Should respect history limit."""
        service = ConversationService(history_limit=2)
        conv = service.create_conversation(session, TEST_USER_ID)

        service.add_message(session, conv.id, MessageRole.USER, "Message 1")
        service.add_message(session, conv.id, MessageRole.ASSISTANT, "Message 2")
        service.add_message(session, conv.id, MessageRole.USER, "Message 3")

        history = service.get_conversation_history(session, conv.id)

        # Should return only the 2 most recent (but in chronological order)
        assert len(history) == 2
        assert history[0]["content"] == "Message 2"
        assert history[1]["content"] == "Message 3"

    def test_returns_role_and_content(
        self, session: Session, service: ConversationService
    ):
        """Should return messages as dicts with role and content."""
        conv = service.create_conversation(session, TEST_USER_ID)
        service.add_message(session, conv.id, MessageRole.USER, "Hello")

        history = service.get_conversation_history(session, conv.id)

        assert history[0] == {"role": "user", "content": "Hello"}


class TestDeleteConversation:
    """Tests for delete_conversation."""

    def test_deletes_conversation(
        self, session: Session, service: ConversationService
    ):
        """Should delete conversation."""
        conv = service.create_conversation(session, TEST_USER_ID)

        service.delete_conversation(session, conv.id, TEST_USER_ID)

        fetched = service.get_conversation(session, conv.id, TEST_USER_ID)
        assert fetched is None

    def test_raises_for_not_found(self, session: Session, service: ConversationService):
        """Should raise error when conversation not found."""
        fake_id = uuid4()

        with pytest.raises(ConversationNotFoundError):
            service.delete_conversation(session, fake_id, TEST_USER_ID)

    def test_raises_for_wrong_user(
        self, session: Session, service: ConversationService
    ):
        """Should raise error when user doesn't own conversation."""
        conv = service.create_conversation(session, OTHER_USER_ID)

        with pytest.raises(ConversationNotFoundError):
            service.delete_conversation(session, conv.id, TEST_USER_ID)


class TestGetConversations:
    """Tests for get_conversations list."""

    def test_returns_empty_list(self, session: Session, service: ConversationService):
        """Should return empty list when user has no conversations."""
        result = service.get_conversations(session, TEST_USER_ID)

        assert result == []

    def test_returns_user_conversations(
        self, session: Session, service: ConversationService
    ):
        """Should return only user's conversations."""
        service.create_conversation(session, TEST_USER_ID)
        service.create_conversation(session, TEST_USER_ID)
        service.create_conversation(session, OTHER_USER_ID)

        result = service.get_conversations(session, TEST_USER_ID)

        assert len(result) == 2

    def test_includes_message_count(
        self, session: Session, service: ConversationService
    ):
        """Should include message count in summary."""
        conv = service.create_conversation(session, TEST_USER_ID)
        service.add_message(session, conv.id, MessageRole.USER, "Hello")
        service.add_message(session, conv.id, MessageRole.ASSISTANT, "Hi!")

        result = service.get_conversations(session, TEST_USER_ID)

        assert result[0].message_count == 2

    def test_includes_last_message_preview(
        self, session: Session, service: ConversationService
    ):
        """Should include last message preview."""
        conv = service.create_conversation(session, TEST_USER_ID)
        service.add_message(session, conv.id, MessageRole.USER, "Hello")
        service.add_message(session, conv.id, MessageRole.ASSISTANT, "Hi there!")

        result = service.get_conversations(session, TEST_USER_ID)

        assert result[0].last_message_preview == "Hi there!"
