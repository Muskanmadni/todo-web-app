from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Define security scheme
security = HTTPBearer()
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
import re
from datetime import datetime
from sqlmodel import Session, select
from mcp.tools import TodoMCPTools
from services.conversation_service import ConversationService
from services.message_service import MessageService
from database import get_session, engine
from models.conversation import Conversation
from models.message import Message
from models.todo import Todo
from models.user import User as UserModel
from analytics import analytics_service, EventType
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import re

# Load environment variables
load_dotenv()

# Configure Google Generative AI
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    print("Warning: GEMINI_API_KEY environment variable is not set. Chatbot functionality may be limited.")
    gemini_model = None
else:
    genai.configure(api_key=gemini_api_key)

    # Initialize the model
    generation_config = {
        "temperature": 0.3,
        "max_output_tokens": 200,
    }

    gemini_model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config,
    )




router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversationId: Optional[str] = None
    metadata: Optional[dict] = None


class ChatResponse(BaseModel):
    conversationId: str
    response: str
    action: str
    todo: Optional[dict] = None
    metadata: Optional[dict] = None


from fastapi import HTTPException, status
import uuid
from models.user import User as UserModel
from sqlmodel import select
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> UserModel:
    """
    Decode JWT token and return the user.
    """
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        # Convert user_id to UUID to match the database field type
        user_id_uuid = uuid.UUID(user_id)
    except (JWTError, ValueError):
        raise credentials_exception

    from database import engine
    from sqlmodel import Session

    with Session(engine) as temp_session:
        user = temp_session.exec(select(UserModel).where(UserModel.id == user_id_uuid)).first()
        if user is None:
            raise credentials_exception
        return user

from fastapi import Request


@router.post("/conversation", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: UserModel = Security(get_current_user_from_token, scopes=[])
):
    """
    Process a chat message and return an appropriate response.
    This endpoint handles natural language processing and executes
    appropriate actions based on the user's intent.
    """
    # Get the authenticated user from the token
    user_id = current_user.id

    # Extract conversation ID or create a new one
    conversation_id = None
    if request.conversationId:
        try:
            conversation_id = UUID(request.conversationId)
            # Verify conversation exists and belongs to user
            conversation = session.get(Conversation, conversation_id)
            if not conversation or conversation.user_id != user_id:
                raise HTTPException(status_code=404, detail="Conversation not found")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid conversation ID")
    else:
        # Create a new conversation
        conversation = ConversationService.create_conversation(
            session=session,
            title=request.message[:50] + "..." if len(request.message) > 50 else request.message,
            user_id=user_id
        )
        conversation_id = conversation.id

    # Track the chat request
    analytics_service.track_chat_request(
        user_id=str(user_id),
        conversation_id=str(conversation_id),
        message=request.message
    )

    # Retrieve conversation history for context, limiting to last 20 messages for performance
    all_messages = MessageService.get_messages_by_conversation(session, conversation_id)
    # Keep only the most recent messages to maintain performance with long conversations
    conversation_history = all_messages[-20:] if len(all_messages) > 20 else all_messages

    # Save the user's message
    MessageService.create_message(
        session=session,
        conversation_id=conversation_id,
        role="user",
        content=request.message,
        metadata=request.metadata
    )

    try:
        # Process the natural language command with context
        response, action, todo_data = process_natural_language_command(
            request.message,
            session,
            conversation_id,
            user_id,  # Pass the user_id to the function
            conversation_history
        )

        # Save the assistant's response
        MessageService.create_message(
            session=session,
            conversation_id=conversation_id,
            role="assistant",
            content=response,
            metadata={"action": action, "timestamp": datetime.utcnow().isoformat()}
        )

        # Track the chat response
        analytics_service.track_chat_response(
            user_id=str(user_id),
            conversation_id=str(conversation_id),
            response=response,
            action=action
        )

        # Track todo operations if they occurred
        if todo_data and action in ["todo_created", "todo_completed", "todo_deleted", "todo_updated"]:
            analytics_service.track_todo_operation(
                operation=action.replace("todo_", ""),
                user_id=str(user_id),
                conversation_id=str(conversation_id),
                todo_data=todo_data
            )

        return ChatResponse(
            conversationId=str(conversation_id),
            response=response,
            action=action,
            todo=todo_data
        )
    except Exception as e:
        # Track the error
        analytics_service.track_error(
            user_id=str(user_id),
            conversation_id=str(conversation_id),
            error_message=str(e),
            error_type=type(e).__name__
        )
        raise


