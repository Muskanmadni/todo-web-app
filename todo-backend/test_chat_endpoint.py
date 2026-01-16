import requests
import json

def test_chat_endpoint():
    """
    Test the chat endpoint to ensure it's accessible at /chat/conversation
    """
    url = "http://localhost:8000/chat/conversation"
    
    # Sample request data
    data = {
        "message": "add todo buy groceries",
        "conversationId": None,
        "metadata": {}
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n✓ SUCCESS: The chat endpoint is working correctly!")
            return True
        else:
            print(f"\n✗ ERROR: Expected status 200, got {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Cannot connect to the server. Make sure the FastAPI app is running on localhost:8000")
        return False
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing the chat endpoint...")
    test_chat_endpoint()