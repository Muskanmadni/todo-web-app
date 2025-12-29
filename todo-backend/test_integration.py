import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app, SQLModel
from sqlmodel import Session, select, create_engine
from datetime import datetime
from uuid import UUID
import uuid

# Set test database URL to SQLite for testing
test_db_url = "sqlite:///./test.db"

# Mock the database URL before importing main app components
with patch.dict(os.environ, {"DATABASE_URL": test_db_url}):
    # Create a test-specific engine
    test_engine = create_engine(test_db_url)

    from main import User, Task, get_password_hash

# Create a test client
client = TestClient(app)

@pytest.fixture(scope="function")
def setup_and_teardown_db():
    """Set up and tear down the test database for each test function"""
    # Create tables
    SQLModel.metadata.create_all(bind=test_engine)

    yield  # This is where the test runs

    # Clean up after test
    SQLModel.metadata.drop_all(bind=test_engine)

def test_register_user(setup_and_teardown_db):
    """Test user registration endpoint"""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "test@example.com"
    assert "created_at" in data

def test_register_duplicate_email(setup_and_teardown_db):
    """Test that registering with duplicate email fails"""
    # Register first user
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    # Try to register with same email
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 409

def test_login_user(setup_and_teardown_db):
    """Test user login endpoint"""
    # Register a user first
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    # Login with the user
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(setup_and_teardown_db):
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_create_task(setup_and_teardown_db):
    """Test creating a task after authentication"""
    # Register and login a user
    register_response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    user_id = register_response.json()["id"]
    
    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Create a task
    response = client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "priority": "medium"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["priority"] == "medium"
    assert data["user_id"] == user_id
    assert data["completed"] is False

def test_get_tasks(setup_and_teardown_db):
    """Test retrieving tasks for authenticated user"""
    # Register and login a user
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Create a task
    client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "priority": "medium"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Get tasks
    response = client.get("/tasks", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Test Task"

def test_update_task(setup_and_teardown_db):
    """Test updating a task"""
    # Register and login a user
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Create a task
    create_response = client.post(
        "/tasks",
        json={
            "title": "Original Task",
            "priority": "medium"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]
    
    # Update the task
    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated Task",
            "completed": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["completed"] is True

def test_delete_task(setup_and_teardown_db):
    """Test deleting a task"""
    # Register and login a user
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Create a task
    create_response = client.post(
        "/tasks",
        json={
            "title": "Task to Delete",
            "priority": "medium"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]
    
    # Delete the task
    response = client.delete(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204
    
    # Verify the task is deleted
    get_response = client.get(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_response.status_code == 404

def test_unauthorized_access(setup_and_teardown_db):
    """Test that unauthorized access is prevented"""
    # Try to access tasks endpoint without token
    response = client.get("/tasks")
    assert response.status_code == 401
    
    # Try to create a task without token
    response = client.post("/tasks", json={"title": "Test"})
    assert response.status_code == 401

def test_cross_user_data_isolation(setup_and_teardown_db):
    """Test that users can't access each other's tasks"""
    # Register first user
    client.post(
        "/auth/register",
        json={
            "email": "user1@example.com",
            "password": "password123"
        }
    )
    user1_login = client.post(
        "/auth/login",
        json={
            "email": "user1@example.com",
            "password": "password123"
        }
    )
    token1 = user1_login.json()["access_token"]
    
    # Register second user
    client.post(
        "/auth/register",
        json={
            "email": "user2@example.com",
            "password": "password123"
        }
    )
    user2_login = client.post(
        "/auth/login",
        json={
            "email": "user2@example.com",
            "password": "password123"
        }
    )
    token2 = user2_login.json()["access_token"]
    
    # User 1 creates a task
    create_response = client.post(
        "/tasks",
        json={
            "title": "User 1's Task",
            "priority": "medium"
        },
        headers={"Authorization": f"Bearer {token1}"}
    )
    task_id = create_response.json()["id"]
    
    # User 2 tries to access User 1's task
    response = client.get(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 404  # Should not find the task
    
    # User 2 tries to update User 1's task
    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated by User 2"},
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 404  # Should not find the task
    
    # User 2 tries to delete User 1's task
    response = client.delete(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 404  # Should not find the task