"""
Recurring task scheduler for handling recurring task patterns.
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlmodel import Session, select
from models.todo import Todo
from models.user import User
from database import engine
from events.producer import EventProducer
from dapr.client import DaprClient as DaprAsyncClient
import logging

logger = logging.getLogger(__name__)


class RecurringTaskScheduler:
    """
    Handles the creation of new tasks based on recurrence patterns.
    """
    
    @staticmethod
    def process_recurrence_pattern(todo: Todo) -> List[Todo]:
        """
        Process a recurring task and create new instances based on the pattern.
        
        Args:
            todo: The recurring task to process
            
        Returns:
            List of new task instances created based on the recurrence pattern
        """
        if not todo.recurrence_pattern:
            return []
        
        try:
            pattern_data = json.loads(todo.recurrence_pattern)
        except json.JSONDecodeError:
            logger.error(f"Invalid recurrence pattern for task {todo.id}: {todo.recurrence_pattern}")
            return []
        
        new_tasks = []
        
        # Determine the next occurrence date based on the pattern
        next_occurrence = RecurringTaskScheduler._calculate_next_occurrence(
            todo.next_occurrence_date or todo.created_at,
            pattern_data
        )
        
        # If the next occurrence is in the future, update the task
        if next_occurrence and next_occurrence > datetime.utcnow():
            todo.next_occurrence_date = next_occurrence
            return []
        
        # Create a new instance of the recurring task
        new_task = RecurringTaskScheduler._create_new_instance(todo, pattern_data)
        if new_task:
            new_tasks.append(new_task)
        
        return new_tasks
    
    @staticmethod
    def _calculate_next_occurrence(last_date: datetime, pattern_data: Dict[str, Any]) -> datetime:
        """
        Calculate the next occurrence date based on the recurrence pattern.
        
        Args:
            last_date: The date of the last occurrence
            pattern_data: The recurrence pattern data
            
        Returns:
            The next occurrence date
        """
        frequency = pattern_data.get('frequency', 'daily')
        interval = pattern_data.get('interval', 1)
        
        if frequency == 'daily':
            return last_date + timedelta(days=interval)
        elif frequency == 'weekly':
            return last_date + timedelta(weeks=interval)
        elif frequency == 'monthly':
            # For monthly, we add the interval to the month
            # This handles month-end edge cases appropriately
            year = last_date.year
            month = last_date.month + interval
            day = last_date.day
            
            # Handle year overflow
            while month > 12:
                year += 1
                month -= 12
                
            # Handle day overflow (e.g., Jan 31 + 1 month should be Feb 28/29)
            import calendar
            max_day = calendar.monthrange(year, month)[1]
            if day > max_day:
                day = max_day
                
            return last_date.replace(year=year, month=month, day=day)
        elif frequency == 'yearly':
            # For yearly, we add the interval to the year
            return last_date.replace(year=last_date.year + interval)
        else:
            # Unknown frequency, return None
            return None
    
    @staticmethod
    def _create_new_instance(original_task: Todo, pattern_data: Dict[str, Any]) -> Todo:
        """
        Create a new instance of a recurring task.
        
        Args:
            original_task: The original recurring task
            pattern_data: The recurrence pattern data
            
        Returns:
            A new task instance
        """
        # Check if the recurrence should end
        if RecurringTaskScheduler._should_end_recurrence(original_task, pattern_data):
            return None
        
        # Create a new task with the same properties as the original
        new_task = Todo(
            title=original_task.title,
            description=original_task.description,
            status="pending",  # New instances start as pending
            priority=original_task.priority,
            tags=original_task.tags,
            due_date=original_task.due_date,
            recurrence_pattern=original_task.recurrence_pattern,
            user_id=original_task.user_id
        )
        
        # Update the original task's next occurrence date
        original_task.next_occurrence_date = RecurringTaskScheduler._calculate_next_occurrence(
            original_task.next_occurrence_date or original_task.created_at,
            pattern_data
        )
        
        return new_task
    
    @staticmethod
    def _should_end_recurrence(task: Todo, pattern_data: Dict[str, Any]) -> bool:
        """
        Determine if a recurring task should stop generating new instances.
        
        Args:
            task: The recurring task
            pattern_data: The recurrence pattern data
            
        Returns:
            True if the recurrence should end, False otherwise
        """
        # Check if we've reached the maximum number of occurrences
        occurrences_limit = pattern_data.get('occurrences')
        if occurrences_limit is not None:
            # This would require tracking how many instances have been created
            # For now, we'll skip this check and rely on other termination conditions
            pass
        
        # Check if we've reached the end date
        end_date_str = pattern_data.get('endDate')
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                if datetime.utcnow() >= end_date:
                    return True
            except ValueError:
                logger.warning(f"Invalid end date format for task {task.id}: {end_date_str}")
        
        return False


async def process_recurring_tasks():
    """
    Background task to periodically check for recurring tasks that need new instances.
    """
    logger.info("Starting recurring task processing...")
    
    while True:
        try:
            with Session(engine) as session:
                # Find all tasks with recurrence patterns
                recurring_tasks = session.exec(
                    select(Todo).where(
                        Todo.recurrence_pattern.is_not(None),
                        Todo.status == "completed"  # Only process completed recurring tasks
                    )
                ).all()
                
                new_tasks = []
                for task in recurring_tasks:
                    new_instances = RecurringTaskScheduler.process_recurrence_pattern(task)
                    new_tasks.extend(new_instances)
                    
                    # Update the task in the session
                    session.add(task)
                
                # Add new task instances to the database
                for new_task in new_tasks:
                    session.add(new_task)
                    
                    # Publish an event for the new task
                    try:
                        event_data = {
                            "id": str(new_task.id),
                            "type": "recurring_task.generated",
                            "source": "recurring-task-scheduler",
                            "timestamp": datetime.utcnow().isoformat(),
                            "data": {
                                "id": str(new_task.id),
                                "title": new_task.title,
                                "user_id": str(new_task.user_id),
                                "recurrence_source_id": str(task.id)  # Link to the original recurring task
                            },
                            "correlation_id": str(new_task.id)
                        }
                        await EventProducer.publish_event("recurring-tasks", event_data)
                        logger.info(f"Published event for new recurring task instance: {new_task.id}")
                    except Exception as e:
                        logger.error(f"Failed to publish event for task {new_task.id}: {e}")
                
                session.commit()
                
                logger.info(f"Processed {len(recurring_tasks)} recurring tasks, created {len(new_tasks)} new instances")
                
        except Exception as e:
            logger.error(f"Error processing recurring tasks: {e}")
        
        # Wait for 1 hour before the next check
        await asyncio.sleep(3600)  # 1 hour


if __name__ == "__main__":
    # For testing purposes
    import asyncio
    asyncio.run(process_recurring_tasks())