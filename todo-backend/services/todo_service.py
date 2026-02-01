from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from models.todo import Todo, Priority
from models.user import User
from models.reminder import Reminder
from models.recurrence import RecurrencePattern
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TodoService:
    """Service class for advanced todo operations including priorities, tags, search, filtering, and sorting."""
    
    def __init__(self):
        pass
    
    def create_todo_with_advanced_features(
        self,
        session: Session,
        title: str,
        description: Optional[str],
        user_id: UUID,
        priority: Priority = Priority.medium,
        tags: Optional[List[str]] = None,
        due_date: Optional[datetime] = None,
        recurrence_pattern: Optional[str] = None
    ) -> Todo:
        """Create a new todo with advanced features."""
        todo = Todo(
            title=title,
            description=description,
            user_id=user_id,
            priority=priority,
            tags=tags,
            due_date=due_date,
            recurrence_pattern=recurrence_pattern
        )
        session.add(todo)
        session.commit()
        session.refresh(todo)

        # Publish event for the created task
        try:
            import asyncio
            from events.producer import publish_task_event
            asyncio.create_task(
                publish_task_event(
                    event_type="task.created",
                    task_data={
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
                    },
                    user_id=str(todo.user_id)
                )
            )
        except Exception as e:
            logger.error(f"Error publishing task.created event: {e}")

        return todo
    
    def get_todos_by_filters(
        self,
        session: Session,
        user_id: UUID,
        completed: Optional[bool] = None,
        priority: Optional[Priority] = None,
        tags: Optional[List[str]] = None,
        search_keyword: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> List[Todo]:
        """Get todos with advanced filtering, searching, and sorting capabilities."""
        query = select(Todo).where(Todo.user_id == user_id)
        
        # Apply filters
        if completed is not None:
            if completed:
                query = query.where(Todo.status == "completed")
            else:
                query = query.where(Todo.status == "pending")
        
        if priority is not None:
            query = query.where(Todo.priority == priority)
        
        if tags:
            # This is a simplified tag search - in a real implementation, 
            # you'd need to handle JSON array queries properly for your database
            for tag in tags:
                query = query.where(Todo.tags.contains(tag))
        
        if search_keyword:
            # Search in title and description
            query = query.where(
                Todo.title.contains(search_keyword) | 
                (Todo.description.contains(search_keyword) if Todo.description else False)
            )
        
        # Apply sorting
        if sort_by == "priority":
            if sort_order == "asc":
                query = query.order_by(Todo.priority)
            else:
                query = query.order_by(Todo.priority.desc())
        elif sort_by == "due_date":
            if sort_order == "asc":
                query = query.order_by(Todo.due_date)
            else:
                query = query.order_by(Todo.due_date.desc())
        elif sort_by == "title":
            if sort_order == "asc":
                query = query.order_by(Todo.title)
            else:
                query = query.order_by(Todo.title.desc())
        else:  # Default to created_at
            if sort_order == "asc":
                query = query.order_by(Todo.created_at)
            else:
                query = query.order_by(Todo.created_at.desc())

        return session.exec(query).all()

    def search_todos_by_keyword(
        self,
        session: Session,
        user_id: UUID,
        keyword: str
    ) -> List[Todo]:
        """Search todos by keyword in title and description."""
        query = select(Todo).where(
            (Todo.user_id == user_id) &
            (
                Todo.title.contains(keyword) |
                (Todo.description.contains(keyword) if Todo.description else False)
            )
        )

        return session.exec(query).all()

    def filter_todos_by_criteria(
        self,
        session: Session,
        user_id: UUID,
        completed: Optional[bool] = None,
        priority: Optional[Priority] = None,
        tags: Optional[List[str]] = None
    ) -> List[Todo]:
        """Filter todos by completion status, priority, and tags."""
        query = select(Todo).where(Todo.user_id == user_id)

        # Apply completion status filter
        if completed is not None:
            if completed:
                query = query.where(Todo.status == "completed")
            else:
                query = query.where(Todo.status == "pending")

        # Apply priority filter
        if priority is not None:
            query = query.where(Todo.priority == priority)

        # Apply tags filter
        if tags:
            # For simplicity, we'll filter for todos that contain any of the specified tags
            # In a real implementation, you might want more sophisticated tag matching
            for tag in tags:
                query = query.where(Todo.tags.contains([tag]))

        return session.exec(query).all()

    def sort_todos_by_criteria(
        self,
        session: Session,
        user_id: UUID,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> List[Todo]:
        """Sort todos by date, priority, or title."""
        query = select(Todo).where(Todo.user_id == user_id)

        # Apply sorting based on the sort_by and sort_order parameters
        if sort_by == "priority":
            if sort_order == "asc":
                query = query.order_by(Todo.priority)
            else:
                query = query.order_by(Todo.priority.desc())
        elif sort_by == "due_date":
            if sort_order == "asc":
                query = query.order_by(Todo.due_date)
            else:
                query = query.order_by(Todo.due_date.desc())
        elif sort_by == "title":
            if sort_order == "asc":
                query = query.order_by(Todo.title)
            else:
                query = query.order_by(Todo.title.desc())
        else:  # Default to created_at
            if sort_order == "asc":
                query = query.order_by(Todo.created_at)
            else:
                query = query.order_by(Todo.created_at.desc())

        return session.exec(query).all()

    def process_recurrence_pattern(
        self,
        session: Session,
        todo_id: UUID
    ) -> Optional[Todo]:
        """
        Process a recurring task's pattern to generate the next occurrence.

        Args:
            session: Database session
            todo_id: ID of the recurring task that was completed

        Returns:
            The newly created task instance or None if not recurring or error
        """
        from datetime import timedelta
        from uuid import UUID

        # Get the completed recurring task
        completed_task = session.get(Todo, todo_id)
        if not completed_task or not completed_task.recurrence_pattern:
            return None

        # Determine the next occurrence date based on the pattern
        next_occurrence_date = self._calculate_next_occurrence(
            completed_task.recurrence_pattern,
            completed_task.next_occurrence_date or completed_task.completed_at or completed_task.created_at
        )

        if not next_occurrence_date:
            return None

        # Create a new task based on the original recurring task
        new_task = Todo(
            title=completed_task.title,
            description=completed_task.description,
            status="pending",
            priority=completed_task.priority,
            tags=completed_task.tags,
            due_date=completed_task.due_date,
            recurrence_pattern=completed_task.recurrence_pattern,
            next_occurrence_date=next_occurrence_date,
            user_id=completed_task.user_id
        )

        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        return new_task

    def _calculate_next_occurrence(
        self,
        recurrence_pattern: str,
        last_occurrence_date: datetime
    ) -> Optional[datetime]:
        """
        Calculate the next occurrence date based on the recurrence pattern.

        Args:
            recurrence_pattern: Pattern string (daily, weekly, monthly, yearly)
            last_occurrence_date: Date of the last occurrence

        Returns:
            The next occurrence date or None if pattern is invalid
        """
        if recurrence_pattern == "daily":
            return last_occurrence_date + timedelta(days=1)
        elif recurrence_pattern == "weekly":
            return last_occurrence_date + timedelta(weeks=1)
        elif recurrence_pattern == "monthly":
            # For monthly, we'll add approximately one month (30 days)
            # In a real implementation, you might want to handle months differently
            return last_occurrence_date + timedelta(days=30)
        elif recurrence_pattern == "yearly":
            return last_occurrence_date + timedelta(days=365)
        else:
            # For more complex patterns, you might parse the pattern string
            # which could contain more detailed recurrence rules
            return None

    def cancel_recurring_series(
        self,
        session: Session,
        todo_id: UUID
    ) -> bool:
        """
        Cancel a recurring task series to stop future occurrences.

        Args:
            session: Database session
            todo_id: ID of the recurring task to cancel

        Returns:
            True if successfully cancelled, False otherwise
        """
        # Get the recurring task
        recurring_task = session.get(Todo, todo_id)
        if not recurring_task or not recurring_task.recurrence_pattern:
            return False

        # Remove the recurrence pattern to stop future occurrences
        recurring_task.recurrence_pattern = None
        recurring_task.next_occurrence_date = None

        session.add(recurring_task)
        session.commit()

        return True

    def update_todo_with_advanced_features(
        self,
        session: Session,
        todo_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[Priority] = None,
        tags: Optional[List[str]] = None,
        due_date: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> Optional[Todo]:
        """Update a todo with advanced features."""
        todo = session.get(Todo, todo_id)
        if not todo:
            return None

        # Update fields if provided
        if title is not None:
            todo.title = title
        if description is not None:
            todo.description = description
        if priority is not None:
            todo.priority = priority
        if tags is not None:
            todo.tags = tags
        if due_date is not None:
            todo.due_date = due_date
        if status is not None:
            todo.status = status

        session.add(todo)
        session.commit()
        session.refresh(todo)

        # Publish event for the updated task
        try:
            import asyncio
            from events.producer import publish_task_event
            asyncio.create_task(
                publish_task_event(
                    event_type="task.updated",
                    task_data={
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
                    },
                    user_id=str(todo.user_id)
                )
            )
        except Exception as e:
            logger.error(f"Error publishing task.updated event: {e}")

        return todo
    
    def create_recurring_todo(
        self,
        session: Session,
        title: str,
        description: Optional[str],
        user_id: UUID,
        recurrence_pattern_id: UUID,
        priority: Priority = Priority.medium,
        tags: Optional[List[str]] = None,
        due_date: Optional[datetime] = None
    ) -> Todo:
        """Create a recurring todo based on a recurrence pattern."""
        # First, get the recurrence pattern
        recurrence_pattern = session.get(RecurrencePattern, recurrence_pattern_id)
        if not recurrence_pattern:
            raise ValueError(f"Recurrence pattern with id {recurrence_pattern_id} not found")
        
        # Convert recurrence pattern to a string representation for storage
        pattern_str = f"{recurrence_pattern.frequency.value}:{recurrence_pattern.interval}"
        
        return self.create_todo_with_advanced_features(
            session=session,
            title=title,
            description=description,
            user_id=user_id,
            priority=priority,
            tags=tags,
            due_date=due_date,
            recurrence_pattern=pattern_str
        )
    
    def create_reminder_for_todo(
        self,
        session: Session,
        todo_id: UUID,
        scheduled_time: datetime
    ) -> Reminder:
        """Create a reminder for a specific todo."""
        reminder = Reminder(
            task_id=todo_id,
            scheduled_time=scheduled_time
        )
        session.add(reminder)
        session.commit()
        session.refresh(reminder)
        return reminder

    def delete_todo(
        self,
        session: Session,
        todo_id: UUID
    ) -> bool:
        """Delete a todo by ID."""
        todo = session.get(Todo, todo_id)
        if not todo:
            return False

        # Prepare task data before deletion for the event
        task_data = {
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

        session.delete(todo)
        session.commit()

        # Publish event for the deleted task
        try:
            import asyncio
            from events.producer import publish_task_event
            asyncio.create_task(
                publish_task_event(
                    event_type="task.deleted",
                    task_data=task_data,
                    user_id=str(todo.user_id)
                )
            )
        except Exception as e:
            logger.error(f"Error publishing task.deleted event: {e}")

        return True