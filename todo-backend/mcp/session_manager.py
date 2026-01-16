"""
Conversation session management for maintaining context between sessions.
"""
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from todo_backend.services.conversation_service import ConversationService
from todo_backend.services.message_service import MessageService
from todo_backend.database import get_session
from sqlmodel import Session


class ConversationSessionManager:
    """
    Manages conversation sessions to maintain context between user interactions.
    """
    
    @staticmethod
    def get_active_conversation(user_id: str, max_inactive_minutes: int = 30) -> Optional[Dict[str, Any]]:
        """
        Retrieves the most recent active conversation for a user, if it's still active.
        
        Args:
            user_id: The ID of the user
            max_inactive_minutes: Maximum minutes of inactivity before a conversation is considered inactive
        
        Returns:
            Dictionary with conversation info if an active conversation exists, None otherwise
        """
        with next(get_session()) as session:
            # Get the most recent conversation for the user
            conversations = ConversationService.get_conversations_by_user(session, UUID(user_id))
            
            if not conversations:
                return None
            
            # Sort by updated_at to get the most recent
            conversations.sort(key=lambda x: x.updated_at, reverse=True)
            latest_conversation = conversations[0]
            
            # Check if the conversation is still active (not too old)
            time_since_update = datetime.utcnow() - latest_conversation.updated_at
            if time_since_update < timedelta(minutes=max_inactive_minutes):
                # Get the messages for this conversation
                messages = MessageService.get_messages_by_conversation(session, latest_conversation.id)
                
                return {
                    "id": str(latest_conversation.id),
                    "title": latest_conversation.title,
                    "updated_at": latest_conversation.updated_at,
                    "messages": messages
                }
            
            return None
    
    @staticmethod
    def create_new_conversation(user_id: str, initial_message: str) -> Dict[str, Any]:
        """
        Creates a new conversation for a user.
        
        Args:
            user_id: The ID of the user
            initial_message: The initial message to start the conversation
        
        Returns:
            Dictionary with new conversation info
        """
        with next(get_session()) as session:
            conversation = ConversationService.create_conversation(
                session=session,
                title=initial_message[:50] + "..." if len(initial_message) > 50 else initial_message,
                user_id=UUID(user_id)
            )
            
            return {
                "id": str(conversation.id),
                "title": conversation.title,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at
            }
    
    @staticmethod
    def archive_old_conversations(user_id: str, max_age_days: int = 30) -> int:
        """
        Archives conversations that are older than the specified age.
        
        Args:
            user_id: The ID of the user
            max_age_days: Maximum age in days before a conversation is archived
        
        Returns:
            Number of conversations archived
        """
        # In a real implementation, this would update conversations to an archived state
        # For now, we'll just return 0 as a placeholder
        return 0