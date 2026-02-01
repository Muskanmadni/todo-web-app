"""
Event consumer for processing events using Dapr pub/sub.
"""
import json
import asyncio
from typing import Dict, Any
from datetime import datetime
import logging
from fastapi import Request
from sqlmodel import Session
from models.event import Event, EventStatus
from database import engine
from reminders.notification import ReminderNotificationProcessor
from reminders.scheduler import RecurringTaskScheduler
from .schema.task_events import validate_event_schema

logger = logging.getLogger(__name__)


class EventConsumer:
    """
    Consumer for processing events using Dapr pub/sub.
    """

    @staticmethod
    async def handle_dapr_subscription(request: Request):
        """
        Handle incoming events from Dapr pub/sub subscription.

        This method is called by Dapr when an event is published to a subscribed topic.
        """
        # Extract the event data from the request
        event_data = await request.json()

        # Extract topic from the request headers
        topic = request.headers.get("x-topic", "unknown")

        try:
            # Process the received event
            await EventConsumer._process_event(topic, event_data)

            # Log successful processing
            logger.info(f"Processed event from topic {topic}: {event_data}")

            # Return success response to Dapr
            return {"status": "SUCCESS"}
        except Exception as e:
            logger.error(f"Failed to process event from topic {topic}: {e}")
            # Return error response to Dapr
            return {"status": "RETRY"}  # Dapr will retry on failure
    
    @staticmethod
    async def _process_event(topic: str, data: Dict[str, Any]):
        """
        Process an individual event based on its topic.

        Args:
            topic: The Dapr pub/sub topic the event came from
            data: The event data
        """
        import time

        # Log event processing start with timestamp
        start_time = time.time()
        logger.info(f"Starting to process event topic '{topic}' at {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start_time))}")

        # Validate the event schema
        is_valid, error_msg = validate_event_schema(topic, data)
        if not is_valid:
            logger.error(f"Schema validation failed for topic {topic}: {error_msg}")
            # In a real implementation, you might want to send the event to a dead letter queue
            # For now, we'll just log the error and return
            return

        # Process the event with retry logic
        max_retries = 3
        retry_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                # Handle different event types based on the event type in the data
                event_type = data.get("type", "")

                if event_type == "task.created":
                    await EventConsumer._handle_task_created(data.get("data", {}))
                elif event_type == "task.completed":
                    await EventConsumer._handle_task_completed(data.get("data", {}))
                elif event_type == "reminder.due_soon":
                    await EventConsumer._handle_reminder_due_soon(data.get("data", {}))
                elif event_type == "reminder.overdue":
                    await EventConsumer._handle_reminder_overdue(data.get("data", {}))
                elif event_type.startswith("task."):  # Generic task-related events
                    await EventConsumer._handle_task_event(event_type, data.get("data", {}))
                else:
                    logger.warning(f"Unknown event type: {event_type}")

                # If successful, break out of retry loop
                break

            except Exception as e:
                logger.error(f"Failed to process event (attempt {attempt + 1}/{max_retries}): {e}")

                # If this is the last attempt, log the failure and potentially send to dead letter queue
                if attempt == max_retries - 1:
                    logger.error(f"Failed to process event after {max_retries} attempts: {topic} - {data}")
                    # In a real implementation, you might want to send the event to a dead letter queue
                    # await EventConsumer._send_to_dead_letter_queue(topic, data, str(e))
                else:
                    # Wait before retrying
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff

        # Log event processing completion with execution time
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Event processing completed for topic '{topic}' in {execution_time:.2f}s")

        # In a real implementation, you might want to send metrics to a monitoring system
        # For example, to Prometheus, StatsD, or other monitoring solutions
        # Example: send_metric("event_processing_duration_seconds", execution_time, labels={"topic": topic})
        # Example: send_metric("events_processed_total", 1, labels={"topic": topic})
    
    @staticmethod
    async def _handle_task_created(data: Dict[str, Any]):
        """
        Handle a task created event.

        Args:
            data: The event data
        """
        logger.info(f"Handling task created event: {data}")

        # In a real implementation, you might want to update related systems
        # or trigger other workflows

        # If this is a recurring task, schedule the next occurrence
        if data.get("recurrence_pattern"):
            # This would trigger the recurring task scheduler
            pass

        # If the task has a due date, schedule a reminder
        if data.get("dueDate"):
            # Schedule a reminder for 1 hour before the due date
            from datetime import datetime, timedelta
            try:
                due_date = datetime.fromisoformat(data["dueDate"].replace('Z', '+00:00'))
                reminder_time = due_date - timedelta(hours=1)  # 1 hour before due

                # Schedule the reminder
                await EventConsumer._schedule_reminder_for_task(
                    task_id=data["id"],
                    scheduled_time=reminder_time.isoformat(),
                    user_id=data["userId"]
                )
            except Exception as e:
                logger.error(f"Failed to schedule reminder for task {data['id']}: {e}")
    
    @staticmethod
    async def _handle_task_completed(data: Dict[str, Any]):
        """
        Handle a task completed event.

        Args:
            data: The event data
        """
        logger.info(f"Handling task completed event: {data}")

        # If this was a recurring task, schedule the next occurrence
        if data.get("recurrence_pattern"):
            # Trigger the recurring task scheduler to create the next instance
            await EventConsumer._create_next_recurring_task(data)

    @staticmethod
    async def _create_next_recurring_task(task_data: Dict[str, Any]):
        """
        Create the next instance of a recurring task based on the recurrence pattern.

        Args:
            task_data: The data of the completed recurring task
        """
        from mcp.tools import TodoMCPTools
        import json
        from datetime import datetime
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Creating next recurring task for task {task_data['id']}")

        try:
            # Parse the recurrence pattern
            recurrence_pattern = json.loads(task_data["recurrence_pattern"])

            # Calculate the next occurrence date based on the pattern
            next_occurrence = EventConsumer._calculate_next_occurrence(
                task_data.get("completedAt"),
                recurrence_pattern
            )

            if next_occurrence:
                # Create a new task with the same properties as the original
                new_task_data = {
                    "title": task_data["title"],
                    "description": task_data.get("description"),
                    "priority": task_data.get("priority", "medium"),
                    "tags": task_data.get("tags", []),
                    "due_date": next_occurrence.isoformat(),  # Use the calculated next occurrence
                    "recurrence_pattern": task_data.get("recurrence_pattern"),
                    "user_id": task_data["userId"]
                }

                # Use the MCP tool to create the new recurring task
                new_task = TodoMCPTools.create_todo_with_priority(
                    title=new_task_data["title"],
                    description=new_task_data["description"],
                    user_id=new_task_data["user_id"],
                    priority=new_task_data["priority"],
                    tags=new_task_data["tags"],
                    due_date=new_task_data["due_date"],
                )

                logger.info(f"Successfully created next recurring task with ID {new_task['id']} for original task {task_data['id']}")

                # Publish an event for the newly created recurring task
                from events.producer import EventProducer
                await EventProducer.publish_event("task-created", {
                    "id": new_task["id"],
                    "title": new_task["title"],
                    "user_id": new_task["userId"],
                    "recurrence_source_id": task_data["id"],  # Link to the original recurring task
                    "is_recurring_instance": True
                })

        except Exception as e:
            logger.error(f"Failed to create next recurring task for {task_data['id']}: {e}")
            raise e

    @staticmethod
    def _calculate_next_occurrence(last_occurrence_str: str, pattern_data: Dict[str, Any]) -> datetime:
        """
        Calculate the next occurrence date based on the recurrence pattern.

        Args:
            last_occurrence_str: The date string of the last occurrence
            pattern_data: The recurrence pattern data

        Returns:
            The next occurrence date, or None if the recurrence should end
        """
        from datetime import datetime, timedelta
        import calendar

        if not last_occurrence_str:
            return None

        try:
            last_date = datetime.fromisoformat(last_occurrence_str.replace('Z', '+00:00'))
        except ValueError:
            logger.error(f"Invalid date format: {last_occurrence_str}")
            return None

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
    async def _handle_reminder_due_soon(data: Dict[str, Any]):
        """
        Handle a reminder due soon event.
        
        Args:
            data: The event data
        """
        logger.info(f"Handling reminder due soon event: {data}")
        
        # In a real implementation, this would send a notification to the user
        # For now, we'll just log it
        pass
    
    @staticmethod
    async def _handle_reminder_overdue(data: Dict[str, Any]):
        """
        Handle a reminder overdue event.

        Args:
            data: The event data
        """
        logger.info(f"Handling reminder overdue event: {data}")

        # In a real implementation, this would send a notification to the user
        # For now, we'll just log it
        pass

    @staticmethod
    async def _schedule_reminder_for_task(task_id: str, scheduled_time: str, user_id: str):
        """
        Schedule a reminder for a task.

        Args:
            task_id: The ID of the task to create a reminder for
            scheduled_time: When the reminder should be triggered (ISO format)
            user_id: The ID of the user who owns the task
        """
        from mcp.tools import TodoMCPTools
        from datetime import datetime
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Scheduling reminder for task {task_id} at {scheduled_time}")

        try:
            # Use the MCP tool to create the reminder
            reminder_data = TodoMCPTools.create_reminder_for_task(
                todo_id=task_id,
                scheduled_time=scheduled_time,
                user_id=user_id
            )

            logger.info(f"Successfully scheduled reminder with ID {reminder_data.get('id')} for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to schedule reminder for task {task_id}: {e}")
            raise e
    
    @staticmethod
    async def _handle_task_event(topic: str, data: Dict[str, Any]):
        """
        Handle a generic task event.
        
        Args:
            topic: The event topic
            data: The event data
        """
        logger.info(f"Handling task event {topic}: {data}")
        
        # Update the event status in the database
        with Session(engine) as session:
            # Create an event record
            event = Event(
                event_type=topic.replace("task-", ""),
                payload=data,
                source="event_consumer",
                processed_status=EventStatus.processed
            )
            session.add(event)
            session.commit()


# Background task to consume events
async def start_event_consumer():
    """
    Start the event consumer to listen for and process events.
    """
    topics = [
        "task-events",
        "reminders",
        "task-updates",
        "task-created",
        "task-completed",
        "reminder-due-soon",
        "reminder-overdue"
    ]
    
    await EventConsumer.consume_events(topics)