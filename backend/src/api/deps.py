"""
API dependencies for dependency injection.

Provides common dependencies used across API routes:
- Database session
- Current authenticated user
- Authorization checks
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from ..db import get_session
from ..middleware import require_auth
from ..models.user import User

# Database session dependency
SessionDep = Annotated[Session, Depends(get_session)]

# User ID from JWT token (requires authentication)
UserIdDep = Annotated[UUID, Depends(require_auth)]


def get_current_user(
    user_id: UserIdDep,
    session: SessionDep,
) -> User:
    """
    Get the current authenticated user from JWT token.

    Extracts user ID from JWT token cookie, then fetches full User
    object from database.

    Args:
        user_id: User ID extracted from JWT token
        session: Database session

    Returns:
        User object for authenticated user

    Raises:
        HTTPException 401: If authentication fails or user not found
    """
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# Current user dependency
CurrentUserDep = Annotated[User, Depends(get_current_user)]
