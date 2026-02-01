"""
Reminder notification processor for sending notifications when tasks are due.
"""
import asyncio
from datetime import datetime, timedelta
from sqlmodel import Session, select
from models.todo import Todo
from models.user import User
from database import engine
from events.producer import EventProducer
from dapr.client import DaprClient as DaprAsyncClient
import logging

logger = logging.getLogger(__name__)


class ReminderNotificationProcessor:
    """
    Handles sending notifications for tasks that are due or past due.
    """

    @staticmethod
    async def process_due_reminders():
        """
        Process all tasks that have due dates and send notifications if needed.
        """
        logger.info("Processing due reminders...")

        with Session(engine) as session:
            # Find all tasks with due dates that are approaching or past due
            # We'll look for tasks due within the next hour or already overdue
            now = datetime.utcnow()
            upcoming_deadline = now + timedelta(hours=1)

            tasks = session.exec(
                select(Todo).where(
                    Todo.due_date.is_not(None),
                    Todo.due_date <= upcoming_deadline,
                    Todo.status != "completed"  # Only process incomplete tasks
                )
            ).all()

            processed_count = 0
            for task in tasks:
                # Check if the task is overdue or due soon
                if task.due_date <= now:
                    # Task is overdue
                    await ReminderNotificationProcessor._send_overdue_notification(task)
                elif task.due_date <= upcoming_deadline:
                    # Task is due soon (within the next hour)
                    await ReminderNotificationProcessor._send_due_soon_notification(task)

                processed_count += 1

            logger.info(f"Processed {processed_count} tasks for reminder notifications")

    @staticmethod
    async def _send_overdue_notification(task: Todo):
        """
        Send a notification for an overdue task.

        Args:
            task: The overdue task
        """
        logger.info(f"Sending overdue notification for task {task.id}: {task.title}")

        # Publish an event for the overdue notification using Dapr
        try:
            event_data = {
                "id": str(task.id),
                "type": "reminder.overdue",
                "source": "reminder-notification-processor",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "task_id": str(task.id),
                    "title": task.title,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "user_id": str(task.user_id),
                    "notification_type": "overdue"
                },
                "correlation_id": str(task.id)
            }
            await EventProducer.publish_event("reminders", event_data)
            logger.info(f"Published overdue reminder event for task: {task.id}")
        except Exception as e:
            logger.error(f"Failed to publish overdue reminder event for task {task.id}: {e}")

    @staticmethod
    async def _send_due_soon_notification(task: Todo):
        """
        Send a notification for a task that is due soon.

        Args:
            task: The task due soon
        """
        logger.info(f"Sending due soon notification for task {task.id}: {task.title}")

        # Publish an event for the due soon notification using Dapr
        try:
            event_data = {
                "id": str(task.id),
                "type": "reminder.due_soon",
                "source": "reminder-notification-processor",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "task_id": str(task.id),
                    "title": task.title,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "user_id": str(task.user_id),
                    "notification_type": "due_soon"
                },
                "correlation_id": str(task.id)
            }
            await EventProducer.publish_event("reminders", event_data)
            logger.info(f"Published due soon reminder event for task: {task.id}")
        except Exception as e:
            logger.error(f"Failed to publish due soon reminder event for task {task.id}: {e}")


async def process_reminders():
    """
    Background task to periodically check for tasks that need reminders.
    """
    logger.info("Starting reminder processing...")
    
    while True:
        try:
            await ReminderNotificationProcessor.process_due_reminders()
        except Exception as e:
            logger.error(f"Error processing reminders: {e}")
        
        # Wait for 10 minutes before the next check
        await asyncio.sleep(600)  # 10 minutes


if __name__ == "__main__":
    # For testing purposes
    import asyncio
    asyncio.run(process_reminders())