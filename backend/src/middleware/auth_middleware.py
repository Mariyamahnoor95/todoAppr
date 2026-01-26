"""
JWT authentication middleware.

Extracts and validates JWT tokens from HTTP-only cookies.
Provides user authentication context for protected routes.
"""

from typing import Optional
from uuid import UUID

from fastapi import Cookie, HTTPException, status

from ..services import AuthService

auth_service = AuthService()


def get_user_id_from_token(access_token: Optional[str] = Cookie(None)) -> Optional[UUID]:
    """
    Extract and validate user ID from JWT token cookie.

    Args:
        access_token: JWT token from HTTP-only cookie

    Returns:
        User ID (UUID) if token is valid, None if no token or invalid

    Note:
        Returns None for missing/invalid tokens rather than raising exceptions.
        This allows endpoints to distinguish between authenticated and
        unauthenticated requests.
    """
    if not access_token:
        return None

    # Verify token
    payload = auth_service.verify_jwt_token(access_token)

    if not payload:
        return None

    # Extract user ID from 'sub' claim
    user_id_str = payload.get("sub")

    if not user_id_str:
        return None

    try:
        user_id = UUID(user_id_str)
        return user_id
    except (ValueError, AttributeError):
        return None


def require_auth(access_token: Optional[str] = Cookie(None)) -> UUID:
    """
    Require authentication and return user ID.

    This is a stricter version of get_user_id_from_token that raises
    an HTTPException if authentication fails.

    Args:
        access_token: JWT token from HTTP-only cookie

    Returns:
        User ID (UUID) if authenticated

    Raises:
        HTTPException 401: If token is missing or invalid
    """
    user_id = get_user_id_from_token(access_token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id
