from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from ..models.conversation import Conversation, ConversationBase
from ..models.message import Message


class ConversationService:
    """
    Service class for handling conversation operations
    """
    
    @staticmethod
    def create_conversation(session: Session, user_id: UUID, context_data: Optional[dict] = None) -> Conversation:
        """
        Create a new conversation for a user
        """
        if context_data is None:
            context_data = {}
        
        conversation = Conversation(
            user_id=user_id,
            context_data=context_data
        )
        
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        return conversation
    
    @staticmethod
    def get_conversation_by_id(session: Session, conversation_id: UUID, user_id: UUID) -> Optional[Conversation]:
        """
        Get a specific conversation by ID for a user
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id, 
            Conversation.user_id == user_id
        )
        conversation = session.exec(statement).first()
        return conversation
    
    @staticmethod
    def update_conversation_context(session: Session, conversation_id: UUID, user_id: UUID, context_data: dict) -> Optional[Conversation]:
        """
        Update the context data for a conversation
        """
        conversation = ConversationService.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return None

        conversation.context_data = context_data
        conversation.last_interaction_at = datetime.utcnow()

        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        return conversation

    @staticmethod
    def get_conversation_context(session: Session, conversation_id: UUID, user_id: UUID) -> Optional[dict]:
        """
        Get the context data for a conversation
        """
        conversation = ConversationService.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return None

        return conversation.context_data

    @staticmethod
    def update_conversation_context_with_new_data(session: Session, conversation_id: UUID, user_id: UUID,
                                               new_context_data: dict) -> Optional[Conversation]:
        """
        Update the context data for a conversation by merging with existing data
        """
        conversation = ConversationService.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return None

        # Merge new context data with existing data
        if conversation.context_data:
            conversation.context_data.update(new_context_data)
        else:
            conversation.context_data = new_context_data

        conversation.last_interaction_at = datetime.utcnow()

        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        return conversation
    
    @staticmethod
    def add_message_to_conversation(session: Session, conversation_id: UUID, user_id: UUID, 
                                   sender_type: str, content: str) -> Optional[Message]:
        """
        Add a message to a conversation
        """
        conversation = ConversationService.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return None
        
        message = Message(
            conversation_id=conversation_id,
            sender_type=sender_type,
            content=content
        )
        
        session.add(message)
        session.commit()
        session.refresh(message)
        
        # Update conversation's last interaction time
        conversation.last_interaction_at = conversation.last_interaction_at.now()
        session.add(conversation)
        session.commit()
        
        return message
    
    @staticmethod
    def get_messages_for_conversation(session: Session, conversation_id: UUID, user_id: UUID) -> List[Message]:
        """
        Get all messages for a specific conversation
        """
        # First verify the conversation belongs to the user
        conversation = ConversationService.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return []
        
        statement = select(Message).where(Message.conversation_id == conversation_id)
        messages = session.exec(statement).all()
        return messages