def process_natural_language_command(message: str, session: Session, conversation_id: UUID, user_id: UUID, conversation_history=None):
    """
    Process natural language commands using Google Gemini and execute appropriate actions.
    Enhanced with error handling, disambiguation, and AI misinterpretation handling.
    """
    # If Gemini model is not available, use fallback processing
    if gemini_model is None:
        print("Gemini model not available, using fallback processing")
        return process_natural_language_command_fallback(message, session, conversation_id, user_id, conversation_history)

    # Prepare conversation history for the AI
    # Format the conversation history for Gemini
    conversation_text = "System: You are an AI assistant that helps users manage their todos.\n"
    conversation_text += "Respond in the following JSON format:\n"
    conversation_text += """{
        "action": "create_todo|create_todo_with_priority|complete_todo|delete_todo|list_todos|search_todos|filter_todos|sort_todos|create_recurring_task|cancel_recurring_series|unknown_command|error",
        "title": "todo title if applicable",
        "description": "todo description if applicable",
        "priority": "priority level (low, medium, high)",
        "tags": "list of tags if applicable",
        "due_date": "due date in ISO format if applicable",
        "recurrence_pattern": "recurrence pattern if applicable",
        "response": "natural language response to the user"
    }\n\n"""

    conversation_text += "For example:\n"
    conversation_text += "- User: 'Add a high priority todo: Buy groceries due tomorrow with tags shopping, urgent'\n"
    conversation_text += '''- Response: {"action": "create_todo_with_priority", "title": "Buy groceries", "priority": "high", "tags": ["shopping", "urgent"], "due_date": "2023-10-06T00:00:00", "response": "I've added 'Buy groceries' to your todo list with high priority."}\n\n'''

    conversation_text += "- User: 'Complete 'Buy groceries''\n"
    conversation_text += '- Response: {"action": "complete_todo", "title": "Buy groceries", "response": "I\'ve marked \'Buy groceries\' as complete."}\n\n'

    conversation_text += "- User: 'Show my todos'\n"
    conversation_text += '- Response: {"action": "list_todos", "response": "Here are your todos..."}\n\n'

    conversation_text += "- User: 'Create a recurring task: Water plants daily'\n"
    conversation_text += '''- Response: {"action": "create_recurring_task", "title": "Water plants", "recurrence_pattern": "daily", "response": "I've created a recurring task to water plants daily."}\n\n'''

    conversation_text += "Always respond in valid JSON format only.\n\n"

    # Add conversation history if available
    if conversation_history:
        for msg in conversation_history:
            role = "Assistant" if msg.role == "assistant" else "User"
            conversation_text += f"{role}: {msg.content}\n"

    # Add the current user message
    conversation_text += f"User: {message}\n"
    conversation_text += "Assistant:"

    try:
        # Call Gemini API to interpret the user's intent
        try:
            response = gemini_model.generate_content(conversation_text)
            # Extract the AI's response
            ai_response = response.text.strip()
        except Exception as gemini_error:
            print(f"Gemini API error: {str(gemini_error)}")
            print("Using fallback rule-based processing...")
            # Fall back to rule-based processing if Gemini API fails
            return process_natural_language_command_fallback(message, session, conversation_id, user_id, conversation_history)

        # Parse the JSON response from the AI
        try:
            # Try to extract JSON from the response if it contains extra text
            # Look for JSON between curly braces, handling nested braces properly
            # First, try to parse the whole response as JSON
            try:
                parsed_response = json.loads(ai_response)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from the response
                # Find the outermost JSON object by counting braces
                brace_count = 0
                start_idx = -1

                for i, char in enumerate(ai_response):
                    if char == '{':
                        if brace_count == 0:
                            start_idx = i
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0 and start_idx != -1:
                            # Found a complete JSON object
                            json_str = ai_response[start_idx:i+1]
                            try:
                                parsed_response = json.loads(json_str)
                                break
                            except json.JSONDecodeError:
                                # If this JSON is invalid, continue looking
                                start_idx = -1
                                continue
                else:
                    # If we couldn't find a valid JSON object, return an error
                    return "I'm having trouble understanding your request. Could you please rephrase it?", "error", None
        except Exception as e:
            # If JSON parsing fails for any reason, return an error
            print(f"JSON parsing error: {str(e)}")
            print(f"Raw Gemini response: {ai_response}")
            return "I'm having trouble understanding your request. Could you please rephrase it?", "error", None

        action = parsed_response.get("action", "unknown_command")
        title = parsed_response.get("title")
        response_text = parsed_response.get("response", "I processed your request.")
        priority = parsed_response.get("priority", "medium")
        tags = parsed_response.get("tags", [])
        due_date = parsed_response.get("due_date")
        recurrence_pattern = parsed_response.get("recurrence_pattern")

        # Execute the appropriate action based on the AI's interpretation
        if action == "create_todo":
            if title:
                try:
                    # Create the todo
                    todo = TodoMCPTools.create_todo(
                        title=title,
                        description=parsed_response.get("description"),
                        user_id=str(user_id)  # Use the actual user ID from the session
                    )
                    return response_text, "todo_created", {
                        "id": todo['id'],
                        "title": todo['title'],
                        "status": todo['status']
                    }
                except Exception as e:
                    return "Sorry, I'm having trouble connecting to the todo service right now. Please try again later.", "service_unavailable", None
            else:
                return "I couldn't understand the todo title. Please try again.", "error", None

        elif action == "create_todo_with_priority":
            if title:
                try:
                    # Create the todo with advanced features
                    todo = TodoMCPTools.create_todo_with_priority(
                        title=title,
                        description=parsed_response.get("description"),
                        user_id=str(user_id),
                        priority=priority,
                        tags=tags,
                        due_date=due_date,
                        recurrence_pattern=recurrence_pattern
                    )
                    return response_text, "todo_created", {
                        "id": todo['id'],
                        "title": todo['title'],
                        "status": todo['status'],
                        "priority": todo.get('priority'),
                        "tags": todo.get('tags'),
                        "dueDate": todo.get('dueDate'),
                        "recurrencePattern": todo.get('recurrencePattern')
                    }
                except Exception as e:
                    return "Sorry, I'm having trouble connecting to the todo service right now. Please try again later.", "service_unavailable", None
            else:
                return "I couldn't understand the todo title. Please try again.", "error", None

        elif action == "create_recurring_task":
            if title and recurrence_pattern:
                try:
                    # Create a recurring task
                    todo = TodoMCPTools.create_recurring_task(
                        title=title,
                        description=parsed_response.get("description"),
                        user_id=str(user_id),
                        priority=priority,
                        tags=tags,
                        due_date=due_date,
                        recurrence_pattern=recurrence_pattern
                    )
                    return response_text, "recurring_task_created", {
                        "id": todo['id'],
                        "title": todo['title'],
                        "status": todo['status'],
                        "recurrencePattern": todo.get('recurrencePattern')
                    }
                except Exception as e:
                    return "Sorry, I'm having trouble connecting to the todo service right now. Please try again later.", "service_unavailable", None
            else:
                return "I couldn't understand the recurring task details. Please specify both the task and the recurrence pattern.", "error", None

        elif action == "cancel_recurring_series":
            if title:
                # Find the recurring todo by title
                todos = session.exec(
                    select(Todo).where(
                        Todo.title.contains(title),  # Use contains to find similar titles
                        Todo.user_id == user_id,  # Use the actual user ID from the session
                        Todo.recurrence_pattern.is_not(None)  # Only recurring tasks
                    )
                ).all()

                if todos:
                    # If multiple todos match, check for exact match first
                    exact_match = None
                    for todo in todos:
                        if todo.title.lower() == title.lower():
                            exact_match = todo
                            break

                    if exact_match:
                        # Use the exact match
                        todo = exact_match
                    elif len(todos) == 1:
                        # If only one similar match, use it
                        todo = todos[0]
                    else:
                        # If multiple matches, ask for clarification
                        todo_titles = [f"'{todo.title}'" for todo in todos[:5]]  # Limit to first 5
                        titles_str = ", ".join(todo_titles)
                        return f"I found multiple recurring tasks with similar titles: {titles_str}. Could you please specify which one you mean?", "disambiguation_needed", None

                    try:
                        result = TodoMCPTools.cancel_recurring_series(str(todo.id), str(user_id))
                        if result['success']:
                            return response_text, "recurring_task_cancelled", {
                                "id": str(todo.id),
                                "title": todo.title
                            }
                        else:
                            return f"I couldn't cancel the recurring task '{title}'.", "error", None
                    except Exception:
                        return "Sorry, I'm having trouble connecting to the todo service right now. Please try again later.", "service_unavailable", None
                else:
                    return f"I couldn't find a recurring task with the title '{title}'.", "error", None
            else:
                return "I couldn't understand which recurring task to cancel. Please specify the title.", "error", None

        elif action == "complete_todo":
            if title:
                # Find the todo by title
                todos = session.exec(
                    select(Todo).where(
                        Todo.title.contains(title),  # Use contains to find similar titles
                        Todo.user_id == user_id  # Use the actual user ID from the session
                    )
                ).all()

                if todos:
                    # If multiple todos match, check for exact match first
                    exact_match = None
                    for todo in todos:
                        if todo.title.lower() == title.lower():
                            exact_match = todo
                            break

                    if exact_match:
                        # Use the exact match
                        todo = exact_match
                    elif len(todos) == 1:
                        # If only one similar match, use it
                        todo = todos[0]
                    else:
                        # If multiple matches, ask for clarification
                        todo_titles = [f"'{todo.title}'" for todo in todos[:5]]  # Limit to first 5
                        titles_str = ", ".join(todo_titles)
                        return f"I found multiple todos with similar titles: {titles_str}. Could you please specify which one you mean?", "disambiguation_needed", None

                    try:
                        updated_todo = TodoMCPTools.mark_todo_completed(str(todo.id))
                        return response_text, "todo_completed", {
                            "id": updated_todo['id'],
                            "title": updated_todo['title'],
                            "status": updated_todo['status']
                        }
                    except Exception:
                        return "Sorry, I'm having trouble connecting to the todo service right now. Please try again later.", "service_unavailable", None
                else:
                    return f"I couldn't find a todo with the title '{title}'.", "error", None
            else:
                return "I couldn't understand which todo to complete. Please specify the title.", "error", None

        elif action == "delete_todo":
            if title:
                # Find the todo by title
                todos = session.exec(
                    select(Todo).where(
                        Todo.title.contains(title),  # Use contains to find similar titles
                        Todo.user_id == user_id  # Use the actual user ID from the session
                    )
                ).all()

                if todos:
                    # If multiple todos match, check for exact match first
                    exact_match = None
                    for todo in todos:
                        if todo.title.lower() == title.lower():
                            exact_match = todo
                            break

                    if exact_match:
                        # Use the exact match
                        todo = exact_match
                    elif len(todos) == 1:
                        # If only one similar match, use it
                        todo = todos[0]
                    else:
                        # If multiple matches, ask for clarification
                        todo_titles = [f"'{todo.title}'" for todo in todos[:5]]  # Limit to first 5
                        titles_str = ", ".join(todo_titles)
                        return f"I found multiple todos with similar titles: {titles_str}. Could you please specify which one you mean?", "disambiguation_needed", None

                    try:
                        result = TodoMCPTools.delete_todo(str(todo.id))
                        if result['success']:
                            return response_text, "todo_deleted", {
                                "id": str(todo.id),
                                "title": todo.title
                            }
                        else:
                            return f"I couldn't delete the todo '{title}'.", "error", None
                    except Exception:
                        return "Sorry, I'm having trouble connecting to the todo service right now. Please try again later.", "service_unavailable", None
                else:
                    return f"I couldn't find a todo with the title '{title}'.", "error", None
            else:
                return "I couldn't understand which todo to delete. Please specify the title.", "error", None

        elif action == "list_todos":
            todos = session.exec(
                select(Todo).where(
                    Todo.user_id == user_id  # Use the actual user ID from the session
                )
            ).all()

            if todos:
                todo_list = [f"- {todo.title} ({todo.status})" for todo in todos]
                todo_str = "\n".join(todo_list)
                return response_text, "show_todos", {
                    "todos": [{"id": str(todo.id), "title": todo.title, "status": todo.status} for todo in todos]
                }
            else:
                return response_text, "show_todos", {"todos": []}

        elif action == "search_todos":
            keyword = title  # Using title field to pass the search keyword
            if keyword:
                try:
                    todos = TodoMCPTools.search_todos(str(user_id), keyword)
                    if todos:
                        todo_list = [f"- {todo['title']} ({todo['status']})" for todo in todos]
                        todo_str = "\n".join(todo_list)
                        return response_text, "search_results", {
                            "todos": todos
                        }
                    else:
                        return f"I couldn't find any todos matching '{keyword}'.", "search_results", {"todos": []}
                except Exception:
                    return "Sorry, I'm having trouble connecting to the todo service right now. Please try again later.", "service_unavailable", None
            else:
                return "I couldn't understand what to search for. Please specify a keyword.", "error", None

        elif action == "filter_todos":
            # Extract filter parameters from the parsed response
            status = parsed_response.get("status")
            priority = parsed_response.get("priority")
            tags = parsed_response.get("tags", [])

            try:
                todos = TodoMCPTools.filter_todos(str(user_id), status, priority, tags)
                if todos:
                    todo_list = [f"- {todo['title']} ({todo['status']})" for todo in todos]
                    todo_str = "\n".join(todo_list)
                    return response_text, "filter_results", {
                        "todos": todos
                    }
                else:
                    return "I couldn't find any todos matching your filters.", "filter_results", {"todos": []}
            except Exception:
                return "Sorry, I'm having trouble connecting to the todo service right now. Please try again later.", "service_unavailable", None

        elif action == "sort_todos":
            sort_by = parsed_response.get("sort_by", "created_at")
            sort_order = parsed_response.get("sort_order", "desc")

            try:
                todos = TodoMCPTools.sort_todos(str(user_id), sort_by, sort_order)
                if todos:
                    todo_list = [f"- {todo['title']} ({todo['status']})" for todo in todos]
                    todo_str = "\n".join(todo_list)
                    return response_text, "sort_results", {
                        "todos": todos
                    }
                else:
                    return "You don't have any todos to sort.", "sort_results", {"todos": []}
            except Exception:
                return "Sorry, I'm having trouble connecting to the todo service right now. Please try again later.", "service_unavailable", None

        else:
            # For unknown commands or other actions
            return response_text, action, None

    except Exception as e:
        # If there's an error with the Gemini service, fall back to the original rule-based approach
        print(f"Error with Gemini API: {str(e)}")
        # Fallback to the original rule-based approach
        return process_natural_language_command_fallback(message, session, conversation_id, user_id, conversation_history)


