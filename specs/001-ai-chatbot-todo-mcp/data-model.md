# Data Model: AI-Powered Chatbot for Todo Management

## Overview
This document defines the data models for the AI-powered chatbot todo management system, including entities, relationships, and validation rules.

## Core Entities

### 1. User
Represents an authenticated user of the system.

```python
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(sa_column=Column(String, unique=True, index=True, nullable=False))
    name: str = Field(sa_column=Column(String, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    todos: List["Todo"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")
```

**Validation Rules:**
- Email must be a valid email format
- Email must be unique
- Name must not be empty

### 2. Todo
Represents a todo item created by a user.

```python
class Todo(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(sa_column=Column(String, nullable=False))
    description: Optional[str] = Field(default=None)
    status: str = Field(default="pending", sa_column=Column(String, nullable=False))  # pending, completed
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    user: User = Relationship(back_populates="todos")
```

**Validation Rules:**
- Title must not be empty
- Status must be one of: "pending", "completed"
- If status is "completed", completed_at must be set
- Each todo must belong to a valid user

### 3. Conversation
Represents a conversation session between a user and the AI chatbot.

```python
class Conversation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    title: str = Field(sa_column=Column(String, nullable=False))  # Auto-generated from first message or summary
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")
```

**Validation Rules:**
- Title must not be empty
- Each conversation must belong to a valid user
- Updated_at must be >= created_at

### 4. Message
Represents an individual message in a conversation.

```python
class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id", nullable=False)
    role: str = Field(sa_column=Column(String, nullable=False))  # user, assistant, system
    content: str = Field(sa_column=Column(Text, nullable=False))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(default=None)  # Store additional data like AI tokens used, etc.
    
    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

**Validation Rules:**
- Role must be one of: "user", "assistant", "system"
- Content must not be empty
- Each message must belong to a valid conversation

## State Transitions

### Todo Status Transitions
- `pending` → `completed`: When a user marks a todo as complete
- `completed` → `pending`: When a user reopens a completed todo

### Conversation Lifecycle
- New conversation created when user starts chatting
- Conversation updated with each new message
- Conversation archived after inactivity period (implementation-specific)

## Relationships

1. **User → Todo**: One-to-many (one user can have many todos)
2. **User → Conversation**: One-to-many (one user can have many conversations)
3. **Conversation → Message**: One-to-many (one conversation can have many messages)

## Indexes for Performance

- User.email: Unique index for authentication
- Todo.user_id: Index for user-specific todo queries
- Conversation.user_id: Index for user-specific conversation queries
- Message.conversation_id: Index for conversation-specific message queries
- Message.timestamp: Index for chronological ordering of messages