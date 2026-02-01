"""
Event model for storing system events.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, Text
import sqlalchemy
from enum import Enum


class EventStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    processed = "processed"
    failed = "failed"


class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    event_type: str = Field(sa_column=Column(String, nullable=False))
    payload: Dict[str, Any] = Field(sa_column=Column(sqlalchemy.JSON, nullable=False))
    source: str = Field(sa_column=Column(String, nullable=False))
    correlation_id: Optional[UUID] = Field(default=None, sa_column=Column(String))
    processed_status: EventStatus = Field(default=EventStatus.pending, sa_column=Column(String, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, nullable=False))
    processed_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))