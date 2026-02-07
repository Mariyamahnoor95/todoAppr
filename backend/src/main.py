"""
Main FastAPI application entry point.

Configures CORS, API routes, and middleware for the Todo Backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings

app = FastAPI(
    title="Todo API",
    description="Phase II - Web Todo Application Backend",
    version="2.0.0",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        dict: Status message
    """
    return {"status": "healthy"}


# Include API routers
# Note: Authentication is handled by Better Auth in the Next.js frontend
# This backend provides task management and AI chat endpoints
from .api import tasks, chat

app.include_router(tasks.router, prefix=settings.api_prefix)
app.include_router(chat.router, prefix=settings.api_prefix)
