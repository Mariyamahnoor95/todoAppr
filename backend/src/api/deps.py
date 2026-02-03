"""
API dependencies for dependency injection.

Provides common dependencies used across API routes:
- Database session
- Current authenticated user (via Better Auth JWT)
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from ..db import get_session
from ..middleware import get_user_from_better_auth_token

# Database session dependency
SessionDep = Annotated[Session, Depends(get_session)]


def require_better_auth(request: Request) -> str:
    """
    Require Better Auth JWT token and return user ID.

    Args:
        request: FastAPI request object

    Returns:
        User ID string from Better Auth JWT token

    Raises:
        HTTPException 401: If not authenticated
    """
    user_id = get_user_from_better_auth_token(request)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


# User ID from Better Auth JWT token (requires authentication)
UserIdDep = Annotated[str, Depends(require_better_auth)]
