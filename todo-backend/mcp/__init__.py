"""
MCP (Model Context Protocol) Server Configuration
"""
from typing import Dict, Any, Callable
import logging

# Set up logging for MCP operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the tools available via MCP
MCP_TOOLS: Dict[str, Callable] = {
    "create_todo": None,  # Will be set after module imports are resolved
    "update_todo": None,
    "delete_todo": None,
    "mark_todo_completed": None,
    "mark_todo_pending": None,
}

# Tool descriptions for MCP discovery
MCP_TOOL_DESCRIPTIONS: Dict[str, Dict[str, Any]] = {
    "create_todo": {
        "description": "Creates a new todo item",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "The title of the todo"},
                "description": {"type": "string", "description": "Optional description of the todo"},
                "user_id": {"type": "string", "description": "ID of the user creating the todo"}
            },
            "required": ["title"]
        }
    },
    "update_todo": {
        "description": "Updates an existing todo item",
        "parameters": {
            "type": "object",
            "properties": {
                "todo_id": {"type": "string", "description": "The ID of the todo to update"},
                "title": {"type": "string", "description": "New title (optional)"},
                "description": {"type": "string", "description": "New description (optional)"},
                "status": {"type": "string", "description": "New status (pending/completed) (optional)"}
            },
            "required": ["todo_id"]
        }
    },
    "delete_todo": {
        "description": "Deletes a todo item",
        "parameters": {
            "type": "object",
            "properties": {
                "todo_id": {"type": "string", "description": "The ID of the todo to delete"}
            },
            "required": ["todo_id"]
        }
    },
    "mark_todo_completed": {
        "description": "Marks a todo as completed",
        "parameters": {
            "type": "object",
            "properties": {
                "todo_id": {"type": "string", "description": "The ID of the todo to mark as completed"}
            },
            "required": ["todo_id"]
        }
    },
    "mark_todo_pending": {
        "description": "Marks a todo as pending",
        "parameters": {
            "type": "object",
            "properties": {
                "todo_id": {"type": "string", "description": "The ID of the todo to mark as pending"}
            },
            "required": ["todo_id"]
        }
    }
}


def initialize_mcp_tools():
    """
    Initialize the MCP tools after all modules are loaded
    """
    # Use absolute import to avoid relative import errors
    try:
        from .tools import TodoMCPTools
    except ImportError:
        # Fallback for when module is run directly
        from mcp.tools import TodoMCPTools

    MCP_TOOLS["create_todo"] = TodoMCPTools.create_todo
    MCP_TOOLS["update_todo"] = TodoMCPTools.update_todo
    MCP_TOOLS["delete_todo"] = TodoMCPTools.delete_todo
    MCP_TOOLS["mark_todo_completed"] = TodoMCPTools.mark_todo_completed
    MCP_TOOLS["mark_todo_pending"] = TodoMCPTools.mark_todo_pending


# Initialize tools when module is loaded
initialize_mcp_tools()


def get_tool(tool_name: str) -> Callable:
    """
    Retrieve an MCP tool by name
    """
    if tool_name not in MCP_TOOLS:
        raise ValueError(f"Tool {tool_name} not found in available MCP tools")
    
    tool = MCP_TOOLS[tool_name]
    if tool is None:
        raise ValueError(f"Tool {tool_name} is not properly initialized")
    
    return tool


def get_tool_description(tool_name: str) -> Dict[str, Any]:
    """
    Retrieve the description for an MCP tool
    """
    if tool_name not in MCP_TOOL_DESCRIPTIONS:
        raise ValueError(f"Description for tool {tool_name} not found")
    
    return MCP_TOOL_DESCRIPTIONS[tool_name]


def list_available_tools() -> list:
    """
    List all available MCP tools
    """
    return list(MCP_TOOLS.keys())