"""
Authentication API endpoints.

Provides endpoints for user registration, login, and logout.
JWT tokens are set as HTTP-only cookies for security.
"""

from fastapi import APIRouter, HTTPException, Response, status

from ..api.deps import CurrentUserDep, SessionDep
from ..api.schemas import (
    AuthResponse,
    ErrorResponse,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    UserResponse,
)
from ..services import AuthService, DuplicateEmailError, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "User registered successfully",
            "model": AuthResponse,
        },
        400: {
            "description": "Email already exists",
            "model": ErrorResponse,
        },
    },
)
def register(
    request: RegisterRequest,
    response: Response,
    session: SessionDep,
) -> AuthResponse:
    """
    Register a new user account.

    Creates a new user with the provided email and password.
    Password is hashed with bcrypt before storage.
    Sets JWT token as HTTP-only cookie on success.

    Args:
        request: Registration request with email and password
        response: FastAPI response object for setting cookies
        session: Database session

    Returns:
        AuthResponse with user data and success message

    Raises:
        HTTPException 400: If email already exists
    """
    try:
        # Register user
        user = auth_service.register(
            session=session,
            email=request.email,
            password=request.password,
        )

        # Generate JWT token
        token = auth_service.create_jwt_token(user_id=user.id)

        # Set HTTP-only cookie
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=7 * 24 * 60 * 60,  # 7 days in seconds
            samesite="lax",
            secure=False,  # Set to True in production with HTTPS
        )

        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                created_at=user.created_at,
            ),
            message="Registration successful",
        )

    except DuplicateEmailError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    responses={
        200: {
            "description": "Login successful",
            "model": AuthResponse,
        },
        401: {
            "description": "Invalid credentials",
            "model": ErrorResponse,
        },
    },
)
def login(
    request: LoginRequest,
    response: Response,
    session: SessionDep,
) -> AuthResponse:
    """
    Authenticate user and create session.

    Verifies email and password, then generates JWT token.
    Sets JWT token as HTTP-only cookie on success.

    Args:
        request: Login request with email and password
        response: FastAPI response object for setting cookies
        session: Database session

    Returns:
        AuthResponse with user data and success message

    Raises:
        HTTPException 401: If credentials are invalid
    """
    try:
        # Authenticate user
        user = auth_service.login(
            session=session,
            email=request.email,
            password=request.password,
        )

        # Generate JWT token
        token = auth_service.create_jwt_token(user_id=user.id)

        # Set HTTP-only cookie
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=7 * 24 * 60 * 60,  # 7 days in seconds
            samesite="lax",
            secure=False,  # Set to True in production with HTTPS
        )

        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                created_at=user.created_at,
            ),
            message="Login successful",
        )

    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    responses={
        200: {
            "description": "Logout successful",
            "model": MessageResponse,
        },
    },
)
def logout(response: Response) -> MessageResponse:
    """
    Logout user by clearing session cookie.

    Removes the JWT token cookie by setting Max-Age=0.

    Args:
        response: FastAPI response object for clearing cookies

    Returns:
        MessageResponse with success message
    """
    # Clear cookie by setting Max-Age to 0
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        max_age=0,  # Expire immediately
        samesite="lax",
        secure=False,  # Set to True in production with HTTPS
    )

    return MessageResponse(message="Logout successful")


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        200: {
            "description": "Current user information",
            "model": UserResponse,
        },
        401: {
            "description": "Not authenticated",
            "model": ErrorResponse,
        },
    },
)
def get_me(current_user: CurrentUserDep) -> UserResponse:
    """
    Get current authenticated user information.

    Requires valid JWT token in HTTP-only cookie.
    This endpoint demonstrates protected route authentication.

    Args:
        current_user: Authenticated user from JWT token

    Returns:
        UserResponse with current user data

    Raises:
        HTTPException 401: If not authenticated or token invalid
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
    )
