"""
Integration tests for Chat API endpoints.

Tests the POST /api/{user_id}/chat endpoint with mocked OpenAI responses
to verify request/response handling and authorization.
"""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session

from src.models.conversation import Conversation
from src.models.message import Message, MessageRole


# Test user IDs
TEST_USER_ID = "test-user-123"
OTHER_USER_ID = "other-user-456"

# Mock JWT token (auth verification is handled by Better Auth in production)
TEST_AUTH_HEADER = {"Authorization": "Bearer test-token"}


@pytest.fixture
def mock_openai():
    """Mock OpenAI client for testing."""
    with patch("src.services.chat_service.OpenAI") as mock:
        # Create mock response
        mock_message = MagicMock()
        mock_message.content = "I've added 'Buy groceries' to your tasks."
        mock_message.tool_calls = None

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_auth(client: TestClient):
    """Override the require_better_auth dependency to return test user."""
    from src.api.deps import require_better_auth
    from src.api.chat import reset_chat_service
    from src.main import app

    def override_auth():
        return TEST_USER_ID

    # Reset chat service to allow fresh mocking
    reset_chat_service()

    app.dependency_overrides[require_better_auth] = override_auth
    yield
    app.dependency_overrides.pop(require_better_auth, None)
    reset_chat_service()


class TestChatEndpoint:
    """Tests for POST /api/{user_id}/chat endpoint."""

    def test_creates_new_conversation(
        self,
        client: TestClient,
        session: Session,
        mock_openai: MagicMock,
        mock_auth,
    ):
        """Should create new conversation when no conversation_id provided."""
        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "Add a task to buy groceries"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "response" in data
        assert data["response"] == "I've added 'Buy groceries' to your tasks."

    def test_uses_existing_conversation(
        self,
        client: TestClient,
        session: Session,
        mock_openai: MagicMock,
        mock_auth,
    ):
        """Should use existing conversation when conversation_id provided."""
        # Create a conversation first
        conv = Conversation(user_id=TEST_USER_ID)
        session.add(conv)
        session.commit()
        session.refresh(conv)

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={
                "conversation_id": str(conv.id),
                "message": "Show my tasks",
            },
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == str(conv.id)

    def test_returns_tool_calls(
        self,
        client: TestClient,
        session: Session,
        mock_auth,
    ):
        """Should return tool calls when agent uses tools."""
        with patch("src.services.chat_service.OpenAI") as mock_openai:
            # First call returns tool use
            mock_tool_call = MagicMock()
            mock_tool_call.id = "call_123"
            mock_tool_call.function.name = "add_task"
            mock_tool_call.function.arguments = '{"title": "Buy groceries"}'

            mock_message_with_tools = MagicMock()
            mock_message_with_tools.content = None
            mock_message_with_tools.tool_calls = [mock_tool_call]
            mock_message_with_tools.model_dump.return_value = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_123",
                        "type": "function",
                        "function": {
                            "name": "add_task",
                            "arguments": '{"title": "Buy groceries"}',
                        },
                    }
                ],
            }

            # Second call returns final message
            mock_final_message = MagicMock()
            mock_final_message.content = "I've added 'Buy groceries' to your tasks."
            mock_final_message.tool_calls = None

            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = [
                MagicMock(choices=[MagicMock(message=mock_message_with_tools)]),
                MagicMock(choices=[MagicMock(message=mock_final_message)]),
            ]
            mock_openai.return_value = mock_client

            response = client.post(
                f"/api/{TEST_USER_ID}/chat",
                json={"message": "Add buy groceries to my tasks"},
                headers=TEST_AUTH_HEADER,
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["tool_calls"]) == 1
            assert data["tool_calls"][0]["tool"] == "add_task"

    def test_rejects_empty_message(
        self,
        client: TestClient,
        mock_auth,
    ):
        """Should reject empty message with 400."""
        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": ""},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 422  # Pydantic validation error

    def test_rejects_whitespace_message(
        self,
        client: TestClient,
        mock_openai: MagicMock,
        mock_auth,
    ):
        """Should reject whitespace-only message."""
        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": "   "},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_rejects_wrong_user(
        self,
        client: TestClient,
        mock_openai: MagicMock,
        mock_auth,
    ):
        """Should reject request when path user_id doesn't match auth."""
        response = client.post(
            f"/api/{OTHER_USER_ID}/chat",
            json={"message": "Hello"},
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 403
        assert "own chat" in response.json()["detail"].lower()

    def test_returns_404_for_invalid_conversation(
        self,
        client: TestClient,
        mock_openai: MagicMock,
        mock_auth,
    ):
        """Should return 404 when conversation_id not found."""
        fake_conv_id = str(uuid4())

        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={
                "conversation_id": fake_conv_id,
                "message": "Hello",
            },
            headers=TEST_AUTH_HEADER,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestChatWithToolExecution:
    """Tests for chat endpoint with MCP tool execution."""

    def test_add_task_creates_task(
        self,
        client: TestClient,
        session: Session,
        mock_auth,
    ):
        """Should create task when agent calls add_task tool."""
        with patch("src.services.chat_service.OpenAI") as mock_openai:
            # Simulate add_task tool call
            mock_tool_call = MagicMock()
            mock_tool_call.id = "call_add"
            mock_tool_call.function.name = "add_task"
            mock_tool_call.function.arguments = '{"title": "Test task"}'

            mock_message_with_tools = MagicMock()
            mock_message_with_tools.content = None
            mock_message_with_tools.tool_calls = [mock_tool_call]
            mock_message_with_tools.model_dump.return_value = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_add",
                        "type": "function",
                        "function": {
                            "name": "add_task",
                            "arguments": '{"title": "Test task"}',
                        },
                    }
                ],
            }

            mock_final = MagicMock()
            mock_final.content = "Task created!"
            mock_final.tool_calls = None

            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = [
                MagicMock(choices=[MagicMock(message=mock_message_with_tools)]),
                MagicMock(choices=[MagicMock(message=mock_final)]),
            ]
            mock_openai.return_value = mock_client

            response = client.post(
                f"/api/{TEST_USER_ID}/chat",
                json={"message": "Add test task"},
                headers=TEST_AUTH_HEADER,
            )

            assert response.status_code == 200
            data = response.json()

            # Verify tool was called
            assert len(data["tool_calls"]) == 1
            assert data["tool_calls"][0]["tool"] == "add_task"
            assert data["tool_calls"][0]["result"]["status"] == "created"

    def test_list_tasks_returns_tasks(
        self,
        client: TestClient,
        session: Session,
        mock_auth,
    ):
        """Should return tasks when agent calls list_tasks tool."""
        # First create a task via direct database
        from src.models.task import Task

        task = Task(user_id=TEST_USER_ID, title="Existing task")
        session.add(task)
        session.commit()

        with patch("src.services.chat_service.OpenAI") as mock_openai:
            mock_tool_call = MagicMock()
            mock_tool_call.id = "call_list"
            mock_tool_call.function.name = "list_tasks"
            mock_tool_call.function.arguments = "{}"

            mock_message_with_tools = MagicMock()
            mock_message_with_tools.content = None
            mock_message_with_tools.tool_calls = [mock_tool_call]
            mock_message_with_tools.model_dump.return_value = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_list",
                        "type": "function",
                        "function": {"name": "list_tasks", "arguments": "{}"},
                    }
                ],
            }

            mock_final = MagicMock()
            mock_final.content = "Here are your tasks."
            mock_final.tool_calls = None

            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = [
                MagicMock(choices=[MagicMock(message=mock_message_with_tools)]),
                MagicMock(choices=[MagicMock(message=mock_final)]),
            ]
            mock_openai.return_value = mock_client

            response = client.post(
                f"/api/{TEST_USER_ID}/chat",
                json={"message": "Show my tasks"},
                headers=TEST_AUTH_HEADER,
            )

            assert response.status_code == 200
            data = response.json()

            assert len(data["tool_calls"]) == 1
            assert data["tool_calls"][0]["tool"] == "list_tasks"
            assert data["tool_calls"][0]["result"]["count"] == 1
