"""
Authentication service for user registration and login.

Handles password hashing with bcrypt, JWT token generation and validation,
and user authentication workflows.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import bcrypt
from jose import JWTError, jwt
from sqlmodel import Session, select

from ..config import settings
from ..models.user import User


# Custom exceptions
class DuplicateEmailError(Exception):
    """Raised when attempting to register with an email that already exists."""

    pass


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""

    pass


class AuthService:
    """
    Service for user authentication and authorization.

    Provides methods for:
    - User registration with password hashing
    - User login with credential verification
    - JWT token generation and validation
    - Password hashing and verification
    """

    def hash_password(self, password: str) -> str:
        """
        Hash a plain-text password using bcrypt.

        Args:
            password: Plain-text password to hash

        Returns:
            Bcrypt hash of the password (60 characters, starts with $2b$)
        """
        # Encode password to bytes
        password_bytes = password.encode('utf-8')
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        # Return as string
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain-text password against a bcrypt hash.

        Args:
            plain_password: Plain-text password to verify
            hashed_password: Bcrypt hash to verify against

        Returns:
            True if password matches hash, False otherwise
        """
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    def register(self, session: Session, email: str, password: str) -> User:
        """
        Register a new user account.

        Args:
            session: Database session
            email: User's email address
            password: Plain-text password

        Returns:
            Created User object

        Raises:
            DuplicateEmailError: If email already exists (case-insensitive)
        """
        # Normalize email to lowercase for case-insensitive uniqueness
        email_normalized = email.lower().strip()

        # Check if email already exists
        statement = select(User).where(User.email == email_normalized)
        existing_user = session.exec(statement).first()

        if existing_user:
            raise DuplicateEmailError(f"User with email {email} already exists")

        # Hash password and create user
        password_hash = self.hash_password(password)
        user = User(email=email_normalized, password_hash=password_hash)

        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    def login(self, session: Session, email: str, password: str) -> User:
        """
        Authenticate user with email and password.

        Args:
            session: Database session
            email: User's email address (case-insensitive)
            password: Plain-text password

        Returns:
            User object if authentication succeeds

        Raises:
            InvalidCredentialsError: If email doesn't exist or password is incorrect
        """
        # Normalize email to lowercase
        email_normalized = email.lower().strip()

        # Find user by email
        statement = select(User).where(User.email == email_normalized)
        user = session.exec(statement).first()

        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        # Verify password
        if not self.verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        return user

    def create_jwt_token(self, user_id: str | UUID) -> str:
        """
        Create a JWT access token for a user.

        Args:
            user_id: User's unique identifier (UUID or string)

        Returns:
            JWT token string

        Note:
            Token expires after jwt_access_token_expire_days (default 7 days).
            Token contains 'sub' (subject) claim with user_id and 'exp' (expiration).
        """
        # Convert UUID to string if needed
        if isinstance(user_id, UUID):
            user_id = str(user_id)

        # Calculate expiration time
        expire = datetime.utcnow() + timedelta(days=settings.jwt_access_token_expire_days)

        # Create JWT payload
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        # Encode token
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        return token

    def verify_jwt_token(self, token: str) -> Optional[dict]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string to verify

        Returns:
            Decoded token payload if valid, None if invalid/expired

        Note:
            Returns None for invalid tokens rather than raising exceptions
            to simplify error handling in middleware.
        """
        try:
            payload = jwt.decode(
                token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError:
            return None
