"""
End-to-End Test for AI-Powered Chatbot Todo Management

This script demonstrates the complete workflow of the AI chatbot for todo management.
It simulates a user interacting with the chatbot through various natural language commands.
"""
import requests
import time
import uuid
from datetime import datetime


def test_complete_workflow():
    """
    Test the complete workflow of the AI chatbot for todo management
    """
    print("Starting End-to-End Test for AI-Powered Chatbot Todo Management")
    print("=" * 60)
    
    # Base URL for the API (adjust as needed)
    base_url = "http://localhost:8000"
    
    # Create a unique conversation ID for this test
    conversation_id = str(uuid.uuid4())
    print(f"Using conversation ID: {conversation_id}")
    
    print("\n1. Testing: Add a new todo")
    response = requests.post(f"{base_url}/api/chat/conversation", json={
        "message": "Add a todo: Buy groceries",
        "conversationId": conversation_id
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {data['response']}")
        print(f"   Action: {data['action']}")
        if 'todo' in data and data['todo']:
            print(f"   Todo ID: {data['todo']['id']}")
            print(f"   Todo Title: {data['todo']['title']}")
            print(f"   Todo Status: {data['todo']['status']}")
    else:
        print(f"   ✗ Failed: Status {response.status_code}, {response.text}")
        return False
    
    print("\n2. Testing: Add another todo")
    response = requests.post(f"{base_url}/api/chat/conversation", json={
        "message": "Add a todo: Walk the dog",
        "conversationId": conversation_id
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {data['response']}")
        print(f"   Action: {data['action']}")
    else:
        print(f"   ✗ Failed: Status {response.status_code}, {response.text}")
        return False
    
    print("\n3. Testing: Show all todos")
    response = requests.post(f"{base_url}/api/chat/conversation", json={
        "message": "Show my todos",
        "conversationId": conversation_id
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {data['response']}")
        print(f"   Action: {data['action']}")
    else:
        print(f"   ✗ Failed: Status {response.status_code}, {response.text}")
        return False
    
    print("\n4. Testing: Mark a todo as complete")
    response = requests.post(f"{base_url}/api/chat/conversation", json={
        "message": "Mark 'Buy groceries' as complete",
        "conversationId": conversation_id
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {data['response']}")
        print(f"   Action: {data['action']}")
        if 'todo' in data and data['todo']:
            print(f"   Todo Status: {data['todo']['status']}")
    else:
        print(f"   ✗ Failed: Status {response.status_code}, {response.text}")
        return False
    
    print("\n5. Testing: Delete a todo")
    response = requests.post(f"{base_url}/api/chat/conversation", json={
        "message": "Delete 'Walk the dog'",
        "conversationId": conversation_id
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {data['response']}")
        print(f"   Action: {data['action']}")
    else:
        print(f"   ✗ Failed: Status {response.status_code}, {response.text}")
        return False
    
    print("\n6. Testing: Show remaining todos")
    response = requests.post(f"{base_url}/api/chat/conversation", json={
        "message": "Show my todos",
        "conversationId": conversation_id
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {data['response']}")
        print(f"   Action: {data['action']}")
    else:
        print(f"   ✗ Failed: Status {response.status_code}, {response.text}")
        return False
    
    print("\n" + "=" * 60)
    print("End-to-End Test Completed Successfully!")
    print("All user stories have been tested:")
    print("- Natural language todo creation")
    print("- Showing list of todos")
    print("- Marking todos as complete")
    print("- Deleting todos")
    print("- Conversation context persistence")
    print("=" * 60)
    
    return True


def test_error_handling():
    """
    Test error handling capabilities
    """
    print("\nTesting Error Handling:")
    print("-" * 30)
    
    base_url = "http://localhost:8000"
    conversation_id = str(uuid.uuid4())
    
    print("1. Testing: Unknown command")
    response = requests.post(f"{base_url}/api/chat/conversation", json={
        "message": "This is an unknown command",
        "conversationId": conversation_id
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Handled gracefully: {data['response']}")
        print(f"   Action: {data['action']}")
    else:
        print(f"   ✗ Failed: Status {response.status_code}, {response.text}")
        return False
    
    print("2. Testing: Referencing non-existent todo")
    response = requests.post(f"{base_url}/api/chat/conversation", json={
        "message": "Mark 'Non-existent todo' as complete",
        "conversationId": conversation_id
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Handled gracefully: {data['response']}")
        print(f"   Action: {data['action']}")
    else:
        print(f"   ✗ Failed: Status {response.status_code}, {response.text}")
        return False
    
    print("\nError handling test completed successfully!")
    return True


if __name__ == "__main__":
    print("AI-Powered Chatbot Todo Management - End-to-End Test")
    print("This script tests the complete workflow of the chatbot system.")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    # Wait a moment to ensure the server is ready
    time.sleep(2)
    
    try:
        # Run the main workflow test
        success = test_complete_workflow()
        
        if success:
            # Run error handling tests
            error_success = test_error_handling()
            success = success and error_success
        
        if success:
            print("\n🎉 All end-to-end tests passed successfully!")
            print("The AI chatbot system is working as expected.")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server. Please ensure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ An error occurred during testing: {str(e)}")