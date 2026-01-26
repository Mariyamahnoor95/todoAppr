"""
Pytest configuration and fixtures for backend tests.

Provides test database setup, test client, and common fixtures
for unit and integration tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.db import get_session
from src.main import app


@pytest.fixture(name="session")
def session_fixture():
    """
    Create a test database session using in-memory SQLite.

    Yields:
        Session: Test database session

    Note:
        Uses StaticPool to maintain single connection for in-memory SQLite.
        Database is created fresh for each test and torn down after.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Create a test client with overridden database session.

    Args:
        session: Test database session from session_fixture

    Yields:
        TestClient: FastAPI test client

    Note:
        Overrides the get_session dependency to use test database.
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()
