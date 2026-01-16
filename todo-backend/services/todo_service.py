from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime
try:
    from ..models.todo import Todo
except (ImportError, ValueError):
    # Fallback for when module is run directly
    from models.todo import Todo


class TodoService:
    @staticmethod
    def create_todo(session: Session, title: str, description: Optional[str], user_id: UUID) -> Todo:
        """
        Creates a new todo item for a user
        """
        todo = Todo(
            title=title,
            description=description,
            user_id=user_id,
            status="pending"
        )
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo

    @staticmethod
    def get_todo_by_id(session: Session, todo_id: UUID) -> Optional[Todo]:
        """
        Retrieves a specific todo by its ID
        """
        return session.get(Todo, todo_id)

    @staticmethod
    def get_todos_by_user(session: Session, user_id: UUID, status: Optional[str] = None) -> List[Todo]:
        """
        Retrieves all todos for a specific user, optionally filtered by status
        """
        query = select(Todo).where(Todo.user_id == user_id)
        
        if status:
            query = query.where(Todo.status == status)
            
        return session.exec(query).all()

    @staticmethod
    def update_todo(
        session: Session,
        todo_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[Todo]:
        """
        Updates an existing todo with new values
        """
        todo = session.get(Todo, todo_id)

        if not todo:
            return None

        if title is not None:
            todo.title = title
        if description is not None:
            todo.description = description
        if status is not None:
            todo.status = status
            if status == "completed":
                todo.completed_at = datetime.utcnow()
            elif status == "pending":
                todo.completed_at = None

        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo

    @staticmethod
    def delete_todo(session: Session, todo_id: UUID) -> bool:
        """
        Deletes a todo by its ID
        """
        todo = session.get(Todo, todo_id)
        
        if not todo:
            return False
            
        session.delete(todo)
        session.commit()
        return True

    @staticmethod
    def mark_todo_completed(session: Session, todo_id: UUID) -> Optional[Todo]:
        """
        Marks a todo as completed
        """
        return TodoService.update_todo(session, todo_id, status="completed")

    @staticmethod
    def mark_todo_pending(session: Session, todo_id: UUID) -> Optional[Todo]:
        """
        Marks a todo as pending
        """
        return TodoService.update_todo(session, todo_id, status="pending")