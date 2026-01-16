"""
Test script to verify the Gemini AI chatbot functionality
"""
import asyncio
from api.chatbot import process_natural_language_command
from sqlmodel import create_engine, Session
from models.todo import Todo
from models.conversation import Conversation
from uuid import UUID


def test_gemini_chatbot():
    """
    Test the Gemini AI integration with the chatbot
    """
    print("Testing Gemini AI Chatbot Integration...")
    
    # Create a mock session for testing
    engine = create_engine("sqlite:///:memory:")
    with Session(engine) as session:
        # Create a mock conversation ID
        conversation_id = UUID("12345678-1234-5678-1234-567812345678")
        
        # Test adding a todo
        print("\n1. Testing 'Add a todo' command...")
        response, action, todo_data = process_natural_language_command(
            message="Add a todo: Buy groceries",
            session=session,
            conversation_id=conversation_id
        )
        print(f"Response: {response}")
        print(f"Action: {action}")
        print(f"Todo Data: {todo_data}")
        
        # Test completing a todo
        print("\n2. Testing 'Complete a todo' command...")
        response, action, todo_data = process_natural_language_command(
            message="Complete 'Buy groceries'",
            session=session,
            conversation_id=conversation_id
        )
        print(f"Response: {response}")
        print(f"Action: {action}")
        print(f"Todo Data: {todo_data}")
        
        # Test listing todos
        print("\n3. Testing 'Show todos' command...")
        response, action, todo_data = process_natural_language_command(
            message="Show my todos",
            session=session,
            conversation_id=conversation_id
        )
        print(f"Response: {response}")
        print(f"Action: {action}")
        print(f"Todo Data: {todo_data}")
        
        # Test an unknown command
        print("\n4. Testing 'Unknown command'...")
        response, action, todo_data = process_natural_language_command(
            message="What is the weather today?",
            session=session,
            conversation_id=conversation_id
        )
        print(f"Response: {response}")
        print(f"Action: {action}")
        print(f"Todo Data: {todo_data}")
    
    print("\nTest completed!")


if __name__ == "__main__":
    test_gemini_chatbot()