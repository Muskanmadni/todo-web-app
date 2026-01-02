from mcp_server import Server
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from sqlmodel import Session
from ..models.todo import Todo
from ..services.todo_service import TodoService
from ..db.session import get_session


class CreateTodoParams(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = "medium"


class UpdateTodoParams(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None


class GetTodoParams(BaseModel):
    id: str


class DeleteTodoParams(BaseModel):
    id: str


class SearchTodosParams(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    due_date_from: Optional[str] = None
    due_date_to: Optional[str] = None
    priority: Optional[str] = None


# Initialize the MCP server for todo tools
todo_tools_server = Server("todo-tools-mcp-server")


@todo_tools_server.tool("create_todo")
async def create_todo(params: CreateTodoParams) -> dict:
    """
    Create a new todo using the parameters provided
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user context
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")
    
    # Get database session
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # Create TodoBase object from params
        from ..models.todo import TodoBase
        todo_data = TodoBase(
            title=params.title,
            description=params.description,
            due_date=params.due_date,
            priority=params.priority or "medium"
        )
        
        # Use TodoService to create the todo
        created_todo = TodoService.create_todo(session, mock_user_id, todo_data)
        
        # Convert to dict for response
        return {
            "id": str(created_todo.id),
            "title": created_todo.title,
            "description": created_todo.description,
            "status": created_todo.status,
            "due_date": created_todo.due_date.isoformat() if created_todo.due_date else None,
            "priority": created_todo.priority,
            "created_at": created_todo.created_at.isoformat(),
            "user_id": str(created_todo.user_id)
        }
    except Exception as e:
        raise e
    finally:
        session.close()


@todo_tools_server.tool("get_todos")
async def get_todos() -> list:
    """
    Get all todos for the current user
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user context
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")
    
    # Get database session
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        todos = TodoService.get_todos_by_user(session, mock_user_id)
        
        # Convert to list of dicts for response
        return [
            {
                "id": str(todo.id),
                "title": todo.title,
                "description": todo.description,
                "status": todo.status,
                "due_date": todo.due_date.isoformat() if todo.due_date else None,
                "priority": todo.priority,
                "created_at": todo.created_at.isoformat(),
                "user_id": str(todo.user_id)
            }
            for todo in todos
        ]
    except Exception as e:
        raise e
    finally:
        session.close()


@todo_tools_server.tool("get_todo")
async def get_todo(params: GetTodoParams) -> dict:
    """
    Get a specific todo by ID
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user context
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")
    
    # Get database session
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # Convert string ID to UUID
        todo_id = UUID(params.id)
        
        todo = TodoService.get_todo_by_id(session, todo_id, mock_user_id)
        if not todo:
            raise ValueError(f"Todo with id {params.id} not found")
        
        # Convert to dict for response
        return {
            "id": str(todo.id),
            "title": todo.title,
            "description": todo.description,
            "status": todo.status,
            "due_date": todo.due_date.isoformat() if todo.due_date else None,
            "priority": todo.priority,
            "created_at": todo.created_at.isoformat(),
            "user_id": str(todo.user_id)
        }
    except Exception as e:
        raise e
    finally:
        session.close()


@todo_tools_server.tool("update_todo")
async def update_todo(params: UpdateTodoParams) -> dict:
    """
    Update an existing todo
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user context
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")
    
    # Get database session
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # Convert string ID to UUID
        todo_id = UUID(params.id)
        
        # Create TodoBase object from params (excluding the ID)
        from ..models.todo import TodoBase
        update_data = {k: v for k, v in params.dict().items() if k != 'id' and v is not None}
        todo_data = TodoBase(**update_data)
        
        updated_todo = TodoService.update_todo(session, todo_id, mock_user_id, todo_data)
        if not updated_todo:
            raise ValueError(f"Todo with id {params.id} not found")
        
        # Convert to dict for response
        return {
            "id": str(updated_todo.id),
            "title": updated_todo.title,
            "description": updated_todo.description,
            "status": updated_todo.status,
            "due_date": updated_todo.due_date.isoformat() if updated_todo.due_date else None,
            "priority": updated_todo.priority,
            "created_at": updated_todo.created_at.isoformat(),
            "updated_at": updated_todo.updated_at.isoformat(),
            "user_id": str(updated_todo.user_id)
        }
    except Exception as e:
        raise e
    finally:
        session.close()


@todo_tools_server.tool("delete_todo")
async def delete_todo(params: DeleteTodoParams) -> dict:
    """
    Delete a specific todo by ID
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user context
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")
    
    # Get database session
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # Convert string ID to UUID
        todo_id = UUID(params.id)
        
        success = TodoService.delete_todo(session, todo_id, mock_user_id)
        if not success:
            raise ValueError(f"Todo with id {params.id} not found")
        
        return {
            "success": True,
            "deleted_id": params.id
        }
    except Exception as e:
        raise e
    finally:
        session.close()


@todo_tools_server.tool("search_todos")
async def search_todos(params: SearchTodosParams) -> list:
    """
    Search todos by various criteria
    """
    # For now, using a mock user_id - in real implementation this would come from authenticated user context
    mock_user_id = UUID("12345678-1234-5678-1234-567812345678")
    
    # Get database session
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        todos = TodoService.search_todos(
            session,
            mock_user_id,
            title=params.title,
            status=params.status,
            priority=params.priority,
            due_date_from=params.due_date_from,
            due_date_to=params.due_date_to
        )
        
        # Convert to list of dicts for response
        return [
            {
                "id": str(todo.id),
                "title": todo.title,
                "description": todo.description,
                "status": todo.status,
                "due_date": todo.due_date.isoformat() if todo.due_date else None,
                "priority": todo.priority,
                "created_at": todo.created_at.isoformat(),
                "user_id": str(todo.user_id)
            }
            for todo in todos
        ]
    except Exception as e:
        raise e
    finally:
        session.close()