from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime
try:
    from ..models.conversation import Conversation
except (ImportError, ValueError):
    # Fallback for when module is run directly
    from models.conversation import Conversation


class ConversationService:
    @staticmethod
    def create_conversation(session: Session, title: str, user_id: UUID) -> Conversation:
        """
        Creates a new conversation for a user
        """
        conversation = Conversation(
            title=title,
            user_id=user_id
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation_by_id(session: Session, conversation_id: UUID) -> Optional[Conversation]:
        """
        Retrieves a specific conversation by its ID
        """
        return session.get(Conversation, conversation_id)

    @staticmethod
    def get_conversations_by_user(session: Session, user_id: UUID) -> List[Conversation]:
        """
        Retrieves all conversations for a specific user
        """
        query = select(Conversation).where(Conversation.user_id == user_id)
        return session.exec(query).all()

    @staticmethod
    def update_conversation(session: Session, conversation_id: UUID, title: Optional[str] = None) -> Optional[Conversation]:
        """
        Updates an existing conversation with new values
        """
        conversation = session.get(Conversation, conversation_id)
        
        if not conversation:
            return None
            
        if title is not None:
            conversation.title = title
            
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    @staticmethod
    def delete_conversation(session: Session, conversation_id: UUID) -> bool:
        """
        Deletes a conversation by its ID
        """
        conversation = session.get(Conversation, conversation_id)
        
        if not conversation:
            return False
            
        session.delete(conversation)
        session.commit()
        return True