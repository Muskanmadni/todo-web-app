"""
Event service for managing system events.
"""
from sqlmodel import Session, select
from models.event import Event, EventStatus
from database import engine
from datetime import datetime
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class EventService:
    """
    Service for managing system events.
    """
    
    @staticmethod
    def create_event(event_type: str, payload: dict, source: str, correlation_id: UUID = None) -> Event:
        """
        Create a new event.
        
        Args:
            event_type: The type of event
            payload: The event data
            source: The source of the event
            correlation_id: Optional correlation ID for tracking related events
            
        Returns:
            The created event
        """
        with Session(engine) as session:
            event = Event(
                event_type=event_type,
                payload=payload,
                source=source,
                correlation_id=correlation_id,
                processed_status=EventStatus.pending
            )
            
            session.add(event)
            session.commit()
            session.refresh(event)
            
            logger.info(f"Created event of type {event_type}")
            
            return event
    
    @staticmethod
    def get_events_by_type(event_type: str, limit: int = 100) -> list[Event]:
        """
        Get events of a specific type.
        
        Args:
            event_type: The type of events to retrieve
            limit: Maximum number of events to return
            
        Returns:
            List of events of the specified type
        """
        with Session(engine) as session:
            events = session.exec(
                select(Event)
                .where(Event.event_type == event_type)
                .order_by(Event.created_at.desc())
                .limit(limit)
            ).all()
            
            return events
    
    @staticmethod
    def get_events_by_status(status: EventStatus, limit: int = 100) -> list[Event]:
        """
        Get events with a specific status.
        
        Args:
            status: The status of events to retrieve
            limit: Maximum number of events to return
            
        Returns:
            List of events with the specified status
        """
        with Session(engine) as session:
            events = session.exec(
                select(Event)
                .where(Event.processed_status == status)
                .order_by(Event.created_at.desc())
                .limit(limit)
            ).all()
            
            return events
    
    @staticmethod
    def update_event_status(event_id: UUID, status: EventStatus) -> Event:
        """
        Update the status of an event.
        
        Args:
            event_id: The ID of the event to update
            status: The new status for the event
            
        Returns:
            The updated event
        """
        with Session(engine) as session:
            event = session.get(Event, event_id)
            if not event:
                raise ValueError(f"Event with ID {event_id} not found")
            
            event.processed_status = status
            event.processed_at = datetime.utcnow()
            
            session.add(event)
            session.commit()
            session.refresh(event)
            
            logger.info(f"Updated event {event_id} status to {status}")
            
            return event
    
    @staticmethod
    def process_event(event_id: UUID) -> Event:
        """
        Process an event by updating its status to 'processed'.
        
        Args:
            event_id: The ID of the event to process
            
        Returns:
            The processed event
        """
        return EventService.update_event_status(event_id, EventStatus.processed)
    
    @staticmethod
    def get_unprocessed_events(limit: int = 100) -> list[Event]:
        """
        Get events that have not yet been processed.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of unprocessed events
        """
        return EventService.get_events_by_status(EventStatus.pending, limit)
    
    @staticmethod
    def delete_event(event_id: UUID) -> bool:
        """
        Delete an event.
        
        Args:
            event_id: The ID of the event to delete
            
        Returns:
            True if the event was deleted, False otherwise
        """
        with Session(engine) as session:
            event = session.get(Event, event_id)
            if not event:
                return False
            
            session.delete(event)
            session.commit()
            
            logger.info(f"Deleted event {event_id}")
            
            return True