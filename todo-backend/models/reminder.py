"""
Reminder model for storing task reminder information.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime
import sqlalchemy
from enum import Enum


class ReminderStatus(str, Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"


class Reminder(SQLModel, table=True):
    __tablename__ = "reminders"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="todos.id", nullable=False)
    scheduled_time: datetime = Field(sa_column=Column(DateTime, nullable=False))
    sent_status: ReminderStatus = Field(default=ReminderStatus.pending, sa_column=Column(String, nullable=False))
    delivery_attempts: int = Field(default=0, sa_column=Column(sqlalchemy.Integer, nullable=False))
    last_attempt_time: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, nullable=False))

    # Relationships
    task: "Todo" = Relationship(back_populates="reminders")