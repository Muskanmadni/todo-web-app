from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from ..models.todo import TodoBase


def validate_todo_data(todo_data: TodoBase) -> None:
    """
    Validate todo data before creating or updating
    """
    # Validate title length
    if not (1 <= len(todo_data.title) <= 255):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must be between 1 and 255 characters"
        )
    
    # Validate status
    valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
    if todo_data.status and todo_data.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status must be one of {valid_statuses}"
        )
    
    # Validate priority
    valid_priorities = ["low", "medium", "high", "urgent"]
    if todo_data.priority and todo_data.priority not in valid_priorities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Priority must be one of {valid_priorities}"
        )
    
    # Validate due date
    if todo_data.due_date and todo_data.due_date < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Due date must be in the future"
        )


def validate_user_access(user_id: str, resource_user_id: str) -> None:
    """
    Validate that the user has access to the resource
    """
    if user_id != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )