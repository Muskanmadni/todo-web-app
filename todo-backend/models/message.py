from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Text
import sqlalchemy
import json


class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False)  # Changed to match table name
    role: str = Field(sa_column=Column(String, nullable=False))  # user, assistant, system
    content: str = Field(sa_column=Column(Text, nullable=False))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata_json: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))  # Store additional data like AI tokens used, etc. as JSON string
    context_references: Optional[str] = Field(sa_column=Column(Text, nullable=True))  # Store references to previous messages/todos

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")