from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, Text
import sqlalchemy
from enum import Enum


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RecurrenceFrequency(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class Todo(SQLModel, table=True):
    __tablename__ = "todos"  # Use a different table name to avoid conflict

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(sa_column=Column(String, nullable=False))
    description: Optional[str] = Field(default=None)
    status: str = Field(default="pending", sa_column=Column(String, nullable=False))  # pending, completed
    priority: Priority = Field(default=Priority.medium)
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(sqlalchemy.JSON))  # Store as JSON
    due_date: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
    recurrence_pattern: Optional[str] = Field(default=None, sa_column=Column(Text))  # JSON string for recurrence pattern
    next_occurrence_date: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship(back_populates="todos")
    reminders: List["Reminder"] = Relationship(back_populates="task")