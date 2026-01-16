from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime
try:
    from ..models.message import Message
except (ImportError, ValueError):
    # Fallback for when module is run directly
    from models.message import Message


class MessageService:
    @staticmethod
    def create_message(
        session: Session,
        conversation_id: UUID,
        role: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> Message:
        """
        Creates a new message in a conversation
        """
        # Convert metadata dict to JSON string
        metadata_str = None
        if metadata:
            import json
            metadata_str = json.dumps(metadata)

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata_json=metadata_str
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        return message

    @staticmethod
    def get_message_by_id(session: Session, message_id: UUID) -> Optional[Message]:
        """
        Retrieves a specific message by its ID
        """
        return session.get(Message, message_id)

    @staticmethod
    def get_messages_by_conversation(session: Session, conversation_id: UUID) -> List[Message]:
        """
        Retrieves all messages in a specific conversation
        """
        query = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.timestamp)
        return session.exec(query).all()

    @staticmethod
    def update_message(
        session: Session,
        message_id: UUID,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Optional[Message]:
        """
        Updates an existing message with new values
        """
        message = session.get(Message, message_id)

        if not message:
            return None

        if content is not None:
            message.content = content
        if metadata is not None:
            import json
            message.metadata_json = json.dumps(metadata)

        session.add(message)
        session.commit()
        session.refresh(message)
        return message

    @staticmethod
    def delete_message(session: Session, message_id: UUID) -> bool:
        """
        Deletes a message by its ID
        """
        message = session.get(Message, message_id)
        
        if not message:
            return False
            
        session.delete(message)
        session.commit()
        return True