def process_natural_language_command_fallback(message: str, session: Session, conversation_id: UUID, user_id: UUID, conversation_history=None):
    """
    Process natural language commands using rule-based approach (fallback).
    """
    # If conversation history is provided, try to resolve references to previous messages/todos
    if conversation_history:
        # Try to resolve pronouns like "that one" or "it" to specific todos
        message = resolve_references_in_message(message, conversation_history, session)

    # Normalize the message
    message = message.strip().lower()

    # Pattern matching for different commands
    # Add todo: "add a todo: [title]", "create todo: [title]", "add todo [title]", or just "add [title]"
    # More flexible pattern to match variations like "add buy groceries"
    add_todo_pattern = r"(add a todo:|create todo:|add todo:|add todo\s+|create todo\s+|add\s+)(.+)"
    match = re.match(add_todo_pattern, message)
    if match:
        title = match.group(2).strip()
        if title:
            try:
                # Create the todo
                todo = TodoMCPTools.create_todo(
                    title=title,
                    user_id=str(user_id)  # Use the actual user ID from the session
                )
                return f"I've added '{todo['title']}' to your todo list.", "todo_created", {
                    "id": todo['id'],
                    "title": todo['title'],
                    "status": todo['status']
                }
            except Exception as e:
                print(f"Error creating todo: {str(e)}")  # Add logging for debugging
                return "Sorry, I'm having trouble connecting to the todo service right now. Please try again later.", "service_unavailable", None
        else:
            return "I couldn't understand the todo title. Please try again.", "error", None

    # Additional pattern for simple "add [title]" format
    simple_add_pattern = r"^add\s+(.+)$"
    match = re.match(simple_add_pattern, message)
    if match and not match.group(1).startswith("a ") and not match.group(1).startswith("todo"):
        title = match.group(1).strip()
        if title:
            try:
                # Create the todo
                todo = TodoMCPTools.create_todo(
                    title=title,
                    user_id=str(user_id)  # Use the actual user ID from the session
                )
                return f"I've added '{todo['title']}' to your todo list.", "todo_created", {
                    "id": todo['id'],
                    "title": todo['title'],
                    "status": todo['status']
                }
            except Exception as e:
                print(f"Error creating todo: {str(e)}")  # Add logging for debugging
                return "Sorry, I'm having trouble connecting to the todo service right now. Please try again later.", "service_unavailable", None

    # Mark todo as complete: "mark '[title]' as complete" or "complete '[title]'"
    mark_complete_pattern = r"(mark|complete)\s*'([^']+)'\s*(as complete)?"
    match = re.match(mark_complete_pattern, message)
    if match:
        title = match.group(2).strip()
        # Find the todo by title
        todos = session.exec(
            select(Todo).where(
                Todo.title.contains(title),  # Use contains to find similar titles
                Todo.user_id == user_id  # Use the actual user ID from the session
            )
        ).all()

        if todos:
            # If multiple todos match, check for exact match first
            exact_match = None
            for todo in todos:
                if todo.title.lower() == title.lower():
                    exact_match = todo
                    break

            if exact_match:
                # Use the exact match
                todo = exact_match
            elif len(todos) == 1:
                # If only one similar match, use it
                todo = todos[0]
            else:
                # If multiple matches, ask for clarification
                todo_titles = [f"'{todo.title}'" for todo in todos[:5]]  # Limit to first 5
                titles_str = ", ".join(todo_titles)
                return f"I found multiple todos with similar titles: {titles_str}. Could you please specify which one you mean?", "disambiguation_needed", None

            try:
                updated_todo = TodoMCPTools.mark_todo_completed(str(todo.id))
                return f"I've marked '{updated_todo['title']}' as complete.", "todo_completed", {
                    "id": updated_todo['id'],
                    "title": updated_todo['title'],
                    "status": updated_todo['status']
                }
            except Exception:
                return "Sorry, I'm having trouble connecting to the todo service right now. Please try again later.", "service_unavailable", None
        else:
            return f"I couldn't find a todo with the title '{title}'.", "error", None

    # Delete todo: "delete '[title]'" or "remove '[title]'"
    delete_pattern = r"(delete|remove)\s*'([^']+)'"
    match = re.match(delete_pattern, message)
    if match:
        title = match.group(2).strip()
        # Find the todo by title
        todos = session.exec(
            select(Todo).where(
                Todo.title.contains(title),  # Use contains to find similar titles
                Todo.user_id == user_id  # Use the actual user ID from the session
            )
        ).all()

        if todos:
            # If multiple todos match, check for exact match first
            exact_match = None
            for todo in todos:
                if todo.title.lower() == title.lower():
                    exact_match = todo
                    break

            if exact_match:
                # Use the exact match
                todo = exact_match
            elif len(todos) == 1:
                # If only one similar match, use it
                todo = todos[0]
            else:
                # If multiple matches, ask for clarification
                todo_titles = [f"'{todo.title}'" for todo in todos[:5]]  # Limit to first 5
                titles_str = ", ".join(todo_titles)
                return f"I found multiple todos with similar titles: {titles_str}. Could you please specify which one you mean?", "disambiguation_needed", None

            try:
                result = TodoMCPTools.delete_todo(str(todo.id))
                if result['success']:
                    return f"I've deleted '{todo.title}' from your todo list.", "todo_deleted", {
                        "id": str(todo.id),
                        "title": todo.title
                    }
                else:
                    return f"I couldn't delete the todo '{title}'.", "error", None
            except Exception:
                return "Sorry, I'm having trouble connecting to the todo service right now. Please try again later.", "service_unavailable", None
        else:
            return f"I couldn't find a todo with the title '{title}'.", "error", None

    # Show todos: "show my todos" or "what are my todos?"
    show_pattern = r"(show|list|what are)\s*(my\s*)?todos"
    if re.match(show_pattern, message):
        from models.todo import Todo
        from sqlmodel import select

        todos = session.exec(
            select(Todo).where(
                Todo.user_id == user_id  # Use the actual user ID from the session
            )
        ).all()

        if todos:
            todo_list = [f"- {todo.title} ({todo.status})" for todo in todos]
            todo_str = "\n".join(todo_list)
            return f"Here are your todos:\n{todo_str}", "show_todos", {
                "todos": [{"id": str(todo.id), "title": todo.title, "status": todo.status} for todo in todos]
            }
        else:
            return "You don't have any todos yet.", "show_todos", {"todos": []}

    # Default response for unrecognized commands
    # Ask clarifying questions for ambiguous requests
    if any(word in message for word in ["it", "that", "this", "the", "one"]):
        return "I'm not sure what you're referring to. Could you please be more specific about which todo you'd like me to work with?", "clarification_needed", None

    return "I'm not sure how to help with that. You can ask me to add a todo, mark a todo as complete, or show your todos.", "unknown_command", None


def resolve_references_in_message(message: str, conversation_history, session: Session):
    """
    Resolve references in the message like "that one" or "it" to specific todos
    based on the conversation history.
    """
    # If the message contains reference terms, try to resolve them
    if "that one" in message or "that" in message or "it" in message:
        # Get the most recent todo mentioned in the conversation
        for msg in reversed(conversation_history):
            if msg.role == "assistant" and "todo" in msg.content.lower():
                # Extract the todo title from the assistant's response
                import re
                # Look for patterns like "I've added 'Buy groceries' to your todo list"
                match = re.search(r"'([^']*)'", msg.content)
                if match:
                    referenced_title = match.group(1)
                    # Replace reference in the user's message with the actual title
                    message = message.replace("that one", f"'{referenced_title}'")
                    message = message.replace("that", f"'{referenced_title}'")
                    message = message.replace("it", f"'{referenced_title}'")
                    break

    return message