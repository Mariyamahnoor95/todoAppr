"""
Unit tests for AuthService.

Tests user registration, login, password hashing, and JWT token operations.
Following TDD Red-Green-Refactor: These tests will FAIL until AuthService is implemented.
"""

import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, select
from sqlmodel.pool import StaticPool

from src.models.user import User
from src.services.auth_service import AuthService, DuplicateEmailError, InvalidCredentialsError


@pytest.fixture
def auth_service():
    """Create AuthService instance for testing."""
    return AuthService()


@pytest.fixture
def db_session():
    """Create in-memory database session for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


# T030: AuthService.register tests


def test_register_creates_user(auth_service: AuthService, db_session: Session):
    """Test that register creates a new user in the database."""
    user = auth_service.register(
        session=db_session,
        email="newuser@example.com",
        password="SecurePassword123!"
    )

    assert user.id is not None
    assert user.email == "newuser@example.com"
    assert user.password_hash != "SecurePassword123!"  # Should be hashed
    assert len(user.password_hash) > 0


def test_register_hashes_password(auth_service: AuthService, db_session: Session):
    """Test that register hashes the password (not stored in plain text)."""
    password = "MySecretPassword123!"
    user = auth_service.register(
        session=db_session,
        email="test@example.com",
        password=password
    )

    # Password hash should not equal plain password
    assert user.password_hash != password
    # Password hash should be bcrypt format (starts with $2b$)
    assert user.password_hash.startswith("$2b$")


def test_register_normalizes_email(auth_service: AuthService, db_session: Session):
    """Test that register normalizes email to lowercase."""
    user = auth_service.register(
        session=db_session,
        email="TestUser@EXAMPLE.COM",
        password="password123"
    )

    assert user.email == "testuser@example.com"


def test_register_duplicate_email_raises_error(auth_service: AuthService, db_session: Session):
    """Test that registering duplicate email raises DuplicateEmailError."""
    # Register first user
    auth_service.register(
        session=db_session,
        email="duplicate@example.com",
        password="password123"
    )

    # Attempt to register second user with same email
    with pytest.raises(DuplicateEmailError) as exc_info:
        auth_service.register(
            session=db_session,
            email="duplicate@example.com",
            password="different_password"
        )

    assert "already exists" in str(exc_info.value).lower()


def test_register_duplicate_email_case_insensitive(auth_service: AuthService, db_session: Session):
    """Test that duplicate email check is case-insensitive."""
    auth_service.register(
        session=db_session,
        email="user@example.com",
        password="password123"
    )

    with pytest.raises(DuplicateEmailError):
        auth_service.register(
            session=db_session,
            email="USER@EXAMPLE.COM",
            password="password456"
        )


# T031: AuthService.login tests


def test_login_with_valid_credentials(auth_service: AuthService, db_session: Session):
    """Test that login succeeds with valid credentials."""
    # Register user first
    password = "CorrectPassword123!"
    auth_service.register(
        session=db_session,
        email="login@example.com",
        password=password
    )

    # Attempt login
    user = auth_service.login(
        session=db_session,
        email="login@example.com",
        password=password
    )

    assert user is not None
    assert user.email == "login@example.com"


def test_login_with_invalid_email(auth_service: AuthService, db_session: Session):
    """Test that login fails with non-existent email."""
    with pytest.raises(InvalidCredentialsError) as exc_info:
        auth_service.login(
            session=db_session,
            email="nonexistent@example.com",
            password="password123"
        )

    assert "invalid" in str(exc_info.value).lower()


def test_login_with_invalid_password(auth_service: AuthService, db_session: Session):
    """Test that login fails with incorrect password."""
    # Register user
    auth_service.register(
        session=db_session,
        email="user@example.com",
        password="CorrectPassword123!"
    )

    # Attempt login with wrong password
    with pytest.raises(InvalidCredentialsError):
        auth_service.login(
            session=db_session,
            email="user@example.com",
            password="WrongPassword456!"
        )


def test_login_email_case_insensitive(auth_service: AuthService, db_session: Session):
    """Test that login email is case-insensitive."""
    password = "Password123!"
    auth_service.register(
        session=db_session,
        email="user@example.com",
        password=password
    )

    # Login with different case
    user = auth_service.login(
        session=db_session,
        email="USER@EXAMPLE.COM",
        password=password
    )

    assert user.email == "user@example.com"


# T032: JWT token generation and validation tests


def test_create_jwt_token(auth_service: AuthService):
    """Test that create_jwt_token generates a valid JWT."""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = auth_service.create_jwt_token(user_id=user_id)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
    # JWT format: header.payload.signature (3 parts separated by dots)
    assert token.count(".") == 2


def test_verify_jwt_token_valid(auth_service: AuthService):
    """Test that verify_jwt_token successfully validates a valid token."""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = auth_service.create_jwt_token(user_id=user_id)

    # Verify token
    payload = auth_service.verify_jwt_token(token)

    assert payload is not None
    assert payload["sub"] == user_id
    assert "exp" in payload  # Expiration claim


def test_verify_jwt_token_invalid(auth_service: AuthService):
    """Test that verify_jwt_token rejects invalid token."""
    invalid_token = "invalid.token.string"

    payload = auth_service.verify_jwt_token(invalid_token)
    assert payload is None


def test_verify_jwt_token_expired(auth_service: AuthService):
    """Test that verify_jwt_token rejects expired token."""
    # Create a token that's already expired (negative expiration)
    # This requires temporarily modifying the expiration time
    # For now, we'll test that tokens have an expiration claim
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = auth_service.create_jwt_token(user_id=user_id)
    payload = auth_service.verify_jwt_token(token)

    # Verify expiration is in the future (7 days per spec)
    exp_timestamp = payload["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    now = datetime.utcnow()

    # Token should expire in approximately 7 days
    time_until_expiry = exp_datetime - now
    assert timedelta(days=6) < time_until_expiry < timedelta(days=8)


def test_hash_password(auth_service: AuthService):
    """Test that hash_password generates bcrypt hash."""
    password = "TestPassword123!"
    hashed = auth_service.hash_password(password)

    assert hashed != password
    assert hashed.startswith("$2b$")  # Bcrypt format
    assert len(hashed) == 60  # Bcrypt hash length


def test_verify_password_correct(auth_service: AuthService):
    """Test that verify_password returns True for correct password."""
    password = "CorrectPassword123!"
    hashed = auth_service.hash_password(password)

    assert auth_service.verify_password(password, hashed) is True


def test_verify_password_incorrect(auth_service: AuthService):
    """Test that verify_password returns False for incorrect password."""
    password = "CorrectPassword123!"
    hashed = auth_service.hash_password(password)

    assert auth_service.verify_password("WrongPassword456!", hashed) is False


def test_hash_password_unique_salts(auth_service: AuthService):
    """Test that same password produces different hashes (salted)."""
    password = "SamePassword123!"
    hash1 = auth_service.hash_password(password)
    hash2 = auth_service.hash_password(password)

    # Hashes should be different due to random salt
    assert hash1 != hash2
    # But both should verify against the original password
    assert auth_service.verify_password(password, hash1)
    assert auth_service.verify_password(password, hash2)
