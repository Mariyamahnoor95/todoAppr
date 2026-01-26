"""
Unit tests for User model.

Tests email validation, password hashing, and model constraints.
Following TDD Red-Green-Refactor: These tests will FAIL until User model is implemented.
"""

import pytest
from pydantic import ValidationError
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from src.models.user import User


def test_user_model_valid_email():
    """Test that User model accepts valid email addresses."""
    user = User(email="test@example.com", password_hash="hashed_password_123")
    assert user.email == "test@example.com"
    assert user.password_hash == "hashed_password_123"


def test_user_model_accepts_valid_email_format():
    """Test that User model stores email in EmailStr format."""
    user = User(email="valid.email+tag@example.com", password_hash="hashed_password_123")
    assert "@" in user.email
    assert "." in user.email


def test_user_model_has_id():
    """Test that User model has an id field."""
    user = User(email="test@example.com", password_hash="hashed_password_123")
    # ID should be None before database insert
    assert hasattr(user, "id")


def test_user_model_has_timestamps():
    """Test that User model has created_at timestamp."""
    user = User(email="test@example.com", password_hash="hashed_password_123")
    assert hasattr(user, "created_at")


def test_user_model_database_persistence():
    """Test that User can be saved to and retrieved from database."""
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Import SQLModel to create tables
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

    # Create and save user
    with Session(engine) as session:
        user = User(email="db-test@example.com", password_hash="hashed_password_123")
        session.add(user)
        session.commit()
        session.refresh(user)

        # Verify user was saved with ID
        assert user.id is not None
        assert user.email == "db-test@example.com"

        # Retrieve user from database
        user_id = user.id

    # Verify user persists in new session
    with Session(engine) as session:
        retrieved_user = session.get(User, user_id)
        assert retrieved_user is not None
        assert retrieved_user.email == "db-test@example.com"
        assert retrieved_user.password_hash == "hashed_password_123"


def test_user_model_email_unique_constraint():
    """Test that email has unique constraint in database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

    # Create first user
    with Session(engine) as session:
        user1 = User(email="unique@example.com", password_hash="hash1")
        session.add(user1)
        session.commit()

    # Attempt to create second user with same email
    with pytest.raises(Exception) as exc_info:
        with Session(engine) as session:
            user2 = User(email="unique@example.com", password_hash="hash2")
            session.add(user2)
            session.commit()

    # Should raise integrity error (exact error type varies by database)
    assert "unique" in str(exc_info.value).lower() or "integrity" in str(exc_info.value).lower()
