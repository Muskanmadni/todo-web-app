from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid
from .user import User


class TodoBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    status: str = Field(default="pending", regex="^(pending|in_progress|completed|cancelled)$")
    due_date: Optional[datetime] = Field(default=None)
    priority: str = Field(default="medium", regex="^(low|medium|high|urgent)$")
    user_id: uuid.UUID = Field(foreign_key="user.id")


class Todo(TodoBase, table=True):
    """
    Represents a todo/task in the system
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to User
    user: User = Relationship(back_populates="todos")


# Link the relationship back to User model
User.todos = Relationship(back_populates="user")