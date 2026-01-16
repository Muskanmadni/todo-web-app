from typing import Optional
from uuid import UUID
import uuid
from models.todo import Todo
from services.todo_service import TodoService
from database import get_session
from sqlmodel import Session, select
import json
from datetime import datetime
import logging

# Import the Task model from main.py to ensure consistency
from main import Task as TaskModel
from main import TaskResponse, PriorityEnum

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
        Creates a new todo item using the Task model for consistency with frontend.

        Args:
            title: The title of the todo
            description: Optional description of the todo
            user_id: ID of the user creating the todo

        Returns:
            A dictionary representation of the created Task object
        """
        logger.info(f"MCP Tool: Creating task with title '{title}' for user {user_id}")

        try:
            with next(get_session()) as session:
                # In a real implementation, user_id would be validated against the authenticated user
                # For now, we'll use a placeholder UUID
                from uuid import uuid4
                user_uuid = UUID(user_id) if user_id else uuid4()

                # Create using the Task model to match what the frontend expects
                from datetime import datetime

                task = TaskModel(
                    title=title,
                    description=description,
                    completed=False,  # Default to not completed
                    due_date=None,    # No due date by default
                    priority=PriorityEnum.medium,  # Default priority
                    user_id=user_uuid,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

                session.add(task)
                session.commit()
                session.refresh(task)

                logger.info(f"MCP Tool: Successfully created task with ID {task.id}")

                # Track the task creation event
                analytics_service.track_todo_operation(
                    operation="create",
                    user_id=str(user_uuid) if user_id else "unknown",
                    conversation_id="unknown",  # This would be passed from the chatbot endpoint
                    todo_data={
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": "completed" if task.completed else "pending"
                    }
                )

                # Convert to TaskResponse format for consistency with API
                task_response = TaskResponse(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    completed=task.completed,
                    due_date=task.due_date,
                    priority=task.priority,
                    user_id=task.user_id,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                )

                # Return a dictionary representation following strict MCP contracts
                task_dict = task_response.dict()
                # Convert datetime objects to ISO format strings
                task_dict["created_at"] = task.created_at.isoformat()
                task_dict["updated_at"] = task.updated_at.isoformat()
                if task.due_date:
                    task_dict["due_date"] = task.due_date.isoformat()

                return task_dict
        except Exception as e:
            logger.error(f"MCP Tool: Error creating task with title '{title}': {str(e)}")

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
        Updates an existing task using the Task model for consistency with frontend.

        Args:
            todo_id: The ID of the task to update
            title: New title (optional)
            description: New description (optional)
            status: New status (pending/completed) (optional)

        Returns:
            A dictionary representation of the updated Task object or None if not found
        """
        logger.info(f"MCP Tool: Updating task with ID {todo_id}")

        try:
            with next(get_session()) as session:
                task_uuid = UUID(todo_id)
                
                # Query the Task model instead of Todo
                task = session.get(TaskModel, task_uuid)
                
                if not task:
                    logger.warning(f"MCP Tool: Task with ID {todo_id} not found for update")
                    return None

                # Update the fields if provided
                if title is not None:
                    task.title = title
                if description is not None:
                    task.description = description
                if status is not None:
                    task.completed = (status == "completed")

                session.add(task)
                session.commit()
                session.refresh(task)

                logger.info(f"MCP Tool: Successfully updated task with ID {task.id}")

                # Convert to TaskResponse format for consistency with API
                task_response = TaskResponse(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    completed=task.completed,
                    due_date=task.due_date,
                    priority=task.priority,
                    user_id=task.user_id,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                )

                # Return a dictionary representation following strict MCP contracts
                task_dict = task_response.dict()
                # Convert datetime objects to ISO format strings
                task_dict["created_at"] = task.created_at.isoformat()
                task_dict["updated_at"] = task.updated_at.isoformat()
                if task.due_date:
                    task_dict["due_date"] = task.due_date.isoformat()
                
                # Track the task update event
                analytics_service.track_todo_operation(
                    operation="update",
                    user_id=str(task.user_id),
                    conversation_id="unknown",  # This would be passed from the chatbot endpoint
                    todo_data={
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": "completed" if task.completed else "pending"
                    }
                )

                return task_dict
        except Exception as e:
            logger.error(f"MCP Tool: Error updating task with ID {todo_id}: {str(e)}")

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
        Deletes a task using the Task model for consistency with frontend.

        Args:
            todo_id: The ID of the task to delete

        Returns:
            A dictionary with the deletion result
        """
        logger.info(f"MCP Tool: Deleting task with ID {todo_id}")

        try:
            with next(get_session()) as session:
                task_uuid = UUID(todo_id)

                # Get the task before deletion to track its data
                task_to_delete = session.get(TaskModel, task_uuid)

                if task_to_delete:
                    session.delete(task_to_delete)
                    session.commit()

                    logger.info(f"MCP Tool: Successfully deleted task with ID {todo_id}")

                    # Track the task deletion event
                    analytics_service.track_todo_operation(
                        operation="delete",
                        user_id=str(task_to_delete.user_id) if task_to_delete else "unknown",
                        conversation_id="unknown",  # This would be passed from the chatbot endpoint
                        todo_data={
                            "id": todo_id,
                            "title": task_to_delete.title if task_to_delete else "unknown",
                            "description": task_to_delete.description if task_to_delete else "unknown",
                            "status": "completed" if task_to_delete.completed else "pending"
                        }
                    )
                    
                    return {
                        "success": True,
                        "deleted_id": todo_id
                    }
                else:
                    logger.warning(f"MCP Tool: Failed to delete task with ID {todo_id} - not found")
                    return {
                        "success": False,
                        "deleted_id": todo_id
                    }
        except Exception as e:
            logger.error(f"MCP Tool: Error deleting task with ID {todo_id}: {str(e)}")

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
        Marks a task as completed using the Task model for consistency with frontend.

        Args:
            todo_id: The ID of the task to mark as completed

        Returns:
            A dictionary representation of the updated Task object or None if not found
        """
        logger.info(f"MCP Tool: Marking task with ID {todo_id} as completed")

        try:
            with next(get_session()) as session:
                task_uuid = UUID(todo_id)
                
                # Get the task to update
                task = session.get(TaskModel, task_uuid)
                
                if not task:
                    logger.warning(f"MCP Tool: Task with ID {todo_id} not found for completion")
                    return None

                # Mark as completed
                task.completed = True
                session.add(task)
                session.commit()
                session.refresh(task)

                logger.info(f"MCP Tool: Successfully marked task with ID {task.id} as completed")

                # Convert to TaskResponse format for consistency with API
                task_response = TaskResponse(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    completed=task.completed,
                    due_date=task.due_date,
                    priority=task.priority,
                    user_id=task.user_id,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                )

                # Return a dictionary representation following strict MCP contracts
                task_dict = task_response.dict()
                # Convert datetime objects to ISO format strings
                task_dict["created_at"] = task.created_at.isoformat()
                task_dict["updated_at"] = task.updated_at.isoformat()
                if task.due_date:
                    task_dict["due_date"] = task.due_date.isoformat()

                # Track the task completion event
                analytics_service.track_todo_operation(
                    operation="completed",
                    user_id=str(task.user_id),
                    conversation_id="unknown",  # This would be passed from the chatbot endpoint
                    todo_data={
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": "completed" if task.completed else "pending"
                    }
                )

                return task_dict
        except Exception as e:
            logger.error(f"MCP Tool: Error marking task with ID {todo_id} as completed: {str(e)}")

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
        Marks a task as pending using the Task model for consistency with frontend.

        Args:
            todo_id: The ID of the task to mark as pending

        Returns:
            A dictionary representation of the updated Task object or None if not found
        """
        logger.info(f"MCP Tool: Marking task with ID {todo_id} as pending")

        try:
            with next(get_session()) as session:
                task_uuid = UUID(todo_id)
                
                # Get the task to update
                task = session.get(TaskModel, task_uuid)
                
                if not task:
                    logger.warning(f"MCP Tool: Task with ID {todo_id} not found for pending update")
                    return None

                # Mark as pending
                task.completed = False
                session.add(task)
                session.commit()
                session.refresh(task)

                logger.info(f"MCP Tool: Successfully marked task with ID {task.id} as pending")

                # Convert to TaskResponse format for consistency with API
                task_response = TaskResponse(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    completed=task.completed,
                    due_date=task.due_date,
                    priority=task.priority,
                    user_id=task.user_id,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                )

                # Return a dictionary representation following strict MCP contracts
                task_dict = task_response.dict()
                # Convert datetime objects to ISO format strings
                task_dict["created_at"] = task.created_at.isoformat()
                task_dict["updated_at"] = task.updated_at.isoformat()
                if task.due_date:
                    task_dict["due_date"] = task.due_date.isoformat()

                # Track the task pending event
                analytics_service.track_todo_operation(
                    operation="pending",
                    user_id=str(task.user_id),
                    conversation_id="unknown",  # This would be passed from the chatbot endpoint
                    todo_data={
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": "completed" if task.completed else "pending"
                    }
                )

                return task_dict
        except Exception as e:
            logger.error(f"MCP Tool: Error marking task with ID {todo_id} as pending: {str(e)}")

            # Track the error
            analytics_service.track_error(
                user_id="unknown",
                conversation_id="unknown",
                error_message=str(e),
                error_type=type(e).__name__
            )
            raise e