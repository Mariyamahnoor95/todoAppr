"""Custom middleware for the FastAPI application."""

from .better_auth_middleware import get_user_from_better_auth_token

__all__ = ["get_user_from_better_auth_token"]
