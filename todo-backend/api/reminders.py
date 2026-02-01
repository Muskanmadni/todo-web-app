"""
API endpoints for task reminders.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from models.reminder import Reminder, ReminderStatus
from models.todo import Todo
from database import get_session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from services.reminder_service import ReminderService

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("/", response_model=dict)
def create_reminder(
    task_id: UUID,
    scheduled_time: datetime,
    session: Session = Depends(get_session)
):
    """
    Create a new reminder for a task.
    
    Args:
        task_id: The ID of the task to create a reminder for
        scheduled_time: When the reminder should be triggered
        session: Database session
        
    Returns:
        Dictionary representation of the created reminder
    """
    try:
        reminder = ReminderService.create_reminder_for_task(task_id, scheduled_time)
        
        # Return a dictionary representation
        return {
            "id": str(reminder.id),
            "taskId": str(reminder.task_id),
            "scheduledTime": reminder.scheduled_time.isoformat(),
            "status": reminder.sent_status,
            "deliveryAttempts": reminder.delivery_attempts,
            "lastAttemptTime": reminder.last_attempt_time.isoformat() if reminder.last_attempt_time else None,
            "createdAt": reminder.created_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating reminder: {str(e)}")


@router.get("/", response_model=List[dict])
def get_reminders(
    status: Optional[ReminderStatus] = None,
    task_id: Optional[UUID] = None,
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    """
    Get reminders with optional filtering.
    
    Args:
        status: Filter by reminder status (pending, sent, failed)
        task_id: Filter by task ID
        limit: Maximum number of reminders to return
        offset: Number of reminders to skip
        session: Database session
        
    Returns:
        List of reminders
    """
    try:
        query = select(Reminder)
        
        if status:
            query = query.where(Reminder.sent_status == status)
        if task_id:
            query = query.where(Reminder.task_id == task_id)
        
        query = query.offset(offset).limit(limit).order_by(Reminder.created_at.desc())
        
        reminders = session.exec(query).all()
        
        # Return a list of dictionary representations
        return [{
            "id": str(reminder.id),
            "taskId": str(reminder.task_id),
            "scheduledTime": reminder.scheduled_time.isoformat(),
            "status": reminder.sent_status,
            "deliveryAttempts": reminder.delivery_attempts,
            "lastAttemptTime": reminder.last_attempt_time.isoformat() if reminder.last_attempt_time else None,
            "createdAt": reminder.created_at.isoformat()
        } for reminder in reminders]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving reminders: {str(e)}")


@router.get("/{reminder_id}", response_model=dict)
def get_reminder(
    reminder_id: UUID,
    session: Session = Depends(get_session)
):
    """
    Get a specific reminder.
    
    Args:
        reminder_id: The ID of the reminder to retrieve
        session: Database session
        
    Returns:
        Dictionary representation of the reminder
    """
    reminder = session.get(Reminder, reminder_id)
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    # Return a dictionary representation
    return {
        "id": str(reminder.id),
        "taskId": str(reminder.task_id),
        "scheduledTime": reminder.scheduled_time.isoformat(),
        "status": reminder.sent_status,
        "deliveryAttempts": reminder.delivery_attempts,
        "lastAttemptTime": reminder.last_attempt_time.isoformat() if reminder.last_attempt_time else None,
        "createdAt": reminder.created_at.isoformat()
    }


@router.put("/{reminder_id}", response_model=dict)
def update_reminder(
    reminder_id: UUID,
    status: ReminderStatus,
    session: Session = Depends(get_session)
):
    """
    Update a reminder's status.
    
    Args:
        reminder_id: The ID of the reminder to update
        status: The new status for the reminder
        session: Database session
        
    Returns:
        Dictionary representation of the updated reminder
    """
    try:
        reminder = ReminderService.update_reminder_status(reminder_id, status)
        
        # Return a dictionary representation
        return {
            "id": str(reminder.id),
            "taskId": str(reminder.task_id),
            "scheduledTime": reminder.scheduled_time.isoformat(),
            "status": reminder.sent_status,
            "deliveryAttempts": reminder.delivery_attempts,
            "lastAttemptTime": reminder.last_attempt_time.isoformat() if reminder.last_attempt_time else None,
            "createdAt": reminder.created_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating reminder: {str(e)}")


@router.delete("/{reminder_id}")
def delete_reminder(
    reminder_id: UUID,
    session: Session = Depends(get_session)
):
    """
    Delete a reminder.
    
    Args:
        reminder_id: The ID of the reminder to delete
        session: Database session
        
    Returns:
        Success message
    """
    success = ReminderService.delete_reminder(reminder_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    return {"success": True, "message": "Reminder deleted successfully"}