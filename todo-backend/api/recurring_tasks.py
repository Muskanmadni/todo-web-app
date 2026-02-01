"""
API endpoints for recurring tasks.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from models.todo import Todo
from models.user import User
from database import get_session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import json

router = APIRouter(prefix="/recurring-tasks", tags=["recurring-tasks"])


@router.post("/", response_model=dict)
def create_recurring_task(
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    tags: Optional[List[str]] = None,
    due_date: Optional[datetime] = None,
    recurrence_pattern: str = None,  # JSON string representing the recurrence pattern
    user_id: str = Depends(lambda: "user123"),  # Placeholder - would come from auth
    session: Session = Depends(get_session)
):
    """
    Create a new recurring task.
    
    Args:
        title: The title of the task
        description: Optional description of the task
        priority: Priority level (low, medium, high)
        tags: Optional list of tags for categorization
        due_date: Optional due date for the task
        recurrence_pattern: JSON string defining the recurrence pattern
        user_id: ID of the user creating the task
        
    Returns:
        Dictionary representation of the created recurring task
    """
    try:
        # Validate recurrence pattern if provided
        if recurrence_pattern:
            try:
                pattern_data = json.loads(recurrence_pattern)
                # Validate required fields in pattern
                if "frequency" not in pattern_data:
                    raise HTTPException(status_code=400, detail="Recurrence pattern must include 'frequency'")
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid recurrence pattern JSON")
        
        # Create the recurring task
        from uuid import UUID as PyUUID
        user_uuid = PyUUID(user_id) if user_id else PyUUID(int=0)  # Use a default UUID if none provided
        
        todo = Todo(
            title=title,
            description=description,
            user_id=user_uuid,
            status="pending",  # Default status
            priority=priority,
            tags=tags,
            due_date=due_date,
            recurrence_pattern=recurrence_pattern
        )
        
        session.add(todo)
        session.commit()
        session.refresh(todo)
        
        # Return a dictionary representation
        return {
            "id": str(todo.id),
            "title": todo.title,
            "description": todo.description,
            "status": todo.status,
            "priority": todo.priority,
            "tags": todo.tags,
            "dueDate": todo.due_date.isoformat() if todo.due_date else None,
            "recurrencePattern": todo.recurrence_pattern,
            "userId": str(todo.user_id),
            "createdAt": todo.created_at.isoformat(),
            "completedAt": todo.completed_at.isoformat() if todo.completed_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating recurring task: {str(e)}")


@router.get("/{task_id}", response_model=dict)
def get_recurring_task(
    task_id: UUID,
    session: Session = Depends(get_session)
):
    """
    Get a specific recurring task.
    
    Args:
        task_id: The ID of the recurring task to retrieve
        session: Database session
        
    Returns:
        Dictionary representation of the recurring task
    """
    todo = session.get(Todo, task_id)
    
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if this is actually a recurring task
    if not todo.recurrence_pattern:
        raise HTTPException(status_code=400, detail="Task is not a recurring task")
    
    # Return a dictionary representation
    return {
        "id": str(todo.id),
        "title": todo.title,
        "description": todo.description,
        "status": todo.status,
        "priority": todo.priority,
        "tags": todo.tags,
        "dueDate": todo.due_date.isoformat() if todo.due_date else None,
        "recurrencePattern": todo.recurrence_pattern,
        "userId": str(todo.user_id),
        "createdAt": todo.created_at.isoformat(),
        "completedAt": todo.completed_at.isoformat() if todo.completed_at else None
    }


@router.put("/{task_id}", response_model=dict)
def update_recurring_task(
    task_id: UUID,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[datetime] = None,
    recurrence_pattern: Optional[str] = None,  # JSON string representing the recurrence pattern
    session: Session = Depends(get_session)
):
    """
    Update an existing recurring task.
    
    Args:
        task_id: The ID of the recurring task to update
        title: New title (optional)
        description: New description (optional)
        status: New status (optional)
        priority: New priority (optional)
        tags: New tags (optional)
        due_date: New due date (optional)
        recurrence_pattern: New recurrence pattern (optional)
        session: Database session
        
    Returns:
        Dictionary representation of the updated recurring task
    """
    todo = session.get(Todo, task_id)
    
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if this is actually a recurring task
    if not todo.recurrence_pattern:
        raise HTTPException(status_code=400, detail="Task is not a recurring task")
    
    # Update the fields if provided
    if title is not None:
        todo.title = title
    if description is not None:
        todo.description = description
    if status is not None:
        todo.status = status
    if priority is not None:
        todo.priority = priority
    if tags is not None:
        todo.tags = tags
    if due_date is not None:
        todo.due_date = due_date
    if recurrence_pattern is not None:
        # Validate the recurrence pattern
        try:
            pattern_data = json.loads(recurrence_pattern)
            # Validate required fields in pattern
            if "frequency" not in pattern_data:
                raise HTTPException(status_code=400, detail="Recurrence pattern must include 'frequency'")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid recurrence pattern JSON")
        todo.recurrence_pattern = recurrence_pattern
    
    session.add(todo)
    session.commit()
    session.refresh(todo)
    
    # Return a dictionary representation
    return {
        "id": str(todo.id),
        "title": todo.title,
        "description": todo.description,
        "status": todo.status,
        "priority": todo.priority,
        "tags": todo.tags,
        "dueDate": todo.due_date.isoformat() if todo.due_date else None,
        "recurrencePattern": todo.recurrence_pattern,
        "userId": str(todo.user_id),
        "createdAt": todo.created_at.isoformat(),
        "completedAt": todo.completed_at.isoformat() if todo.completed_at else None
    }


@router.delete("/{task_id}")
def delete_recurring_task(
    task_id: UUID,
    session: Session = Depends(get_session)
):
    """
    Delete a recurring task.
    
    Args:
        task_id: The ID of the recurring task to delete
        session: Database session
        
    Returns:
        Success message
    """
    todo = session.get(Todo, task_id)
    
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if this is actually a recurring task
    if not todo.recurrence_pattern:
        raise HTTPException(status_code=400, detail="Task is not a recurring task")
    
    session.delete(todo)
    session.commit()
    
    return {"success": True, "message": "Recurring task deleted successfully"}