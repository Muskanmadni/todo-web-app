from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid
from typing import Optional, Dict, Any
from .user import User
from .message import Message
import json


class ConversationBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_interaction_at: datetime = Field(default_factory=datetime.utcnow)
    context_data: Optional[Dict[str, Any]] = Field(default=lambda: {})


class Conversation(ConversationBase, table=True):
    """
    Represents a conversation session between user and chatbot
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="conversations")
    messages: list[Message] = Relationship(back_populates="conversation")


# Link the relationship back to User model
User.conversations = Relationship(back_populates="user")