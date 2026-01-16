from typing import Optional
from uuid import UUID
from models.todo import Todo
from services.todo_service import TodoService
from database import get_session
from sqlmodel import Session, select
import json
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import analytics service
from analytics import analytics_service


class TodoMCPTools:
    """
    MCP tools for todo operations following the Model Context Protocol.
    These tools are stateless and interact directly with the database.
    """

    @staticmethod
    def create_todo(title: str, description: Optional[str] = None, user_id: str = None) -> dict:
        """
        Creates a new todo using the Todo model for consistency with frontend.

        Args:
            title: The title of the todo
            description: Optional description of the todo
            user_id: ID of the user creating the todo

        Returns:
            A dictionary representation of the created Todo object
        """
        logger.info(f"MCP Tool: Creating todo with title '{title}' for user {user_id}")

        try:
            with next(get_session()) as session:
                # Import Todo model from models
                from models.todo import Todo as TodoModel
                from uuid import UUID
                user_uuid = UUID(user_id) if user_id else UUID(int=0)  # Use a default UUID if none provided

                # Create using the Todo model to match what the frontend expects
                todo = TodoModel(
                    title=title,
                    description=description,
                    user_id=user_uuid,
                    status="pending"  # Default status
                )

                session.add(todo)
                session.commit()
                session.refresh(todo)

                logger.info(f"MCP Tool: Successfully created todo with ID {todo.id}")

                # Track the todo creation event
                analytics_service.track_todo_operation(
                    operation="create",
                    user_id=str(user_uuid) if user_id else "unknown",
                    conversation_id="unknown",  # This would be passed from the chatbot endpoint
                    todo_data={
                        "id": str(todo.id),
                        "title": todo.title,
                        "description": todo.description,
                        "status": todo.status
                    }
                )

                # Return a dictionary representation following strict MCP contracts
                todo_dict = {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status,
                    "userId": str(todo.user_id),
                    "createdAt": todo.created_at.isoformat(),
                    "completedAt": todo.completed_at.isoformat() if todo.completed_at else None
                }

                return todo_dict
        except Exception as e:
            logger.error(f"MCP Tool: Error creating todo with title '{title}': {str(e)}")

            # Track the error
            analytics_service.track_error(
                user_id=user_id or "unknown",
                conversation_id="unknown",
                error_message=str(e),
                error_type=type(e).__name__
            )
            raise e

    @staticmethod
    def update_todo(todo_id: str, title: Optional[str] = None, description: Optional[str] = None, status: Optional[str] = None) -> Optional[dict]:
        """
        Updates an existing todo using the Todo model for consistency with frontend.

        Args:
            todo_id: The ID of the todo to update
            title: New title (optional)
            description: New description (optional)
            status: New status (pending/completed) (optional)

        Returns:
            A dictionary representation of the updated Todo object or None if not found
        """
        logger.info(f"MCP Tool: Updating todo with ID {todo_id}")

        try:
            with next(get_session()) as session:
                # Import Todo model from models
                from models.todo import Todo as TodoModel
                from uuid import UUID
                todo_uuid = UUID(todo_id)

                # Query the Todo model
                todo = session.get(TodoModel, todo_uuid)

                if not todo:
                    logger.warning(f"MCP Tool: Todo with ID {todo_id} not found for update")
                    return None

                # Update the fields if provided
                if title is not None:
                    todo.title = title
                if description is not None:
                    todo.description = description
                if status is not None:
                    todo.status = status

                session.add(todo)
                session.commit()
                session.refresh(todo)

                logger.info(f"MCP Tool: Successfully updated todo with ID {todo.id}")

                # Track the todo update event
                analytics_service.track_todo_operation(
                    operation="update",
                    user_id=str(todo.user_id),
                    conversation_id="unknown",  # This would be passed from the chatbot endpoint
                    todo_data={
                        "id": str(todo.id),
                        "title": todo.title,
                        "description": todo.description,
                        "status": todo.status
                    }
                )

                # Return a dictionary representation following strict MCP contracts
                todo_dict = {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status,
                    "userId": str(todo.user_id),
                    "createdAt": todo.created_at.isoformat(),
                    "completedAt": todo.completed_at.isoformat() if todo.completed_at else None
                }

                return todo_dict
        except Exception as e:
            logger.error(f"MCP Tool: Error updating todo with ID {todo_id}: {str(e)}")

            # Track the error
            analytics_service.track_error(
                user_id="unknown",
                conversation_id="unknown",
                error_message=str(e),
                error_type=type(e).__name__
            )
            raise e

    @staticmethod
    def delete_todo(todo_id: str) -> dict:
        """
        Deletes a todo using the Todo model for consistency with frontend.

        Args:
            todo_id: The ID of the todo to delete

        Returns:
            A dictionary with the deletion result
        """
        logger.info(f"MCP Tool: Deleting todo with ID {todo_id}")

        try:
            with next(get_session()) as session:
                # Import Todo model from models
                from models.todo import Todo as TodoModel
                from uuid import UUID
                todo_uuid = UUID(todo_id)

                # Get the todo before deletion to track its data
                todo_to_delete = session.get(TodoModel, todo_uuid)

                if todo_to_delete:
                    session.delete(todo_to_delete)
                    session.commit()

                    logger.info(f"MCP Tool: Successfully deleted todo with ID {todo_id}")

                    # Track the todo deletion event
                    analytics_service.track_todo_operation(
                        operation="delete",
                        user_id=str(todo_to_delete.user_id) if todo_to_delete else "unknown",
                        conversation_id="unknown",  # This would be passed from the chatbot endpoint
                        todo_data={
                            "id": todo_id,
                            "title": todo_to_delete.title if todo_to_delete else "unknown",
                            "description": todo_to_delete.description if todo_to_delete else "unknown",
                            "status": todo_to_delete.status
                        }
                    )

                    return {
                        "success": True,
                        "deleted_id": todo_id
                    }
                else:
                    logger.warning(f"MCP Tool: Failed to delete todo with ID {todo_id} - not found")
                    return {
                        "success": False,
                        "deleted_id": todo_id
                    }
        except Exception as e:
            logger.error(f"MCP Tool: Error deleting todo with ID {todo_id}: {str(e)}")

            # Track the error
            analytics_service.track_error(
                user_id="unknown",
                conversation_id="unknown",
                error_message=str(e),
                error_type=type(e).__name__
            )
            raise e

    @staticmethod
    def mark_todo_completed(todo_id: str) -> Optional[dict]:
        """
        Marks a todo as completed using the Todo model for consistency with frontend.

        Args:
            todo_id: The ID of the todo to mark as completed

        Returns:
            A dictionary representation of the updated Todo object or None if not found
        """
        logger.info(f"MCP Tool: Marking todo with ID {todo_id} as completed")

        try:
            with next(get_session()) as session:
                # Import Todo model from models
                from models.todo import Todo as TodoModel
                from uuid import UUID
                from datetime import datetime
                todo_uuid = UUID(todo_id)

                # Get the todo to update
                todo = session.get(TodoModel, todo_uuid)

                if not todo:
                    logger.warning(f"MCP Tool: Todo with ID {todo_id} not found for completion")
                    return None

                # Mark as completed
                todo.status = "completed"
                todo.completed_at = datetime.utcnow()
                session.add(todo)
                session.commit()
                session.refresh(todo)

                logger.info(f"MCP Tool: Successfully marked todo with ID {todo.id} as completed")

                # Track the todo completion event
                analytics_service.track_todo_operation(
                    operation="completed",
                    user_id=str(todo.user_id),
                    conversation_id="unknown",  # This would be passed from the chatbot endpoint
                    todo_data={
                        "id": str(todo.id),
                        "title": todo.title,
                        "description": todo.description,
                        "status": todo.status
                    }
                )

                # Return a dictionary representation following strict MCP contracts
                todo_dict = {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status,
                    "userId": str(todo.user_id),
                    "createdAt": todo.created_at.isoformat(),
                    "completedAt": todo.completed_at.isoformat() if todo.completed_at else None
                }

                return todo_dict
        except Exception as e:
            logger.error(f"MCP Tool: Error marking todo with ID {todo_id} as completed: {str(e)}")

            # Track the error
            analytics_service.track_error(
                user_id="unknown",
                conversation_id="unknown",
                error_message=str(e),
                error_type=type(e).__name__
            )
            raise e

    @staticmethod
    def mark_todo_pending(todo_id: str) -> Optional[dict]:
        """
        Marks a todo as pending using the Todo model for consistency with frontend.

        Args:
            todo_id: The ID of the todo to mark as pending

        Returns:
            A dictionary representation of the updated Todo object or None if not found
        """
        logger.info(f"MCP Tool: Marking todo with ID {todo_id} as pending")

        try:
            with next(get_session()) as session:
                # Import Todo model from models
                from models.todo import Todo as TodoModel
                from uuid import UUID
                todo_uuid = UUID(todo_id)

                # Get the todo to update
                todo = session.get(TodoModel, todo_uuid)

                if not todo:
                    logger.warning(f"MCP Tool: Todo with ID {todo_id} not found for pending update")
                    return None

                # Mark as pending
                todo.status = "pending"
                todo.completed_at = None
                session.add(todo)
                session.commit()
                session.refresh(todo)

                logger.info(f"MCP Tool: Successfully marked todo with ID {todo.id} as pending")

                # Track the todo pending event
                analytics_service.track_todo_operation(
                    operation="pending",
                    user_id=str(todo.user_id),
                    conversation_id="unknown",  # This would be passed from the chatbot endpoint
                    todo_data={
                        "id": str(todo.id),
                        "title": todo.title,
                        "description": todo.description,
                        "status": todo.status
                    }
                )

                # Return a dictionary representation following strict MCP contracts
                todo_dict = {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status,
                    "userId": str(todo.user_id),
                    "createdAt": todo.created_at.isoformat(),
                    "completedAt": todo.completed_at.isoformat() if todo.completed_at else None
                }

                return todo_dict
        except Exception as e:
            logger.error(f"MCP Tool: Error marking todo with ID {todo_id} as pending: {str(e)}")

            # Track the error
            analytics_service.track_error(
                user_id="unknown",
                conversation_id="unknown",
                error_message=str(e),
                error_type=type(e).__name__
            )
            raise e