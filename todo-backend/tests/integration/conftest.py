"""
Configuration for integration tests.
"""
import pytest
from sqlmodel import create_engine, SQLModel
from sqlalchemy.pool import StaticPool
from database import engine as original_engine
from main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield engine


@pytest.fixture(scope="session")
def test_app(test_engine):
    """Create a test app with the test database."""
    # Override the original engine with the test engine
    app.dependency_overrides[original_engine] = lambda: test_engine
    
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def setup_test_database(test_engine):
    """Set up the test database schema before each test."""
    SQLModel.metadata.create_all(bind=test_engine)
    yield
    # Clean up after each test if needed