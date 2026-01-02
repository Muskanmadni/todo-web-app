from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid
from typing import Optional


class MessageBase(SQLModel):
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    sender_type: str = Field(regex="^(user|ai)$")
    content: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Message(MessageBase, table=True):
    """
    Represents a message in a conversation
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to Conversation
    conversation: "Conversation" = Relationship(back_populates="messages")