"""
Unit tests for MCP tools.

Tests each MCP tool in isolation to verify correct behavior
for task management operations.
"""

import pytest
from sqlmodel import Session

from src.mcp.tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    get_mcp_tools,
)
from src.models.task import Task


# Test user ID for all tests
TEST_USER_ID = "test-user-123"
OTHER_USER_ID = "other-user-456"


class TestGetMCPTools:
    """Tests for get_mcp_tools function."""

    def test_returns_five_tools(self):
        """Should return all 5 MCP tool definitions."""
        tools = get_mcp_tools()
        assert len(tools) == 5

    def test_tool_names(self):
        """Should have correct tool names."""
        tools = get_mcp_tools()
        tool_names = [t["function"]["name"] for t in tools]
        assert "add_task" in tool_names
        assert "list_tasks" in tool_names
        assert "complete_task" in tool_names
        assert "delete_task" in tool_names
        assert "update_task" in tool_names

    def test_tools_have_descriptions(self):
        """Each tool should have a description."""
        tools = get_mcp_tools()
        for tool in tools:
            assert "description" in tool["function"]
            assert len(tool["function"]["description"]) > 0


class TestAddTask:
    """Tests for add_task MCP tool."""

    def test_add_task_success(self, session: Session):
        """Should create task and return success response."""
        result = add_task(
            session=session,
            user_id=TEST_USER_ID,
            title="Buy groceries",
            description="Milk, eggs, bread",
        )

        assert result["status"] == "created"
        assert result["title"] == "Buy groceries"
        assert "task_id" in result

    def test_add_task_without_description(self, session: Session):
        """Should create task without description."""
        result = add_task(
            session=session,
            user_id=TEST_USER_ID,
            title="Call mom",
        )

        assert result["status"] == "created"
        assert result["title"] == "Call mom"

    def test_add_task_empty_title(self, session: Session):
        """Should return error for empty title."""
        result = add_task(
            session=session,
            user_id=TEST_USER_ID,
            title="",
        )

        assert "error" in result
        assert result["error"] == "validation_error"

    def test_add_task_title_too_long(self, session: Session):
        """Should return error for title exceeding 200 chars."""
        result = add_task(
            session=session,
            user_id=TEST_USER_ID,
            title="x" * 201,
        )

        assert "error" in result
        assert result["error"] == "validation_error"


class TestListTasks:
    """Tests for list_tasks MCP tool."""

    def test_list_tasks_empty(self, session: Session):
        """Should return empty list when no tasks."""
        result = list_tasks(
            session=session,
            user_id=TEST_USER_ID,
        )

        assert result["count"] == 0
        assert result["tasks"] == []

    def test_list_tasks_all(self, session: Session):
        """Should return all tasks for user."""
        # Create test tasks
        add_task(session, TEST_USER_ID, "Task 1")
        add_task(session, TEST_USER_ID, "Task 2")

        result = list_tasks(session, TEST_USER_ID, status="all")

        assert result["count"] == 2

    def test_list_tasks_pending_only(self, session: Session):
        """Should filter to pending tasks only."""
        # Create tasks
        add_result = add_task(session, TEST_USER_ID, "Pending task")
        task_id = add_result["task_id"]

        # Complete one task
        complete_task(session, TEST_USER_ID, task_id)

        # Add another pending task
        add_task(session, TEST_USER_ID, "Another pending")

        result = list_tasks(session, TEST_USER_ID, status="pending")

        # Only the uncompleted task should be returned
        assert result["count"] == 1
        assert result["tasks"][0]["title"] == "Another pending"

    def test_list_tasks_user_isolation(self, session: Session):
        """Should only return tasks for the specified user."""
        add_task(session, TEST_USER_ID, "My task")
        add_task(session, OTHER_USER_ID, "Other user task")

        result = list_tasks(session, TEST_USER_ID)

        assert result["count"] == 1
        assert result["tasks"][0]["title"] == "My task"


class TestCompleteTask:
    """Tests for complete_task MCP tool."""

    def test_complete_task_success(self, session: Session):
        """Should mark task as complete."""
        add_result = add_task(session, TEST_USER_ID, "Test task")
        task_id = add_result["task_id"]

        result = complete_task(session, TEST_USER_ID, task_id)

        assert result["status"] == "completed"
        assert result["task_id"] == task_id

    def test_complete_task_not_found(self, session: Session):
        """Should return error for non-existent task."""
        result = complete_task(
            session, TEST_USER_ID, "00000000-0000-0000-0000-000000000000"
        )

        assert "error" in result
        assert result["error"] == "task_not_found"
        assert "suggestion" in result

    def test_complete_task_invalid_id(self, session: Session):
        """Should return error for invalid task ID format."""
        result = complete_task(session, TEST_USER_ID, "invalid-id")

        assert "error" in result
        assert result["error"] == "invalid_task_id"

    def test_complete_task_user_isolation(self, session: Session):
        """Should not complete another user's task."""
        add_result = add_task(session, OTHER_USER_ID, "Other task")
        task_id = add_result["task_id"]

        result = complete_task(session, TEST_USER_ID, task_id)

        assert "error" in result
        assert result["error"] == "task_not_found"


class TestDeleteTask:
    """Tests for delete_task MCP tool."""

    def test_delete_task_success(self, session: Session):
        """Should delete task."""
        add_result = add_task(session, TEST_USER_ID, "To delete")
        task_id = add_result["task_id"]

        result = delete_task(session, TEST_USER_ID, task_id)

        assert result["status"] == "deleted"
        assert result["title"] == "To delete"

        # Verify task is deleted
        list_result = list_tasks(session, TEST_USER_ID)
        assert list_result["count"] == 0

    def test_delete_task_not_found(self, session: Session):
        """Should return error for non-existent task."""
        result = delete_task(
            session, TEST_USER_ID, "00000000-0000-0000-0000-000000000000"
        )

        assert "error" in result
        assert result["error"] == "task_not_found"

    def test_delete_task_user_isolation(self, session: Session):
        """Should not delete another user's task."""
        add_result = add_task(session, OTHER_USER_ID, "Other task")
        task_id = add_result["task_id"]

        result = delete_task(session, TEST_USER_ID, task_id)

        assert "error" in result
        assert result["error"] == "task_not_found"


class TestUpdateTask:
    """Tests for update_task MCP tool."""

    def test_update_task_title(self, session: Session):
        """Should update task title."""
        add_result = add_task(session, TEST_USER_ID, "Original title")
        task_id = add_result["task_id"]

        result = update_task(
            session, TEST_USER_ID, task_id, title="Updated title"
        )

        assert result["status"] == "updated"
        assert result["title"] == "Updated title"

    def test_update_task_description(self, session: Session):
        """Should update task description."""
        add_result = add_task(session, TEST_USER_ID, "Task")
        task_id = add_result["task_id"]

        result = update_task(
            session, TEST_USER_ID, task_id, description="New description"
        )

        assert result["status"] == "updated"

    def test_update_task_not_found(self, session: Session):
        """Should return error for non-existent task."""
        result = update_task(
            session,
            TEST_USER_ID,
            "00000000-0000-0000-0000-000000000000",
            title="New title",
        )

        assert "error" in result
        assert result["error"] == "task_not_found"

    def test_update_task_user_isolation(self, session: Session):
        """Should not update another user's task."""
        add_result = add_task(session, OTHER_USER_ID, "Other task")
        task_id = add_result["task_id"]

        result = update_task(session, TEST_USER_ID, task_id, title="Hacked")

        assert "error" in result
        assert result["error"] == "task_not_found"
