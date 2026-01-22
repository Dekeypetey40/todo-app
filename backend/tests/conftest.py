"""
Pytest configuration and fixtures for testing.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer
from app.database import Base, get_db
from app.main import app


@pytest.fixture(scope="session")
def postgres_container():
    """
    Create a PostgreSQL container for testing.
    Uses the same PostgreSQL version as production.
    """
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def engine(postgres_container):
    """Create database engine using PostgreSQL container."""
    database_url = postgres_container.get_connection_url()
    engine = create_engine(database_url)
    return engine


@pytest.fixture(scope="function")
def db_session(engine):
    """
    Create a fresh database for each test.
    Uses PostgreSQL instead of SQLite for accurate testing.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Clean up tables after each test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
