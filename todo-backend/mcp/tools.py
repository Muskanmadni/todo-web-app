from typing import Optional, List
from uuid import UUID
from models.todo import Todo, Priority as PriorityEnum
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
                        "status": todo.status,
                        "userId": str(todo.user_id),
                        "createdAt": todo.created_at.isoformat(),
                        "completedAt": todo.completed_at.isoformat() if todo.completed_at else None
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
    def create_todo_with_priority(title: str, description: Optional[str] = None, user_id: str = None,
                                 priority: str = "medium", tags: Optional[List[str]] = None,
                                 due_date: Optional[str] = None, recurrence_pattern: Optional[str] = None) -> dict:
        """
        Creates a new todo with advanced features like priority, tags, due date, and recurrence pattern.

        Args:
            title: The title of the todo
            description: Optional description of the todo
            user_id: ID of the user creating the todo
            priority: Priority level (low, medium, high)
            tags: Optional list of tags for categorization
            due_date: Optional due date in ISO format
            recurrence_pattern: Optional recurrence pattern for recurring tasks

        Returns:
            A dictionary representation of the created Todo object
        """
        logger.info(f"MCP Tool: Creating todo with title '{title}' for user {user_id} with advanced features")

        try:
            with next(get_session()) as session:
                # Use the service layer for creating todo with advanced features
                from services.todo_service import TodoService
                from uuid import UUID
                from datetime import datetime

                user_uuid = UUID(user_id) if user_id else UUID(int=0)  # Use a default UUID if none provided

                # Parse due date if provided
                due_datetime = None
                if due_date:
                    try:
                        due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    except ValueError:
                        logger.warning(f"Invalid due date format: {due_date}")
                        due_datetime = None

                # Use the service to create the todo with advanced features
                service = TodoService()
                todo = service.create_todo_with_advanced_features(
                    session=session,
                    title=title,
                    description=description,
                    user_id=user_uuid,
                    priority=PriorityEnum(priority.lower()),
                    tags=tags,
                    due_date=due_datetime,
                    recurrence_pattern=recurrence_pattern
                )

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
                        "status": todo.status,
                        "priority": todo.priority.value,
                        "tags": todo.tags,
                        "dueDate": todo.due_date.isoformat() if todo.due_date else None,
                        "recurrencePattern": todo.recurrence_pattern,
                        "nextOccurrenceDate": todo.next_occurrence_date.isoformat() if todo.next_occurrence_date else None,
                        "userId": str(todo.user_id),
                        "createdAt": todo.created_at.isoformat(),
                        "completedAt": todo.completed_at.isoformat() if todo.completed_at else None
                    }
                )

                # Return a dictionary representation following strict MCP contracts
                todo_dict = {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status,
                    "priority": todo.priority.value,
                    "tags": todo.tags,
                    "dueDate": todo.due_date.isoformat() if todo.due_date else None,
                    "recurrencePattern": todo.recurrence_pattern,
                    "nextOccurrenceDate": todo.next_occurrence_date.isoformat() if todo.next_occurrence_date else None,
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
    def update_todo_with_advanced_features(todo_id: str, title: Optional[str] = None, description: Optional[str] = None, 
                                          status: Optional[str] = None, priority: Optional[str] = None, 
                                          tags: Optional[List[str]] = None, due_date: Optional[str] = None) -> Optional[dict]:
        """
        Updates an existing todo with advanced features like priority, tags, and due date.

        Args:
            todo_id: The ID of the todo to update
            title: New title (optional)
            description: New description (optional)
            status: New status (pending/completed) (optional)
            priority: New priority level (optional)
            tags: New list of tags (optional)
            due_date: New due date in ISO format (optional)

        Returns:
            A dictionary representation of the updated Todo object or None if not found
        """
        logger.info(f"MCP Tool: Updating todo with ID {todo_id} with advanced features")

        try:
            with next(get_session()) as session:
                # Import Todo model from models
                from models.todo import Todo as TodoModel, Priority as PriorityEnum
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
                if priority is not None:
                    try:
                        priority_enum = PriorityEnum(priority.lower())
                        todo.priority = priority_enum
                    except ValueError:
                        logger.warning(f"Invalid priority value: {priority}")
                if tags is not None:
                    todo.tags = tags
                if due_date is not None:
                    try:
                        todo.due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    except ValueError:
                        logger.warning(f"Invalid due date format: {due_date}")

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
                        "status": todo.status,
                        "priority": todo.priority.value,
                        "tags": todo.tags,
                        "dueDate": todo.due_date.isoformat() if todo.due_date else None
                    }
                )

                # Return a dictionary representation following strict MCP contracts
                todo_dict = {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status,
                    "priority": todo.priority.value,
                    "tags": todo.tags,
                    "dueDate": todo.due_date.isoformat() if todo.due_date else None,
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

    @staticmethod
    def search_todos(user_id: str, keyword: str) -> List[dict]:
        """
        Search todos by keyword in title or description.

        Args:
            user_id: The ID of the user whose todos to search
            keyword: The keyword to search for

        Returns:
            A list of matching Todo objects as dictionaries
        """
        logger.info(f"MCP Tool: Searching todos for user {user_id} with keyword '{keyword}'")

        try:
            with next(get_session()) as session:
                # Import Todo model from models
                from models.todo import Todo as TodoModel
                from uuid import UUID
                user_uuid = UUID(user_id)

                # Query todos that match the keyword in title or description
                query = select(TodoModel).where(
                    (TodoModel.user_id == user_uuid) &
                    (
                        TodoModel.title.contains(keyword) |
                        TodoModel.description.contains(keyword)
                    )
                )

                todos = session.exec(query).all()

                logger.info(f"MCP Tool: Found {len(todos)} todos matching keyword '{keyword}'")

                # Return a list of dictionary representations following strict MCP contracts
                todos_list = []
                for todo in todos:
                    todo_dict = {
                        "id": str(todo.id),
                        "title": todo.title,
                        "description": todo.description,
                        "status": todo.status,
                        "priority": todo.priority.value,
                        "tags": todo.tags,
                        "dueDate": todo.due_date.isoformat() if todo.due_date else None,
                        "userId": str(todo.user_id),
                        "createdAt": todo.created_at.isoformat(),
                        "completedAt": todo.completed_at.isoformat() if todo.completed_at else None
                    }
                    todos_list.append(todo_dict)

                return todos_list
        except Exception as e:
            logger.error(f"MCP Tool: Error searching todos for user {user_id} with keyword '{keyword}': {str(e)}")

            # Track the error
            analytics_service.track_error(
                user_id=user_id,
                conversation_id="unknown",
                error_message=str(e),
                error_type=type(e).__name__
            )
            raise e

    @staticmethod
    def filter_todos(user_id: str, status: Optional[str] = None, priority: Optional[str] = None, 
                     tags: Optional[List[str]] = None) -> List[dict]:
        """
        Filter todos by status, priority, or tags.

        Args:
            user_id: The ID of the user whose todos to filter
            status: Filter by status (pending/completed) (optional)
            priority: Filter by priority (low/medium/high) (optional)
            tags: Filter by tags (optional)

        Returns:
            A list of matching Todo objects as dictionaries
        """
        logger.info(f"MCP Tool: Filtering todos for user {user_id}")

        try:
            with next(get_session()) as session:
                # Import Todo model from models
                from models.todo import Todo as TodoModel, Priority as PriorityEnum
                from uuid import UUID
                user_uuid = UUID(user_id)

                # Build query with filters
                query = select(TodoModel).where(TodoModel.user_id == user_uuid)

                if status:
                    query = query.where(TodoModel.status == status)
                if priority:
                    try:
                        priority_enum = PriorityEnum(priority.lower())
                        query = query.where(TodoModel.priority == priority_enum)
                    except ValueError:
                        logger.warning(f"Invalid priority value: {priority}")
                if tags:
                    # Simple tag filtering - in a real implementation, you'd need to handle JSON array queries properly
                    for tag in tags:
                        query = query.where(TodoModel.tags.contains(tag))

                todos = session.exec(query).all()

                logger.info(f"MCP Tool: Found {len(todos)} todos matching filters")

                # Return a list of dictionary representations following strict MCP contracts
                todos_list = []
                for todo in todos:
                    todo_dict = {
                        "id": str(todo.id),
                        "title": todo.title,
                        "description": todo.description,
                        "status": todo.status,
                        "priority": todo.priority.value,
                        "tags": todo.tags,
                        "dueDate": todo.due_date.isoformat() if todo.due_date else None,
                        "userId": str(todo.user_id),
                        "createdAt": todo.created_at.isoformat(),
                        "completedAt": todo.completed_at.isoformat() if todo.completed_at else None
                    }
                    todos_list.append(todo_dict)

                return todos_list
        except Exception as e:
            logger.error(f"MCP Tool: Error filtering todos for user {user_id}: {str(e)}")

            # Track the error
            analytics_service.track_error(
                user_id=user_id,
                conversation_id="unknown",
                error_message=str(e),
                error_type=type(e).__name__
            )
            raise e

    @staticmethod
    def create_reminder_for_task(todo_id: str, scheduled_time: str, user_id: str = None) -> dict:
        """
        Creates a reminder for a specific task.

        Args:
            todo_id: The ID of the task to create a reminder for
            scheduled_time: When the reminder should be triggered (ISO format)
            user_id: ID of the user creating the reminder

        Returns:
            A dictionary representation of the created reminder
        """
        from models.reminder import Reminder, ReminderStatus
        from models.todo import Todo
        from uuid import UUID
        from datetime import datetime
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"MCP Tool: Creating reminder for task {todo_id} scheduled for {scheduled_time}")

        try:
            with next(get_session()) as session:
                user_uuid = UUID(user_id) if user_id else UUID(int=0)
                todo_uuid = UUID(todo_id)

                # Verify the task exists and belongs to the user
                todo = session.get(Todo, todo_uuid)
                if not todo:
                    logger.warning(f"MCP Tool: Task with ID {todo_id} not found")
                    return {"success": False, "error": "Task not found"}

                if str(todo.user_id) != user_id:
                    logger.warning(f"MCP Tool: User {user_id} does not own task {todo_id}")
                    return {"success": False, "error": "Unauthorized access to task"}

                # Parse the scheduled time
                try:
                    scheduled_datetime = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                except ValueError:
                    logger.warning(f"MCP Tool: Invalid scheduled time format: {scheduled_time}")
                    return {"success": False, "error": "Invalid scheduled time format"}

                # Create the reminder
                reminder = Reminder(
                    task_id=todo_uuid,
                    scheduled_time=scheduled_datetime
                )

                session.add(reminder)
                session.commit()
                session.refresh(reminder)

                logger.info(f"MCP Tool: Successfully created reminder with ID {reminder.id}")

                # Track the reminder creation event
                analytics_service.track_todo_operation(
                    operation="reminder_created",
                    user_id=user_id or "unknown",
                    conversation_id="unknown",  # This would be passed from the chatbot endpoint
                    todo_data={
                        "reminderId": str(reminder.id),
                        "taskId": str(reminder.task_id),
                        "scheduledTime": reminder.scheduled_time.isoformat(),
                        "status": reminder.sent_status.value
                    }
                )

                # Return a dictionary representation following strict MCP contracts
                return {
                    "id": str(reminder.id),
                    "taskId": str(reminder.task_id),
                    "scheduledTime": reminder.scheduled_time.isoformat(),
                    "status": reminder.sent_status.value,
                    "deliveryAttempts": reminder.delivery_attempts,
                    "createdAt": reminder.created_at.isoformat()
                }
        except Exception as e:
            logger.error(f"MCP Tool: Error creating reminder for task {todo_id}: {str(e)}")

            # Track the error
            analytics_service.track_error(
                user_id=user_id or "unknown",
                conversation_id="unknown",
                error_message=str(e),
                error_type=type(e).__name__
            )
            raise e

    @staticmethod
    def create_recurring_task(title: str, description: Optional[str] = None, user_id: str = None,
                             priority: str = "medium", tags: Optional[List[str]] = None,
                             due_date: Optional[str] = None, recurrence_pattern: str = None) -> dict:
        """
        Creates a new recurring task with specified recurrence pattern.

        Args:
            title: The title of the task
            description: Optional description of the task
            user_id: ID of the user creating the task
            priority: Priority level (low, medium, high)
            tags: Optional list of tags for categorization
            due_date: Optional due date in ISO format
            recurrence_pattern: Recurrence pattern for the task (e.g., "daily", "weekly", "monthly", "yearly")

        Returns:
            A dictionary representation of the created recurring task
        """
        logger.info(f"MCP Tool: Creating recurring task with title '{title}' for user {user_id}")

        try:
            with next(get_session()) as session:
                # Use the service layer for creating recurring todo
                from services.todo_service import TodoService
                from uuid import UUID
                from datetime import datetime

                user_uuid = UUID(user_id) if user_id else UUID(int=0)  # Use a default UUID if none provided

                # Parse due date if provided
                due_datetime = None
                if due_date:
                    try:
                        due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    except ValueError:
                        logger.warning(f"Invalid due date format: {due_date}")
                        due_datetime = None

                # Use the service to create the recurring todo
                service = TodoService()
                todo = service.create_todo_with_advanced_features(
                    session=session,
                    title=title,
                    description=description,
                    user_id=user_uuid,
                    priority=PriorityEnum(priority.lower()),
                    tags=tags,
                    due_date=due_datetime,
                    recurrence_pattern=recurrence_pattern
                )

                logger.info(f"MCP Tool: Successfully created recurring task with ID {todo.id}")

                # Track the recurring task creation event
                analytics_service.track_todo_operation(
                    operation="create_recurring",
                    user_id=str(user_uuid) if user_id else "unknown",
                    conversation_id="unknown",  # This would be passed from the chatbot endpoint
                    todo_data={
                        "id": str(todo.id),
                        "title": todo.title,
                        "description": todo.description,
                        "status": todo.status,
                        "priority": todo.priority.value,
                        "tags": todo.tags,
                        "dueDate": todo.due_date.isoformat() if todo.due_date else None,
                        "recurrencePattern": todo.recurrence_pattern,
                        "nextOccurrenceDate": todo.next_occurrence_date.isoformat() if todo.next_occurrence_date else None,
                        "userId": str(todo.user_id),
                        "createdAt": todo.created_at.isoformat(),
                        "completedAt": todo.completed_at.isoformat() if todo.completed_at else None
                    }
                )

                # Return a dictionary representation following strict MCP contracts
                todo_dict = {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status,
                    "priority": todo.priority.value,
                    "tags": todo.tags,
                    "dueDate": todo.due_date.isoformat() if todo.due_date else None,
                    "recurrencePattern": todo.recurrence_pattern,
                    "nextOccurrenceDate": todo.next_occurrence_date.isoformat() if todo.next_occurrence_date else None,
                    "userId": str(todo.user_id),
                    "createdAt": todo.created_at.isoformat(),
                    "completedAt": todo.completed_at.isoformat() if todo.completed_at else None
                }

                return todo_dict
        except Exception as e:
            logger.error(f"MCP Tool: Error creating recurring task with title '{title}': {str(e)}")

            # Track the error
            analytics_service.track_error(
                user_id=user_id or "unknown",
                conversation_id="unknown",
                error_message=str(e),
                error_type=type(e).__name__
            )
            raise e

    @staticmethod
    def cancel_recurring_series(todo_id: str, user_id: str = None) -> dict:
        """
        Cancels a recurring task series to prevent future occurrences.

        Args:
            todo_id: The ID of the recurring task to cancel
            user_id: ID of the user cancelling the task

        Returns:
            A dictionary with the cancellation result
        """
        logger.info(f"MCP Tool: Cancelling recurring task series with ID {todo_id}")

        try:
            with next(get_session()) as session:
                # Use the service layer for cancelling recurring todo
                from services.todo_service import TodoService
                from uuid import UUID

                user_uuid = UUID(user_id) if user_id else UUID(int=0)  # Use a default UUID if none provided
                todo_uuid = UUID(todo_id)

                # Use the service to cancel the recurring series
                service = TodoService()
                success = service.cancel_recurring_series(
                    session=session,
                    todo_id=todo_uuid
                )

                if success:
                    logger.info(f"MCP Tool: Successfully cancelled recurring task series with ID {todo_id}")

                    # Track the recurring task cancellation event
                    analytics_service.track_todo_operation(
                        operation="cancel_recurring",
                        user_id=user_id or "unknown",
                        conversation_id="unknown",  # This would be passed from the chatbot endpoint
                        todo_data={
                            "id": todo_id,
                            "cancelledBy": user_id
                        }
                    )

                    return {
                        "success": True,
                        "cancelledId": todo_id,
                        "message": "Recurring task series cancelled successfully"
                    }
                else:
                    logger.warning(f"MCP Tool: Failed to cancel recurring task series with ID {todo_id} - not found or not recurring")
                    return {
                        "success": False,
                        "cancelledId": todo_id,
                        "message": "Recurring task series not found or not a recurring task"
                    }
        except Exception as e:
            logger.error(f"MCP Tool: Error cancelling recurring task series with ID {todo_id}: {str(e)}")

            # Track the error
            analytics_service.track_error(
                user_id=user_id or "unknown",
                conversation_id="unknown",
                error_message=str(e),
                error_type=type(e).__name__
            )
            raise e

    @staticmethod
    def get_reminders_for_task(todo_id: str, user_id: str = None) -> List[dict]:
        """
        Gets all reminders for a specific task.

        Args:
            todo_id: The ID of the task to get reminders for
            user_id: ID of the user requesting the reminders

        Returns:
            A list of dictionary representations of the reminders
        """
        from models.reminder import Reminder
        from models.todo import Todo
        from uuid import UUID
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"MCP Tool: Getting reminders for task {todo_id}")

        try:
            with next(get_session()) as session:
                user_uuid = UUID(user_id) if user_id else UUID(int=0)
                todo_uuid = UUID(todo_id)

                # Verify the task exists and belongs to the user
                todo = session.get(Todo, todo_uuid)
                if not todo:
                    logger.warning(f"MCP Tool: Task with ID {todo_id} not found")
                    return []

                if str(todo.user_id) != user_id:
                    logger.warning(f"MCP Tool: User {user_id} does not own task {todo_id}")
                    return []

                # Get all reminders for the task
                reminders = session.exec(
                    select(Reminder).where(Reminder.task_id == todo_uuid)
                ).all()

                logger.info(f"MCP Tool: Found {len(reminders)} reminders for task {todo_id}")

                # Return a list of dictionary representations following strict MCP contracts
                reminders_list = []
                for reminder in reminders:
                    reminder_dict = {
                        "id": str(reminder.id),
                        "taskId": str(reminder.task_id),
                        "scheduledTime": reminder.scheduled_time.isoformat(),
                        "status": reminder.sent_status.value,
                        "deliveryAttempts": reminder.delivery_attempts,
                        "lastAttemptTime": reminder.last_attempt_time.isoformat() if reminder.last_attempt_time else None,
                        "createdAt": reminder.created_at.isoformat()
                    }
                    reminders_list.append(reminder_dict)

                return reminders_list
        except Exception as e:
            logger.error(f"MCP Tool: Error getting reminders for task {todo_id}: {str(e)}")

            # Track the error
            analytics_service.track_error(
                user_id=user_id or "unknown",
                conversation_id="unknown",
                error_message=str(e),
                error_type=type(e).__name__
            )
            raise e

    @staticmethod
    def sort_todos(user_id: str, sort_by: str = "created_at", sort_order: str = "desc") -> List[dict]:
        """
        Sort todos by various criteria.

        Args:
            user_id: The ID of the user whose todos to sort
            sort_by: Field to sort by (created_at, due_date, priority, title) (default: created_at)
            sort_order: Sort order (asc, desc) (default: desc)

        Returns:
            A list of sorted Todo objects as dictionaries
        """
        logger.info(f"MCP Tool: Sorting todos for user {user_id} by {sort_by} in {sort_order} order")

        try:
            with next(get_session()) as session:
                # Import Todo model from models
                from models.todo import Todo as TodoModel
                from uuid import UUID
                from sqlalchemy import asc, desc
                user_uuid = UUID(user_id)

                # Build query with sorting
                query = select(TodoModel).where(TodoModel.user_id == user_uuid)

                # Apply sorting based on the sort_by and sort_order parameters
                if sort_by == "priority":
                    if sort_order == "asc":
                        query = query.order_by(asc(TodoModel.priority))
                    else:
                        query = query.order_by(desc(TodoModel.priority))
                elif sort_by == "due_date":
                    if sort_order == "asc":
                        query = query.order_by(asc(TodoModel.due_date))
                    else:
                        query = query.order_by(desc(TodoModel.due_date))
                elif sort_by == "title":
                    if sort_order == "asc":
                        query = query.order_by(asc(TodoModel.title))
                    else:
                        query = query.order_by(desc(TodoModel.title))
                else:  # Default to created_at
                    if sort_order == "asc":
                        query = query.order_by(asc(TodoModel.created_at))
                    else:
                        query = query.order_by(desc(TodoModel.created_at))

                todos = session.exec(query).all()

                logger.info(f"MCP Tool: Sorted {len(todos)} todos")

                # Return a list of dictionary representations following strict MCP contracts
                todos_list = []
                for todo in todos:
                    todo_dict = {
                        "id": str(todo.id),
                        "title": todo.title,
                        "description": todo.description,
                        "status": todo.status,
                        "priority": todo.priority.value,
                        "tags": todo.tags,
                        "dueDate": todo.due_date.isoformat() if todo.due_date else None,
                        "userId": str(todo.user_id),
                        "createdAt": todo.created_at.isoformat(),
                        "completedAt": todo.completed_at.isoformat() if todo.completed_at else None
                    }
                    todos_list.append(todo_dict)

                return todos_list
        except Exception as e:
            logger.error(f"MCP Tool: Error sorting todos for user {user_id}: {str(e)}")

            # Track the error
            analytics_service.track_error(
                user_id=user_id,
                conversation_id="unknown",
                error_message=str(e),
                error_type=type(e).__name__
            )
            raise e

    @staticmethod
    def update_todo_with_advanced_features(todo_id: str, title: Optional[str] = None,
                                         description: Optional[str] = None, status: Optional[str] = None,
                                         priority: Optional[str] = None, tags: Optional[List[str]] = None,
                                         due_date: Optional[str] = None) -> Optional[dict]:
        """
        Updates a todo with advanced features like priority, tags, and due date.

        Args:
            todo_id: The ID of the todo to update
            title: New title (optional)
            description: New description (optional)
            status: New status (pending/completed) (optional)
            priority: New priority level (optional)
            tags: New list of tags (optional)
            due_date: New due date in ISO format (optional)

        Returns:
            A dictionary representation of the updated Todo object or None if not found
        """
        logger.info(f"MCP Tool: Updating todo with ID {todo_id} with advanced features")

        try:
            with next(get_session()) as session:
                # Import Todo model from models
                from models.todo import Todo as TodoModel, Priority as PriorityEnum
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
                if priority is not None:
                    try:
                        priority_enum = PriorityEnum(priority.lower())
                        todo.priority = priority_enum
                    except ValueError:
                        logger.warning(f"Invalid priority value: {priority}")
                if tags is not None:
                    todo.tags = tags
                if due_date is not None:
                    try:
                        todo.due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    except ValueError:
                        logger.warning(f"Invalid due date format: {due_date}")

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
                        "status": todo.status,
                        "priority": todo.priority.value,
                        "tags": todo.tags,
                        "dueDate": todo.due_date.isoformat() if todo.due_date else None
                    }
                )

                # Return a dictionary representation following strict MCP contracts
                todo_dict = {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status,
                    "priority": todo.priority.value,
                    "tags": todo.tags,
                    "dueDate": todo.due_date.isoformat() if todo.due_date else None,
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