"""
Integration tests for event-driven flows in the todo application.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool

from events.consumer import EventConsumer, validate_event_schema
from events.producer import EventProducer, publish_task_event
from models.todo import Todo, Priority
from models.user import User
from database import engine as db_engine
from services.todo_service import TodoService


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_task_created_event_flow(db_session, sample_user):
    """Test the complete flow from task creation to event processing."""
    # Mock the Kafka producer
    with patch.object(EventProducer, 'publish_event', new_callable=AsyncMock) as mock_publish:
        # Create a task using the service
        service = TodoService()
        new_task = service.create_todo_with_advanced_features(
            session=db_session,
            title="Test Task",
            description="Test Description",
            user_id=sample_user.id,
            priority=Priority.high,
            tags=["test", "important"],
            due_date=None
        )
        
        # Verify the task was created
        assert new_task.title == "Test Task"
        assert new_task.user_id == sample_user.id
        
        # Wait for async event publishing to complete
        await asyncio.sleep(0.1)
        
        # Verify that an event was published
        assert mock_publish.called
        args, kwargs = mock_publish.call_args
        topic, event_data = args
        
        assert topic == "task-events"
        assert event_data["type"] == "task.created"
        assert event_data["data"]["id"] == str(new_task.id)


@pytest.mark.asyncio
async def test_task_updated_event_flow(db_session, sample_user):
    """Test the complete flow from task update to event processing."""
    # Create a task first
    service = TodoService()
    original_task = service.create_todo_with_advanced_features(
        session=db_session,
        title="Original Task",
        description="Original Description",
        user_id=sample_user.id,
        priority=Priority.low,
        tags=["original"],
        due_date=None
    )
    
    # Mock the Kafka producer
    with patch.object(EventProducer, 'publish_event', new_callable=AsyncMock) as mock_publish:
        # Update the task using the service
        updated_task = service.update_todo_with_advanced_features(
            session=db_session,
            todo_id=original_task.id,
            title="Updated Task",
            priority=Priority.high
        )
        
        # Verify the task was updated
        assert updated_task.title == "Updated Task"
        assert updated_task.priority == Priority.high
        
        # Wait for async event publishing to complete
        await asyncio.sleep(0.1)
        
        # Verify that an event was published
        assert mock_publish.called
        args, kwargs = mock_publish.call_args
        topic, event_data = args
        
        assert topic == "task-events"
        assert event_data["type"] == "task.updated"


@pytest.mark.asyncio
async def test_task_deleted_event_flow(db_session, sample_user):
    """Test the complete flow from task deletion to event processing."""
    # Create a task first
    service = TodoService()
    task_to_delete = service.create_todo_with_advanced_features(
        session=db_session,
        title="Task to Delete",
        description="Description",
        user_id=sample_user.id,
        priority=Priority.medium,
        tags=["delete"],
        due_date=None
    )
    
    # Mock the Kafka producer
    with patch.object(EventProducer, 'publish_event', new_callable=AsyncMock) as mock_publish:
        # Delete the task using the service
        result = service.delete_todo(
            session=db_session,
            todo_id=task_to_delete.id
        )
        
        # Verify the task was deleted
        assert result is True
        
        # Wait for async event publishing to complete
        await asyncio.sleep(0.1)
        
        # Verify that an event was published
        assert mock_publish.called
        args, kwargs = mock_publish.call_args
        topic, event_data = args
        
        assert topic == "task-events"
        assert event_data["type"] == "task.deleted"


def test_event_schema_validation():
    """Test the event schema validation functionality."""
    # Valid task event data
    valid_task_data = {
        "id": "123",
        "type": "task.created",
        "source": "todo-backend",
        "timestamp": "2023-01-01T00:00:00Z",
        "data": {
            "id": "123",
            "title": "Test Task",
            "description": "Test Description",
            "status": "pending",
            "priority": "medium",
            "tags": ["test"],
            "due_date": None,
            "recurrence_pattern": None,
            "next_occurrence_date": None,
            "user_id": "456",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": None,
            "completed_at": None
        },
        "correlation_id": "789"
    }
    
    # Validate the schema
    is_valid, error_msg = validate_event_schema("task-events", valid_task_data)
    assert is_valid is True
    assert error_msg == ""
    
    # Invalid task event data (missing required field)
    invalid_task_data = {
        "id": "123",
        "type": "task.created",
        "source": "todo-backend",
        "timestamp": "2023-01-01T00:00:00Z",
        # Missing required "data" field
        "correlation_id": "789"
    }
    
    # Validate the schema
    is_valid, error_msg = validate_event_schema("task-events", invalid_task_data)
    assert is_valid is False
    assert error_msg != ""


@pytest.mark.asyncio
async def test_event_consumer_processing():
    """Test the event consumer processing functionality."""
    # Sample event data
    sample_event_data = {
        "id": "123",
        "type": "task.created",
        "source": "todo-backend",
        "timestamp": "2023-01-01T00:00:00Z",
        "data": {
            "id": "123",
            "title": "Test Task",
            "description": "Test Description",
            "status": "pending",
            "priority": "medium",
            "tags": ["test"],
            "due_date": None,
            "recurrence_pattern": None,
            "next_occurrence_date": None,
            "user_id": "456",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": None,
            "completed_at": None
        },
        "correlation_id": "789"
    }
    
    # Mock the database session
    with patch('events.consumer.Session') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        # Process the event
        await EventConsumer._process_event("task-events", sample_event_data)
        
        # Verify that the event was processed without errors
        # (the function should complete without raising exceptions)