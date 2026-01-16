from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String
import sqlalchemy


class Todo(SQLModel, table=True):
    __tablename__ = "todos"  # Use a different table name to avoid conflict

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(sa_column=Column(String, nullable=False))
    description: Optional[str] = Field(default=None)
    status: str = Field(default="pending", sa_column=Column(String, nullable=False))  # pending, completed
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship(back_populates="todos")