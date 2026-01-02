import asyncio
from openai import OpenAI
from ..config import settings
from ..mcp.todo_tools import todo_tools_server
from mcp_server import ClientSession
import json


class TodoChatAgent:
    """
    AI agent that uses MCP tools to manage todos
    """

    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=settings.openai_api_key)

        # For now, we'll simulate the MCP client connection
        # In a real implementation, this would connect to the running MCP server
        self.todo_tools_client = None

    async def process_message(self, message: str, conversation_context: dict = None) -> str:
        """
        Process a user message and return an appropriate response
        """
        if conversation_context is None:
            conversation_context = {}

        # This is a simplified implementation
        # In a real system, we would:
        # 1. Use the MCP client to connect to our tools server
        # 2. Use OpenAI's function calling or similar to decide which tools to call
        # 3. Process the results and generate a natural language response

        # For now, we'll implement a basic rule-based approach to demonstrate the concept
        response = await self._handle_natural_language_request(message, conversation_context)

        return response

    async def _handle_natural_language_request(self, message: str, conversation_context: dict) -> str:
        """
        Handle natural language requests by mapping them to appropriate todo operations
        """
        message_lower = message.lower()

        # Simple keyword-based matching for demonstration
        # In a real implementation, this would use proper NLP/LLM to understand intent
        if any(word in message_lower for word in ["create", "add", "new", "make"]):
            if any(word in message_lower for word in ["task", "todo", "do", "to do"]):
                # Extract task details from message (simplified)
                # In real implementation, use proper NLP
                task_description = self._extract_task_from_message(message)

                # Update conversation context to include the new task
                if "recent_tasks" not in conversation_context:
                    conversation_context["recent_tasks"] = []
                conversation_context["recent_tasks"].append(task_description)

                return f"I've created a task for you: '{task_description}'."

        elif any(word in message_lower for word in ["show", "list", "see", "what"]):
            if any(word in message_lower for word in ["task", "todo", "do", "to do"]):
                # In real implementation, would call get_todos tool
                # Use conversation context to provide more relevant response
                recent_tasks = conversation_context.get("recent_tasks", [])
                if recent_tasks:
                    return f"Here are your recent tasks: {', '.join(recent_tasks)}"
                else:
                    return "You don't have any tasks yet. Would you like to create one?"

        elif any(word in message_lower for word in ["complete", "done", "finish", "mark"]):
            # Handle completing a task
            # Use conversation context to identify which task to complete
            task_to_complete = self._identify_task_from_context(message, conversation_context)
            if task_to_complete:
                # Update conversation context to reflect the completed task
                if "completed_tasks" not in conversation_context:
                    conversation_context["completed_tasks"] = []
                conversation_context["completed_tasks"].append(task_to_complete)

                # Remove from recent tasks if it's there
                if "recent_tasks" in conversation_context:
                    conversation_context["recent_tasks"] = [
                        task for task in conversation_context["recent_tasks"]
                        if task.lower() != task_to_complete.lower()
                    ]

                return f"I've marked '{task_to_complete}' as completed."
            else:
                return "I couldn't identify which task to complete. Could you be more specific?"

        elif any(word in message_lower for word in ["delete", "remove", "cancel"]):
            # Handle deleting a task
            # Use conversation context to identify which task to delete
            task_to_delete = self._identify_task_from_context(message, conversation_context)
            if task_to_delete:
                # Update conversation context to reflect the deleted task
                if "recent_tasks" in conversation_context:
                    conversation_context["recent_tasks"] = [
                        task for task in conversation_context["recent_tasks"]
                        if task.lower() != task_to_delete.lower()
                    ]

                return f"I've removed '{task_to_delete}' from your list."
            else:
                return "I couldn't identify which task to delete. Could you be more specific?"

        elif any(ref in message_lower for ref in ["that", "the previous", "the last", "it"]):
            # Handle references to previous tasks
            recent_tasks = conversation_context.get("recent_tasks", [])
            if recent_tasks:
                last_task = recent_tasks[-1]
                return f"You mentioned '{last_task}'. How would you like me to help with it?"
            else:
                return "I don't have context about what 'that' refers to. Could you clarify?"

        else:
            # In a real implementation, we would use an LLM to generate a more appropriate response
            return f"I received your message: '{message}'. How can I help you with your tasks?"

    def _extract_task_from_message(self, message: str) -> str:
        """
        Extract task details from a natural language message (simplified implementation)
        """
        # Remove common phrases and extract the core task
        message_lower = message.lower()

        # Remove common leading phrases
        for phrase in ["add a task to", "create a task to", "add task", "create task", "add to do", "create to do", "add todo", "create todo"]:
            if phrase in message_lower:
                return message[len(phrase):].strip()

        # If no common phrase found, return the message as is
        return message.strip()

    def _identify_task_from_context(self, message: str, conversation_context: dict) -> str:
        """
        Identify which task the user is referring to based on the conversation context
        """
        # Look for task references in the message
        message_lower = message.lower()

        # Check if the user is referring to "the last task" or "that task"
        if any(ref in message_lower for ref in ["that", "the previous", "the last", "it"]):
            recent_tasks = conversation_context.get("recent_tasks", [])
            if recent_tasks:
                return recent_tasks[-1]

        # Look for specific task names in the message
        all_tasks = (
            conversation_context.get("recent_tasks", []) +
            conversation_context.get("completed_tasks", [])
        )

        # Find the task that best matches the message
        for task in all_tasks:
            if task.lower() in message_lower:
                return task

        # If no specific task found, return None
        return None


# Example usage of the agent
async def run_example():
    agent = TodoChatAgent()

    # Simulate a conversation with context
    conversation_context = {}
    messages = [
        "Add a task to buy groceries",
        "What are my tasks?",
        "Mark the grocery task as completed",
        "What about that task?",
        "Remove the grocery task"
    ]

    for msg in messages:
        response = await agent.process_message(msg, conversation_context)
        print(f"User: {msg}")
        print(f"Agent: {response}")
        print(f"Context: {conversation_context}")
        print()


if __name__ == "__main__":
    asyncio.run(run_example())