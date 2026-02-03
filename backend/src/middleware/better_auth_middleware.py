"""
Better Auth JWT validation middleware.

Validates JWT tokens issued by Better Auth (EdDSA/Ed25519) using JWKS
and extracts user information.
"""

import json
import time
import urllib.request
from typing import Optional

import jwt
from fastapi import HTTPException, Request, status

from ..config import settings

# Cache for JWKS public keys
_jwks_cache: dict = {}
_jwks_cache_time: float = 0
_JWKS_CACHE_TTL = 3600  # 1 hour


def _get_jwks() -> dict:
    """Fetch and cache JWKS from Better Auth."""
    global _jwks_cache, _jwks_cache_time

    now = time.time()
    if _jwks_cache and (now - _jwks_cache_time) < _JWKS_CACHE_TTL:
        return _jwks_cache

    jwks_url = f"{settings.frontend_url}/api/auth/jwks"
    req = urllib.request.Request(jwks_url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        _jwks_cache = json.loads(resp.read())
    _jwks_cache_time = now
    return _jwks_cache


def _get_signing_key(token: str) -> jwt.algorithms.OKPAlgorithm:
    """Get the signing key for a token from JWKS."""
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")

    jwks = _get_jwks()
    for key_data in jwks.get("keys", []):
        if key_data.get("kid") == kid:
            return jwt.algorithms.OKPAlgorithm.from_jwk(key_data)

    # If kid not found, invalidate cache and retry once
    global _jwks_cache_time
    _jwks_cache_time = 0
    jwks = _get_jwks()
    for key_data in jwks.get("keys", []):
        if key_data.get("kid") == kid:
            return jwt.algorithms.OKPAlgorithm.from_jwk(key_data)

    raise jwt.InvalidTokenError(f"No matching key found for kid: {kid}")


def get_user_from_better_auth_token(request: Request) -> Optional[str]:
    """
    Extract and validate Better Auth JWT token from Authorization header.

    Better Auth issues EdDSA (Ed25519) JWT tokens signed with keys from the JWKS endpoint.

    Args:
        request: FastAPI request object

    Returns:
        User ID (string) if token is valid, None otherwise

    Raises:
        HTTPException: If token is invalid or expired
    """
    authorization = request.headers.get("authorization")

    if not authorization:
        return None

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1]

    try:
        public_key = _get_signing_key(token)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["EdDSA"],
            audience=settings.frontend_url,
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token: missing user ID",
            )

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except (jwt.InvalidTokenError, Exception) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
        )
