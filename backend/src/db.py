"""
Database session management for SQLModel.

Provides database engine, session factory, and dependency injection
for FastAPI routes.
"""

from typing import Generator

from sqlmodel import Session, create_engine

from .config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Yields:
        Session: SQLModel database session

    Example:
        @app.get("/users")
        def get_users(session: Session = Depends(get_session)):
            return session.exec(select(User)).all()
    """
    with Session(engine) as session:
        yield session
