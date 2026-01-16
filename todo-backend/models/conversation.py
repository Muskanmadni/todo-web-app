from sqlmodel import SQLModel, Field, Relationship
from typing import List
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String
import sqlalchemy


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"  # Standardize table name

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)  # Changed to match main.py table name
    title: str = Field(sa_column=Column(String, nullable=False))  # Auto-generated from first message or summary
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")