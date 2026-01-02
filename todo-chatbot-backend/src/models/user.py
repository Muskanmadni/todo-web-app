from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid


class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False)
    name: Optional[str] = Field(default=None, max_length=255)


class User(UserBase, table=True):
    """
    Represents a user in the system
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)