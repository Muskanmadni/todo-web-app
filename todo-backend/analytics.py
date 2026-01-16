"""
Analytics and Monitoring for Chatbot Usage
"""
import logging
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel
from enum import Enum


class EventType(str, Enum):
    CHAT_REQUEST = "chat_request"
    CHAT_RESPONSE = "chat_response"
    TODO_CREATED = "todo_created"
    TODO_UPDATED = "todo_updated"
    TODO_DELETED = "todo_deleted"
    TODO_COMPLETED = "todo_completed"
    TODO_PENDING = "todo_pending"
    ERROR_OCCURRED = "error_occurred"


class AnalyticsEvent(BaseModel):
    event_type: EventType
    user_id: str
    conversation_id: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}


class AnalyticsService:
    """
    Service for tracking analytics and monitoring chatbot usage
    """
    def __init__(self):
        # Set up logging for analytics
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def track_event(self, event: AnalyticsEvent):
        """
        Track an analytics event
        """
        self.logger.info(f"Analytics Event: {event.event_type.value} - User: {event.user_id} - Conversation: {event.conversation_id}")
        # In a production system, you would send this to a metrics database like InfluxDB, 
        # or an analytics service like Segment, or a message queue like Kafka
        
        # For now, we're just logging the events
        print(f"Analytics Event: {event.dict()}")
        
    def track_chat_request(self, user_id: str, conversation_id: str, message: str):
        """
        Track when a user sends a message to the chatbot
        """
        event = AnalyticsEvent(
            event_type=EventType.CHAT_REQUEST,
            user_id=user_id,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow(),
            metadata={"message": message}
        )
        self.track_event(event)
        
    def track_chat_response(self, user_id: str, conversation_id: str, response: str, action: str):
        """
        Track when the chatbot responds to a user
        """
        event = AnalyticsEvent(
            event_type=EventType.CHAT_RESPONSE,
            user_id=user_id,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow(),
            metadata={"response": response, "action": action}
        )
        self.track_event(event)
        
    def track_todo_operation(self, operation: str, user_id: str, conversation_id: str, todo_data: Dict[str, Any]):
        """
        Track when a todo operation occurs
        """
        event_type_map = {
            "create": EventType.TODO_CREATED,
            "update": EventType.TODO_UPDATED,
            "delete": EventType.TODO_DELETED,
            "completed": EventType.TODO_COMPLETED,
            "pending": EventType.TODO_PENDING
        }
        
        event_type = event_type_map.get(operation, EventType.TODO_CREATED)
        
        event = AnalyticsEvent(
            event_type=event_type,
            user_id=user_id,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow(),
            metadata=todo_data
        )
        self.track_event(event)
        
    def track_error(self, user_id: str, conversation_id: str, error_message: str, error_type: str):
        """
        Track when an error occurs
        """
        event = AnalyticsEvent(
            event_type=EventType.ERROR_OCCURRED,
            user_id=user_id,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow(),
            metadata={"error_message": error_message, "error_type": error_type}
        )
        self.track_event(event)


# Global instance of the analytics service
analytics_service = AnalyticsService()