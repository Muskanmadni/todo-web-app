"""
Recurrence pattern model for defining recurring task patterns.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime
import sqlalchemy
from enum import Enum


class RecurrenceFrequency(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class RecurrencePattern(SQLModel, table=True):
    __tablename__ = "recurrence_patterns"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    frequency: RecurrenceFrequency = Field(sa_column=Column(String, nullable=False))
    interval: int = Field(default=1, sa_column=Column(sqlalchemy.Integer, nullable=False))
    end_condition_type: Optional[str] = Field(default=None, sa_column=Column(String))  # after_occurrences, on_date
    end_condition_value: Optional[str] = Field(default=None, sa_column=Column(String))  # value for the end condition
    days_of_week: Optional[List[str]] = Field(default=None, sa_column=Column(sqlalchemy.ARRAY(String)))  # For weekly recurrences
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, nullable=False))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, nullable=False))