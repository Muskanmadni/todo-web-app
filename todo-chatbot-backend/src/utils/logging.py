import logging
from datetime import datetime
from typing import Any, Dict


def setup_logger(name: str, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the specified name and configuration
    """
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')

    if log_file:
        handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def log_todo_operation(operation: str, user_id: str, todo_id: str = None, details: Dict[str, Any] = None):
    """
    Log a todo operation with relevant details
    """
    logger = setup_logger("todo_operations")
    
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "operation": operation,
        "user_id": user_id,
        "todo_id": todo_id,
        "details": details
    }
    
    logger.info(f"Todo operation: {log_data}")


def log_conversation_event(event: str, user_id: str, conversation_id: str, details: Dict[str, Any] = None):
    """
    Log a conversation event with relevant details
    """
    logger = setup_logger("conversation_events")
    
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event,
        "user_id": user_id,
        "conversation_id": conversation_id,
        "details": details
    }
    
    logger.info(f"Conversation event: {log_data}")


def log_ai_interaction(query: str, response: str, user_id: str = None, conversation_id: str = None):
    """
    Log an AI interaction with query and response
    """
    logger = setup_logger("ai_interactions")
    
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "response": response,
        "user_id": user_id,
        "conversation_id": conversation_id
    }
    
    logger.info(f"AI interaction: {log_data}")