from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String
import sqlalchemy


class User(SQLModel, table=True):
    __tablename__ = "users"  # Match the table name in main.py

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(sa_column=Column(String, unique=True, index=True, nullable=False))
    password_hash: str = Field(sa_column=Column(String, nullable=False))  # Added to match main.py
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    todos: List["Todo"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")