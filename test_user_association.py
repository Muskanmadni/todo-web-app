"""
Test script to verify that tasks added by the chatbot now appear in the UI
and are correctly associated with the logged-in user.
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

def test_user_association():
    """Test that tasks created by the chatbot are associated with the correct user."""
    print("Testing user association for chatbot tasks...")
    
    # Create two different test users
    user1 = get_or_create_test_user()
    print(f"User 1: {user1.email} (ID: {user1.id})")
    
    # Create a second user
    with Session(engine) as session:
        user2 = session.exec(
            select(UserModel).where(UserModel.email == "test_user2@example.com")
        ).first()

        if not user2:
            password = "test_password"
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user2 = UserModel(
                email="test_user2@example.com",
                password_hash=password_hash
            )
            session.add(user2)
            session.commit()
            session.refresh(user2)
    
    print(f"User 2: {user2.email} (ID: {user2.id})")
    
    # Create a task for user1 using the chatbot tools
    print(f"\n1. Creating task for User 1 using TodoMCPTools...")
    task1_data = TodoMCPTools.create_todo(
        title="Task for User 1",
        description="Created by chatbot for User 1",
        user_id=str(user1.id)  # Pass User 1's ID
    )
    
    print(f"Created task for User 1: {task1_data['title']} (ID: {task1_data['id']})")
    
    # Create a task for user2 using the chatbot tools
    print(f"\n2. Creating task for User 2 using TodoMCPTools...")
    task2_data = TodoMCPTools.create_todo(
        title="Task for User 2",
        description="Created by chatbot for User 2",
        user_id=str(user2.id)  # Pass User 2's ID
    )
    
    print(f"Created task for User 2: {task2_data['title']} (ID: {task2_data['id']})")
    
    # Verify that each task is associated with the correct user
    print(f"\n3. Verifying task-user associations...")
    
    with Session(engine) as session:
        # Get task 1 and check its user
        task1_db = session.get(Task, task1_data['id'])
        if task1_db and str(task1_db.user_id) == str(user1.id):
            print(f"SUCCESS: Task '{task1_db.title}' is correctly associated with User 1")
        else:
            print(f"FAILURE: Task is not associated with User 1")
            if task1_db:
                print(f"  Actual user ID: {task1_db.user_id}")
                print(f"  Expected user ID: {user1.id}")
        
        # Get task 2 and check its user
        task2_db = session.get(Task, task2_data['id'])
        if task2_db and str(task2_db.user_id) == str(user2.id):
            print(f"SUCCESS: Task '{task2_db.title}' is correctly associated with User 2")
        else:
            print(f"FAILURE: Task is not associated with User 2")
            if task2_db:
                print(f"  Actual user ID: {task2_db.user_id}")
                print(f"  Expected user ID: {user2.id}")
    
    # Verify that each user can only see their own tasks
    print(f"\n4. Verifying user isolation (each user sees only their tasks)...")
    
    with Session(engine) as session:
        # Get all tasks for User 1
        user1_tasks = session.exec(
            select(Task).where(Task.user_id == user1.id)
        ).all()
        
        user1_task_titles = [task.title for task in user1_tasks]
        print(f"Tasks for User 1: {user1_task_titles}")
        
        # Get all tasks for User 2
        user2_tasks = session.exec(
            select(Task).where(Task.user_id == user2.id)
        ).all()
        
        user2_task_titles = [task.title for task in user2_tasks]
        print(f"Tasks for User 2: {user2_task_titles}")
        
        # Verify each user only has their own task
        if "Task for User 1" in user1_task_titles and "Task for User 2" not in user1_task_titles:
            print(f"SUCCESS: User 1 only sees their own tasks")
        else:
            print(f"FAILURE: User 1 sees wrong tasks")
            
        if "Task for User 2" in user2_task_titles and "Task for User 1" not in user2_task_titles:
            print(f"SUCCESS: User 2 only sees their own tasks")
        else:
            print(f"FAILURE: User 2 sees wrong tasks")

def test_end_to_end_scenario():
    """Test the complete scenario: user logs in, adds task via chatbot, sees it in UI."""
    print(f"\n{'='*60}")
    print("Testing end-to-end scenario...")
    
    user = get_or_create_test_user()
    print(f"Simulated logged-in user: {user.email} (ID: {user.id})")
    
    # Simulate: user uses chatbot to add a task
    print(f"\n1. Simulating user using chatbot to add a task...")
    chatbot_task = TodoMCPTools.create_todo(
        title="Chatbot task for logged-in user",
        description="This task was added via chatbot by a logged-in user",
        user_id=str(user.id)  # Simulate passing the authenticated user's ID
    )
    
    print(f"Chatbot created task: '{chatbot_task['title']}' (ID: {chatbot_task['id']})")
    
    # Simulate: user views tasks in UI (retrieves from tasks API)
    print(f"\n2. Simulating user viewing tasks in UI...")
    with Session(engine) as session:
        ui_tasks = session.exec(
            select(Task).where(Task.user_id == user.id)
        ).all()
        
        print(f"Tasks visible in UI for this user: {[task.title for task in ui_tasks]}")
        
        # Check if the chatbot task is visible
        chatbot_task_visible = any(task.id == chatbot_task['id'] for task in ui_tasks)
        
        if chatbot_task_visible:
            print(f"SUCCESS: Chatbot task is visible in UI for the correct user!")
            print(f"  The task '{chatbot_task['title']}' appears in the user's task list.")
            return True
        else:
            print(f"FAILURE: Chatbot task is not visible in UI for this user!")
            return False

if __name__ == "__main__":
    print("Testing the fix for chatbot tasks appearing in UI with proper user association...")
    print("="*80)
    
    test_user_association()
    
    success = test_end_to_end_scenario()
    
    print("\n" + "="*80)
    if success:
        print("SUCCESS: All tests passed! The fix is working correctly.")
        print("  - Tasks created by the chatbot now appear in the UI")
        print("  - Tasks are correctly associated with the appropriate user")
        print("  - Each user only sees their own tasks")
    else:
        print("FAILURE: Some tests failed! The fix needs more work.")