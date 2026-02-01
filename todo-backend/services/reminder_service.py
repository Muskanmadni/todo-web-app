"""
Reminder service for managing task reminders.
"""
from sqlmodel import Session, select
from models.reminder import Reminder, ReminderStatus
from models.todo import Todo
from database import engine
from datetime import datetime
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class ReminderService:
    """
    Service for managing task reminders.
    """
    
    @staticmethod
    def create_reminder_for_task(todo_id: UUID, scheduled_time: datetime) -> Reminder:
        """
        Create a reminder for a task.
        
        Args:
            todo_id: The ID of the task to create a reminder for
            scheduled_time: When the reminder should be triggered
            
        Returns:
            The created reminder
        """
        with Session(engine) as session:
            # Verify the task exists
            todo = session.get(Todo, todo_id)
            if not todo:
                raise ValueError(f"Task with ID {todo_id} not found")
            
            # Create the reminder
            reminder = Reminder(
                task_id=todo_id,
                scheduled_time=scheduled_time
            )
            
            session.add(reminder)
            session.commit()
            session.refresh(reminder)
            
            logger.info(f"Created reminder for task {todo_id} scheduled for {scheduled_time}")
            
            return reminder
    
    @staticmethod
    def get_reminders_by_task(todo_id: UUID) -> list[Reminder]:
        """
        Get all reminders for a specific task.
        
        Args:
            todo_id: The ID of the task
            
        Returns:
            List of reminders for the task
        """
        with Session(engine) as session:
            reminders = session.exec(
                select(Reminder).where(Reminder.task_id == todo_id)
            ).all()
            
            return reminders
    
    @staticmethod
    def get_upcoming_reminders(limit: int = 100) -> list[Reminder]:
        """
        Get upcoming reminders that are scheduled for the future.
        
        Args:
            limit: Maximum number of reminders to return
            
        Returns:
            List of upcoming reminders
        """
        with Session(engine) as session:
            reminders = session.exec(
                select(Reminder)
                .where(
                    Reminder.scheduled_time >= datetime.utcnow(),
                    Reminder.sent_status == ReminderStatus.pending
                )
                .order_by(Reminder.scheduled_time)
                .limit(limit)
            ).all()
            
            return reminders
    
    @staticmethod
    def update_reminder_status(reminder_id: UUID, status: ReminderStatus) -> Reminder:
        """
        Update the status of a reminder.
        
        Args:
            reminder_id: The ID of the reminder to update
            status: The new status for the reminder
            
        Returns:
            The updated reminder
        """
        with Session(engine) as session:
            reminder = session.get(Reminder, reminder_id)
            if not reminder:
                raise ValueError(f"Reminder with ID {reminder_id} not found")
            
            reminder.sent_status = status
            reminder.last_attempt_time = datetime.utcnow()
            
            if status != ReminderStatus.pending:
                reminder.delivery_attempts += 1
            
            session.add(reminder)
            session.commit()
            session.refresh(reminder)
            
            logger.info(f"Updated reminder {reminder_id} status to {status}")
            
            return reminder
    
    @staticmethod
    def delete_reminder(reminder_id: UUID) -> bool:
        """
        Delete a reminder.
        
        Args:
            reminder_id: The ID of the reminder to delete
            
        Returns:
            True if the reminder was deleted, False otherwise
        """
        with Session(engine) as session:
            reminder = session.get(Reminder, reminder_id)
            if not reminder:
                return False
            
            session.delete(reminder)
            session.commit()
            
            logger.info(f"Deleted reminder {reminder_id}")
            
            return True