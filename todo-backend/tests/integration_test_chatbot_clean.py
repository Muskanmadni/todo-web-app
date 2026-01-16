"""
Integration tests for the chatbot workflow without conflicting models
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from datetime import datetime
from unittest.mock import patch, MagicMock
from uuid import uuid4

from api.chatbot import router, ChatRequest, ChatResponse
from database import get_session
from mcp.tools import TodoMCPTools
from services.todo_service import TodoService
from models.todo import Todo
from models.user import User
from models.conversation import Conversation
from models.message import Message


# Create a test database engine
test_engine = create_engine(
    "sqlite:///:memory:",
    echo=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


# Create a minimal FastAPI app for testing the chatbot API
from fastapi import FastAPI
app = FastAPI()
app.include_router(router, prefix="/api", tags=["chat"])


# Dependency to override the database session
def get_test_session():
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    # Override the dependency in the app
    app.dependency_overrides[get_session] = get_test_session
    
    with TestClient(app) as client:
        # Create tables in the test database
        SQLModel.metadata.create_all(test_engine)
        yield client


def test_chatbot_create_todo(client: TestClient):
    """Test creating a todo through the chatbot interface"""
    # Send a message to create a todo
    response = client.post(
        "/api/chat/conversation",
        json={"message": "Add a todo: Buy groceries"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "conversationId" in data
    assert "response" in data
    assert "action" in data
    assert data["action"] == "todo_created"
    
    # Verify the response mentions the created todo
    assert "Buy groceries" in data["response"]
    
    # Verify todo data is returned
    assert "todo" in data
    assert data["todo"] is not None
    assert data["todo"]["title"] == "Buy groceries"
    assert data["todo"]["status"] == "pending"


def test_chatbot_complete_todo(client: TestClient):
    """Test completing a todo through the chatbot interface"""
    # First, create a todo
    create_response = client.post(
        "/api/chat/conversation",
        json={"message": "Add a todo: Complete this task"}
    )
    
    assert create_response.status_code == 200
    create_data = create_response.json()
    assert create_data["action"] == "todo_created"
    
    # Now, complete the todo
    complete_response = client.post(
        "/api/chat/conversation",
        json={
            "message": "Mark 'Complete this task' as complete",
            "conversationId": create_data["conversationId"]
        }
    )
    
    assert complete_response.status_code == 200
    complete_data = complete_response.json()
    
    assert complete_data["action"] == "todo_completed"
    assert "Complete this task" in complete_data["response"]
    assert complete_data["todo"]["status"] == "completed"


def test_chatbot_delete_todo(client: TestClient):
    """Test deleting a todo through the chatbot interface"""
    # First, create a todo
    create_response = client.post(
        "/api/chat/conversation",
        json={"message": "Add a todo: Delete this task"}
    )
    
    assert create_response.status_code == 200
    create_data = create_response.json()
    assert create_data["action"] == "todo_created"
    
    # Now, delete the todo
    delete_response = client.post(
        "/api/chat/conversation",
        json={
            "message": "Delete 'Delete this task'",
            "conversationId": create_data["conversationId"]
        }
    )
    
    assert delete_response.status_code == 200
    delete_data = delete_response.json()
    
    assert delete_data["action"] == "todo_deleted"
    assert "Delete this task" in delete_data["response"]


def test_chatbot_show_todos(client: TestClient):
    """Test showing todos through the chatbot interface"""
    # First, create a few todos
    client.post("/api/chat/conversation", json={"message": "Add a todo: First task"})
    client.post("/api/chat/conversation", json={"message": "Add a todo: Second task"})
    
    # Now, ask to show todos
    response = client.post(
        "/api/chat/conversation",
        json={"message": "Show my todos"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["action"] == "show_todos"
    assert "First task" in data["response"]
    assert "Second task" in data["response"]


def test_chatbot_conversation_persistence(client: TestClient):
    """Test that conversation context is maintained"""
    # Start a conversation
    first_response = client.post(
        "/api/chat/conversation",
        json={"message": "Add a todo: Remember this conversation"}
    )
    
    assert first_response.status_code == 200
    first_data = first_response.json()
    conversation_id = first_data["conversationId"]
    assert conversation_id is not None
    
    # Continue the conversation
    second_response = client.post(
        "/api/chat/conversation",
        json={
            "message": "Show my todos",
            "conversationId": conversation_id
        }
    )
    
    assert second_response.status_code == 200
    second_data = second_response.json()
    
    # Verify we're in the same conversation
    assert second_data["conversationId"] == conversation_id
    assert "Remember this conversation" in second_data["response"]


def test_chatbot_error_handling(client: TestClient):
    """Test chatbot error handling for invalid commands"""
    response = client.post(
        "/api/chat/conversation",
        json={"message": "Invalid command that should return an error"}
    )
    
    assert response.status_code == 200  # Should still return 200, but with error response
    data = response.json()
    
    # The action might be unknown_command or clarification_needed
    assert data["action"] in ["unknown_command", "clarification_needed"]
    # The response should indicate the chatbot didn't understand
    assert "not sure" in data["response"].lower() or "help" in data["response"].lower()


if __name__ == "__main__":
    pytest.main([__file__])