from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session

from database import get_session
from models.todo import Todo, Priority
from services.todo_service import TodoService
from mcp.tools import TodoMCPTools

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=List[Todo])
def get_todos(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    search: Optional[str] = Query(None, description="Search keyword"),
    sort_by: str = Query("created_at", description="Sort by field"),
    order: str = Query("desc", description="Sort order (asc/desc)"),
    session: Session = Depends(get_session)
):
    """
    Get todos with advanced filtering, searching, and sorting capabilities.
    """
    service = TodoService()
    # This would come from auth in a real implementation
    user_id = get_current_user_id()
    todos = service.get_todos_by_filters(
        session=session,
        user_id=user_id,
        completed=completed,
        priority=priority,
        tags=tags,
        search_keyword=search,
        sort_by=sort_by,
        sort_order=order
    )
    return todos


@router.post("/", response_model=Todo)
def create_todo(
    title: str,
    description: Optional[str] = None,
    priority: Priority = Priority.medium,
    tags: Optional[List[str]] = Query(None, description="Tags for the task"),
    due_date: Optional[str] = None,
    recurrence_pattern: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """
    Create a new todo with advanced features.
    """
    # Using MCP tool for this operation
    result = TodoMCPTools.create_todo_with_priority(
        title=title,
        description=description,
        user_id=str(get_current_user_id()),
        priority=priority.value if priority else "medium",
        tags=tags,
        due_date=due_date
    )
    return result


@router.put("/{todo_id}", response_model=Todo)
def update_todo(
    todo_id: UUID,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[Priority] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """
    Update a todo with advanced features.
    """
    # Using MCP tool for this operation
    result = TodoMCPTools.update_todo_with_advanced_features(
        todo_id=str(todo_id),
        title=title,
        description=description,
        status=status,
        priority=priority.value if priority else None,
        tags=tags,
        due_date=due_date
    )

    if not result:
        raise HTTPException(status_code=404, detail="Todo not found")

    return result


@router.delete("/{todo_id}")
def delete_todo(todo_id: UUID, session: Session = Depends(get_session)):
    """
    Delete a todo.
    """
    # Using MCP tool for this operation
    result = TodoMCPTools.delete_todo(str(todo_id))
    if not result["success"]:
        raise HTTPException(status_code=404, detail="Todo not found")
    return result


@router.put("/{todo_id}/complete", response_model=Todo)
def mark_todo_complete(todo_id: UUID, session: Session = Depends(get_session)):
    """
    Mark a todo as completed.
    """
    # Using MCP tool for this operation
    result = TodoMCPTools.mark_todo_completed(str(todo_id))
    if not result:
        raise HTTPException(status_code=404, detail="Todo not found")
    return result


@router.put("/{todo_id}/pending", response_model=Todo)
def mark_todo_pending(todo_id: UUID, session: Session = Depends(get_session)):
    """
    Mark a todo as pending.
    """
    # Using MCP tool for this operation
    result = TodoMCPTools.mark_todo_pending(str(todo_id))
    if not result:
        raise HTTPException(status_code=404, detail="Todo not found")
    return result


def get_current_user_id():
    """
    Placeholder function to get the current user ID from authentication.
    In a real implementation, this would extract the user ID from the JWT token.
    """
    # This is a placeholder - in reality, this would come from the authenticated user
    # extracted from the JWT token in the Authorization header
    from uuid import UUID
    return UUID("12345678-1234-5678-9abc-123456789abc")  # Example UUID