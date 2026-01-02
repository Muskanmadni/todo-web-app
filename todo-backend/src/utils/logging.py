import logging
from datetime import datetime
from typing import Optional
import json

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name
    """
    return logging.getLogger(name)

def log_todo_operation(
    operation: str, 
    user_id: str, 
    todo_id: Optional[str] = None, 
    details: Optional[dict] = None
):
    """
    Log todo operations with standardized format
    """
    logger = get_logger("todo_operations")
    
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "operation": operation,
        "user_id": user_id,
        "todo_id": todo_id,
        "details": details
    }
    
    logger.info(json.dumps(log_data))

def log_conversation_context_operation(
    operation: str,
    user_id: str,
    conversation_id: Optional[str] = None,
    details: Optional[dict] = None
):
    """
    Log conversation context operations with standardized format
    """
    logger = get_logger("conversation_context")
    
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "operation": operation,
        "user_id": user_id,
        "conversation_id": conversation_id,
        "details": details
    }
    
    logger.info(json.dumps(log_data))

def log_complex_operation(
    operation: str,
    user_id: str,
    operation_details: Optional[dict] = None
):
    """
    Log complex operations with standardized format
    """
    logger = get_logger("complex_operations")
    
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "operation": operation,
        "user_id": user_id,
        "operation_details": operation_details
    }
    
    logger.info(json.dumps(log_data))