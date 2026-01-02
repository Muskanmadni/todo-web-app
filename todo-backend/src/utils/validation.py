from pydantic import BaseModel, validator
from typing import Optional, List
from enum import Enum
import re


class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TodoValidation:
    """
    Validation utilities for todo operations
    """
    
    @staticmethod
    def validate_title(title: str) -> bool:
        """
        Validate todo title - must be between 1 and 200 characters
        """
        if not title or len(title) < 1 or len(title) > 200:
            return False
        return True
    
    @staticmethod
    def validate_description(description: Optional[str]) -> bool:
        """
        Validate todo description - must be less than 1000 characters if provided
        """
        if description and len(description) > 1000:
            return False
        return True
    
    @staticmethod
    def validate_priority(priority: str) -> bool:
        """
        Validate todo priority - must be one of the allowed values
        """
        try:
            PriorityEnum(priority)
            return True
        except ValueError:
            return False


class ComplexOperationValidation:
    """
    Validation utilities for complex operations
    """
    
    @staticmethod
    def validate_multiple_operations(operations: List[dict]) -> bool:
        """
        Validate a list of operations to ensure they are properly structured
        """
        if not operations:
            return False
        
        for op in operations:
            if not isinstance(op, dict) or 'type' not in op:
                return False
                
            op_type = op.get('type')
            if op_type not in ['create', 'update', 'delete', 'search']:
                return False
        
        return True
    
    @staticmethod
    def validate_complex_request_text(text: str) -> bool:
        """
        Validate that the complex request text is not empty and has reasonable length
        """
        if not text or len(text) < 1 or len(text) > 1000:
            return False
        return True