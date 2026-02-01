"""
Event producer for publishing events using Dapr pub/sub.
"""
import json
from typing import Dict, Any
import asyncio
import logging
from dapr.client import DaprClient as DaprAsyncClient
import os

logger = logging.getLogger(__name__)

DAPR_PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "todo-pubsub")


class EventProducer:
    """
    Producer for publishing events using Dapr pub/sub.
    """

    @classmethod
    async def publish_event(cls, topic: str, data: Dict[str, Any]):
        """
        Publish an event to the specified topic using Dapr.

        Args:
            topic: The Dapr pub/sub topic to publish to
            data: The event data to publish
        """
        try:
            # Use Dapr client to publish the event
            async with DaprAsyncClient() as dapr_client:
                await dapr_client.publish_event(
                    pubsub_name=DAPR_PUBSUB_NAME,
                    topic_name=topic,
                    data=json.dumps(data),
                    data_content_type='application/json'
                )
            logger.info(f"Published event to topic {topic}: {data}")
        except Exception as e:
            logger.error(f"Failed to publish event to topic {topic}: {e}")
            raise e


# Global event producer instance
event_producer = EventProducer()


async def publish_task_event(event_type: str, task_data: dict, user_id: str):
    """
    Convenience function to publish task-related events.

    Args:
        event_type: Type of the event (e.g., 'task.created', 'task.updated', 'task.deleted')
        task_data: Dictionary containing task information
        user_id: ID of the user associated with the task
    """
    # Format the event according to our schema
    event_payload = {
        "id": task_data.get("id"),
        "type": event_type,
        "source": "todo-backend",
        "timestamp": task_data.get("createdAt", task_data.get("updatedAt", task_data.get("completedAt"))),
        "data": task_data,
        "correlationId": task_data.get("id")  # Using task ID as correlation ID
    }

    # Determine the appropriate topic based on event type
    if event_type.startswith("task."):
        topic = "task-events"
    elif event_type.startswith("reminder."):
        topic = "reminders"
    else:
        topic = "task-updates"

    await event_producer.publish_event(topic, event_payload)


# Background task to periodically check for and publish events
async def publish_queued_events():
    """
    Background task to publish any queued events.
    """
    logger.info("Starting event publisher...")

    while True:
        try:
            # In a real implementation, this would fetch events from a queue/db
            # and publish them to Kafka
            pass
        except Exception as e:
            logger.error(f"Error publishing queued events: {e}")

        # Wait for 5 seconds before the next check
        await asyncio.sleep(5)