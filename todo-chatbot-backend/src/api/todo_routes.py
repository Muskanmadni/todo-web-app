from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlmodel import Session
from ..models.todo import Todo, TodoBase
from ..services.todo_service import TodoService
from ..db.session import get_session
from ..models.user import User
from fastapi.security import HTTPBearer


router = APIRouter()
security = HTTPBearer()


@router.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo_data: TodoBase,
    session: Session = Depends(get_session),
    # In a real implementation, you'd get the user from the token
    # user: User = Depends(get_current_user)
):
    """
    Create a new todo
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")
    
    try:
        todo = TodoService.create_todo(session, mock_user_id, todo_data)
        return todo
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/todos", response_model=List[Todo])
def get_todos(
    session: Session = Depends(get_session),
    # user: User = Depends(get_current_user)
):
    """
    Get all todos for the authenticated user
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")
    
    todos = TodoService.get_todos_by_user(session, mock_user_id)
    return todos


@router.get("/todos/{todo_id}", response_model=Todo)
def get_todo(
    todo_id: UUID,
    session: Session = Depends(get_session),
    # user: User = Depends(get_current_user)
):
    """
    Get a specific todo by ID
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")
    
    todo = TodoService.get_todo_by_id(session, todo_id, mock_user_id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    
    return todo


@router.put("/todos/{todo_id}", response_model=Todo)
def update_todo(
    todo_id: UUID,
    todo_data: TodoBase,
    session: Session = Depends(get_session),
    # user: User = Depends(get_current_user)
):
    """
    Update a specific todo
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")
    
    updated_todo = TodoService.update_todo(session, todo_id, mock_user_id, todo_data)
    if not updated_todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    
    return updated_todo


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: UUID,
    session: Session = Depends(get_session),
    # user: User = Depends(get_current_user)
):
    """
    Delete a specific todo
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")
    
    success = TodoService.delete_todo(session, todo_id, mock_user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    
    return