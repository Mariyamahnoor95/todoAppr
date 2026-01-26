"""
User model for authentication and authorization.

Represents a user account with email-based authentication.
Passwords are stored as bcrypt hashes, never in plain text.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """
    User account model.

    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address (unique, stored lowercase)
        password_hash: Bcrypt hash of user's password
        created_at: Account creation timestamp

    Note:
        Email normalization (lowercase) is handled at the service layer
        before saving to ensure case-insensitive uniqueness.
    """

    __tablename__ = "users"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(min_length=1, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
