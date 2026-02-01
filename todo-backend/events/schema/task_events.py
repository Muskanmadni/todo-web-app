"""
Event schemas for task-related events in the todo application.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from uuid import UUID


class EventType(str, Enum):
    """Enumeration of possible event types."""
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_DELETED = "task.deleted"
    TASK_COMPLETED = "task.completed"
    REMINDER_SCHEDULED = "reminder.scheduled"
    REMINDER_SENT = "reminder.sent"
    RECURRING_TASK_GENERATED = "recurring_task.generated"


class TaskEventData(BaseModel):
    """Schema for task event data."""
    id: str = Field(..., description="Unique identifier for the task")
    title: str = Field(..., min_length=1, max_length=255, description="Title of the task")
    description: Optional[str] = Field(None, description="Detailed description of the task")
    status: str = Field(default="pending", description="Completion status of the task")
    priority: str = Field(default="medium", description="Priority level of the task")
    tags: Optional[list[str]] = Field(default=[], description="Array of tag strings for categorization")
    due_date: Optional[datetime] = Field(None, description="Date and time when the task is due")
    recurrence_pattern: Optional[str] = Field(None, description="Defines recurrence rules")
    next_occurrence_date: Optional[datetime] = Field(None, description="When the next occurrence is due")
    user_id: str = Field(..., description="Identifier for the user who owns the task")
    created_at: datetime = Field(..., description="Timestamp when task was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when task was last updated")
    completed_at: Optional[datetime] = Field(None, description="Timestamp when task was completed")


class ReminderEventData(BaseModel):
    """Schema for reminder event data."""
    task_id: str = Field(..., description="Identifier for the task this reminder is for")
    scheduled_time: datetime = Field(..., description="When the reminder should be triggered")
    user_id: str = Field(..., description="Identifier for the user who owns the task")
    notification_type: str = Field(default="reminder", description="Type of notification")


class RecurringTaskEventData(BaseModel):
    """Schema for recurring task event data."""
    id: str = Field(..., description="Unique identifier for the new task instance")
    title: str = Field(..., min_length=1, max_length=255, description="Title of the task")
    description: Optional[str] = Field(None, description="Detailed description of the task")
    status: str = Field(default="pending", description="Completion status of the task")
    priority: str = Field(default="medium", description="Priority level of the task")
    tags: Optional[list[str]] = Field(default=[], description="Array of tag strings for categorization")
    due_date: Optional[datetime] = Field(None, description="Date and time when the task is due")
    recurrence_pattern: Optional[str] = Field(None, description="Defines recurrence rules")
    user_id: str = Field(..., description="Identifier for the user who owns the task")
    recurrence_source_id: str = Field(..., description="Identifier for the original recurring task")


class BaseEvent(BaseModel):
    """Base schema for all events."""
    id: str = Field(..., description="Unique identifier for the event")
    type: EventType = Field(..., description="Type of the event")
    source: str = Field(..., description="Source service that generated the event")
    timestamp: datetime = Field(..., description="When the event was created")
    data: Dict[str, Any] = Field(..., description="Event-specific data payload")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracing")


class TaskEvent(BaseEvent):
    """Schema for task-related events."""
    type: EventType
    data: TaskEventData


class ReminderEvent(BaseEvent):
    """Schema for reminder-related events."""
    type: EventType
    data: ReminderEventData


class RecurringTaskEvent(BaseEvent):
    """Schema for recurring task events."""
    type: EventType
    data: RecurringTaskEventData


def validate_event_schema(topic: str, data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate the schema of an incoming event based on its topic.

    Args:
        topic: The Kafka topic the event came from
        data: The event data to validate

    Returns:
        A tuple containing (is_valid, error_message)
    """
    try:
        if topic == "task-events":
            # Validate against TaskEvent schema
            TaskEvent(**data)
        elif topic == "reminders":
            # Validate against ReminderEvent schema
            ReminderEvent(**data)
        elif topic == "recurring-tasks":
            # Validate against RecurringTaskEvent schema
            RecurringTaskEvent(**data)
        else:
            # For other topics, just ensure basic structure
            BaseEvent(**data)
        
        return True, ""
    except Exception as e:
        return False, str(e)