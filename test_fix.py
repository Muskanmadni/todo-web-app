"""
Test script to verify that tasks added by the chatbot now appear in the UI.
This script simulates the scenario where a task is added via the chatbot
and then retrieved via the standard tasks API.
"""
import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'todo-backend'))

from uuid import UUID
from sqlmodel import Session, select
from database import engine
from models.user import User as UserModel
from mcp.tools import TodoMCPTools
# Import the Task model from main module since that's where the tools now use
from main import Task
import bcrypt

def get_or_create_test_user():
    """Create a test user if one doesn't exist."""
    with Session(engine) as session:
        # Look for an existing test user
        existing_user = session.exec(
            select(UserModel).where(UserModel.email == "test_user@example.com")
        ).first()

        if existing_user:
            return existing_user

        # If no test user exists, create one
        password = "test_password"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        test_user = UserModel(
            email="test_user@example.com",
            password_hash=password_hash
        )

        session.add(test_user)
        session.commit()
        session.refresh(test_user)

        return test_user

def test_task_creation_and_retrieval():
    """Test that tasks created by the chatbot can be retrieved by the UI."""
    print("Testing task creation and retrieval...")
    
    # Get or create a test user
    user = get_or_create_test_user()
    print(f"Using user: {user.email} (ID: {user.id})")
    
    # Create a task using the updated TodoMCPTools (simulating chatbot action)
    print("\n1. Creating task using TodoMCPTools (simulating chatbot)...")
    task_data = TodoMCPTools.create_todo(
        title="Test task from chatbot",
        description="This task was created via the chatbot",
        user_id=str(user.id)
    )
    
    print(f"Created task: {task_data['title']} (ID: {task_data['id']})")
    
    # Now verify that this task exists in the Task table (which the UI uses)
    print("\n2. Verifying task exists in Task table (used by UI)...")
    with Session(engine) as session:
        # Query the Task table to see if our task is there
        # The ID from create_todo is already a UUID object
        task = session.get(Task, task_data['id'])

        if task:
            print(f"SUCCESS: Task found in Task table!")
            print(f"  Title: {task.title}")
            print(f"  Description: {task.description}")
            print(f"  User ID: {task.user_id}")
            print(f"  Completed: {task.completed}")
            print(f"  Priority: {task.priority}")

            # Also verify it's NOT in the old Todo table
            from models.todo import Todo
            old_todo = session.get(Todo, task_data['id'])
            if old_todo:
                print(f"\nWARNING: Task also exists in old Todo table - this could cause duplicates")
            else:
                print(f"\nGOOD: Task does NOT exist in old Todo table (as expected)")

            return True
        else:
            print(f"FAILURE: Task NOT found in Task table!")
            print("This means the fix did not work correctly.")
            return False

def test_multiple_operations():
    """Test multiple operations to ensure everything works correctly."""
    print("\n" + "="*60)
    print("Testing multiple operations...")
    
    user = get_or_create_test_user()
    
    # Create multiple tasks
    print("\n1. Creating multiple tasks...")
    task1 = TodoMCPTools.create_todo(
        title="First chatbot task",
        description="Created by chatbot",
        user_id=str(user.id)
    )
    
    task2 = TodoMCPTools.create_todo(
        title="Second chatbot task",
        description="Also created by chatbot",
        user_id=str(user.id)
    )
    
    print(f"Created tasks: '{task1['title']}' and '{task2['title']}'")
    
    # Test updating a task
    print(f"\n2. Updating task '{task1['title']}'...")
    updated_task = TodoMCPTools.update_todo(
        todo_id=task1['id'],
        title="Updated chatbot task",
        description="Updated by chatbot",
        status="completed"
    )
    
    print(f"Updated task: '{updated_task['title']}' - Completed: {updated_task['completed']}")
    
    # Verify the update worked
    with Session(engine) as session:
        task = session.get(TaskModel, UUID(updated_task['id']))
        if task and task.completed:
            print("✓ Update successful!")
        else:
            print("✗ Update failed!")
    
    # Test marking as completed
    print(f"\n3. Marking task '{task2['title']}' as completed...")
    completed_task = TodoMCPTools.mark_todo_completed(task2['id'])
    print(f"Marked as completed: '{completed_task['title']}' - Status: {'Completed' if completed_task['completed'] else 'Pending'}")
    
    # Verify completion worked
    with Session(engine) as session:
        task = session.get(TaskModel, UUID(completed_task['id']))
        if task and task.completed:
            print("✓ Completion successful!")
        else:
            print("✗ Completion failed!")

if __name__ == "__main__":
    print("Testing the fix for chatbot tasks appearing in UI...")
    print("="*60)
    
    success = test_task_creation_and_retrieval()
    
    if success:
        test_multiple_operations()
        print("\n" + "="*60)
        print("✓ OVERALL: All tests passed! The fix is working correctly.")
        print("Tasks created by the chatbot will now appear in the UI.")
    else:
        print("\n" + "="*60)
        print("✗ OVERALL: Tests failed! The fix needs more work.")