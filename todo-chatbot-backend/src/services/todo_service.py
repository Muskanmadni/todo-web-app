from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from ..models.todo import Todo, TodoBase


class TodoService:
    """
    Service class for handling todo operations
    """
    
    @staticmethod
    def create_todo(session: Session, user_id: UUID, todo_data: TodoBase) -> Todo:
        """
        Create a new todo for a user
        """
        # Ensure due date is in the future if provided
        if todo_data.due_date and todo_data.due_date < todo_data.due_date.now():
            raise ValueError("Due date must be in the future")
        
        todo = Todo(
            user_id=user_id,
            title=todo_data.title,
            description=todo_data.description,
            status=todo_data.status,
            due_date=todo_data.due_date,
            priority=todo_data.priority
        )
        
        session.add(todo)
        session.commit()
        session.refresh(todo)
        
        return todo
    
    @staticmethod
    def get_todos_by_user(session: Session, user_id: UUID) -> List[Todo]:
        """
        Get all todos for a specific user
        """
        statement = select(Todo).where(Todo.user_id == user_id)
        todos = session.exec(statement).all()
        return todos
    
    @staticmethod
    def get_todo_by_id(session: Session, todo_id: UUID, user_id: UUID) -> Optional[Todo]:
        """
        Get a specific todo by ID for a user
        """
        statement = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        todo = session.exec(statement).first()
        return todo
    
    @staticmethod
    def update_todo(session: Session, todo_id: UUID, user_id: UUID, todo_data: TodoBase) -> Optional[Todo]:
        """
        Update a specific todo for a user
        """
        todo = TodoService.get_todo_by_id(session, todo_id, user_id)
        if not todo:
            return None
        
        # Update fields if provided
        update_data = todo_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)
        
        # Ensure due date is in the future if provided
        if todo.due_date and todo.due_date < todo.due_date.now():
            raise ValueError("Due date must be in the future")
        
        session.add(todo)
        session.commit()
        session.refresh(todo)
        
        return todo
    
    @staticmethod
    def delete_todo(session: Session, todo_id: UUID, user_id: UUID) -> bool:
        """
        Delete a specific todo for a user
        """
        todo = TodoService.get_todo_by_id(session, todo_id, user_id)
        if not todo:
            return False
        
        session.delete(todo)
        session.commit()
        return True
    
    @staticmethod
    def search_todos(session: Session, user_id: UUID, title: Optional[str] = None, 
                    status: Optional[str] = None, priority: Optional[str] = None,
                    due_date_from: Optional[str] = None, due_date_to: Optional[str] = None) -> List[Todo]:
        """
        Search todos by various criteria
        """
        statement = select(Todo).where(Todo.user_id == user_id)
        
        if title:
            statement = statement.where(Todo.title.contains(title))
        if status:
            statement = statement.where(Todo.status == status)
        if priority:
            statement = statement.where(Todo.priority == priority)
        if due_date_from:
            from datetime import datetime
            date_from = datetime.fromisoformat(due_date_from)
            statement = statement.where(Todo.due_date >= date_from)
        if due_date_to:
            from datetime import datetime
            date_to = datetime.fromisoformat(due_date_to)
            statement = statement.where(Todo.due_date <= date_to)
        
        todos = session.exec(statement).all()
        return todos