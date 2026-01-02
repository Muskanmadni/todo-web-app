from mcp_server import Server
from pydantic import BaseModel
from typing import Optional
import asyncio


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


# Initialize the MCP server
server = Server("todo-mcp-server")


@server.tool("create_todo")
async def create_todo(params: CreateTodoParams) -> dict:
    """
    Create a new todo using the parameters provided
    """
    # In a real implementation, this would call the TodoService
    # For now, we return a mock response
    return {
        "id": "mock-todo-id",
        "title": params.title,
        "description": params.description,
        "status": "pending",
        "due_date": params.due_date,
        "priority": params.priority,
        "created_at": "2025-01-01T00:00:00Z"
    }


@server.tool("get_todos")
async def get_todos() -> list:
    """
    Get all todos for the current user
    """
    # In a real implementation, this would call the TodoService
    # For now, we return a mock response
    return [
        {
            "id": "mock-todo-id-1",
            "title": "Sample todo",
            "description": "Sample description",
            "status": "pending",
            "due_date": "2025-01-02T00:00:00Z",
            "priority": "medium",
            "created_at": "2025-01-01T00:00:00Z"
        }
    ]


@server.tool("get_todo")
async def get_todo(params: GetTodoParams) -> dict:
    """
    Get a specific todo by ID
    """
    # In a real implementation, this would call the TodoService
    # For now, we return a mock response
    return {
        "id": params.id,
        "title": "Sample todo",
        "description": "Sample description",
        "status": "pending",
        "due_date": "2025-01-02T00:00:00Z",
        "priority": "medium",
        "created_at": "2025-01-01T00:00:00Z"
    }


@server.tool("update_todo")
async def update_todo(params: UpdateTodoParams) -> dict:
    """
    Update an existing todo
    """
    # In a real implementation, this would call the TodoService
    # For now, we return a mock response
    return {
        "id": params.id,
        "title": params.title or "Sample todo",
        "description": params.description or "Sample description",
        "status": params.status or "pending",
        "due_date": params.due_date or "2025-01-02T00:00:00Z",
        "priority": params.priority or "medium",
        "created_at": "2025-01-01T00:00:00Z"
    }


@server.tool("delete_todo")
async def delete_todo(params: DeleteTodoParams) -> dict:
    """
    Delete a specific todo by ID
    """
    # In a real implementation, this would call the TodoService
    # For now, we return a mock response
    return {
        "success": True,
        "deleted_id": params.id
    }


@server.tool("search_todos")
async def search_todos(params: SearchTodosParams) -> list:
    """
    Search todos by various criteria
    """
    # In a real implementation, this would call the TodoService
    # For now, we return a mock response
    return [
        {
            "id": "mock-todo-id-1",
            "title": "Sample todo",
            "description": "Sample description",
            "status": "pending",
            "due_date": "2025-01-02T00:00:00Z",
            "priority": "medium",
            "created_at": "2025-01-01T00:00:00Z"
        }
    ]


# Example of how to run the server
async def run_server():
    async with server.serve("127.0.0.1", 8080):
        print("MCP server running on 127.0.0.1:8080")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(run_server())