import httpx
import json
from typing import Any, Dict, Optional
from database import settings  # Import the settings from database module


class DaprClient:
    """
    A wrapper class for interacting with Dapr sidecar.
    Provides methods for state management, pub/sub, secrets, and service invocation.
    """

    def __init__(self):
        self.base_url = f"http://localhost:{settings.dapr_sidecar_port}"
        self.headers = {"Content-Type": "application/json"}

    async def save_state(self, store_name: str, key: str, value: Any) -> bool:
        """
        Save state to Dapr state store.
        """
        url = f"{self.base_url}/v1.0/state/{store_name}"
        data = [{
            "key": key,
            "value": value
        }]
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=data, headers=self.headers)
                return response.status_code == 204
            except Exception as e:
                print(f"Error saving state: {e}")
                return False

    async def get_state(self, store_name: str, key: str) -> Optional[Any]:
        """
        Get state from Dapr state store.
        """
        url = f"{self.base_url}/v1.0/state/{store_name}/{key}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    print(f"Error getting state: {response.status_code}")
                    return None
            except Exception as e:
                print(f"Error getting state: {e}")
                return None

    async def publish_event(self, pubsub_name: str, topic_name: str, data: Any) -> bool:
        """
        Publish an event to a Dapr pub/sub topic.
        """
        url = f"{self.base_url}/v1.0/publish/{pubsub_name}/{topic_name}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=data, headers=self.headers)
                return response.status_code == 200
            except Exception as e:
                print(f"Error publishing event: {e}")
                return False

    async def get_secret(self, store_name: str, key: str) -> Optional[str]:
        """
        Get a secret from Dapr secret store.
        """
        url = f"{self.base_url}/v1.0/secrets/{store_name}/{key}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    secret_data = response.json()
                    # Return the actual secret value (Dapr returns it in a dict with the key as the secret name)
                    return secret_data.get(key)
                else:
                    print(f"Error getting secret: {response.status_code}")
                    return None
            except Exception as e:
                print(f"Error getting secret: {e}")
                return None

    async def invoke_service(self, app_id: str, method: str, data: Optional[Any] = None) -> Optional[Any]:
        """
        Invoke a method on another service via Dapr.
        """
        url = f"{self.base_url}/v1.0/invoke/{app_id}/method/{method}"
        
        async with httpx.AsyncClient() as client:
            try:
                if data:
                    response = await client.post(url, json=data, headers=self.headers)
                else:
                    response = await client.post(url, headers=self.headers)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Error invoking service: {response.status_code}")
                    return None
            except Exception as e:
                print(f"Error invoking service: {e}")
                return None


# Global instance
dapr_client = DaprClient()