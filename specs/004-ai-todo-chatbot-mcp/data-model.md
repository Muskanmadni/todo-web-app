# Data Model: AI-Powered Todo Chatbot Interface

## Entities

### User
- **Description**: Represents a person interacting with the system
- **Fields**:
  - id: UUID (Primary Key)
  - email: String (Unique, Required)
  - name: String (Optional)
  - created_at: DateTime
  - updated_at: DateTime
- **Relationships**:
  - One-to-Many: User → Todos
  - One-to-Many: User → Conversations

### Todo/Task
- **Description**: Represents a single task with properties like title, description, status, due date, and priority
- **Fields**:
  - id: UUID (Primary Key)
  - title: String (Required)
  - description: Text (Optional)
  - status: String (Enum: 'pending', 'in_progress', 'completed', 'cancelled')
  - due_date: DateTime (Optional)
  - priority: String (Enum: 'low', 'medium', 'high', 'urgent')
  - created_at: DateTime
  - updated_at: DateTime
  - user_id: UUID (Foreign Key to User)
- **Relationships**:
  - Many-to-One: Todo → User
  - One-to-Many: Todo → TodoEvents (optional, for tracking changes)

### Conversation
- **Description**: Represents a single interaction session between user and chatbot, containing context and history
- **Fields**:
  - id: UUID (Primary Key)
  - user_id: UUID (Foreign Key to User)
  - started_at: DateTime
  - last_interaction_at: DateTime
  - context_data: JSON (Stores conversation context, like recently mentioned tasks)
  - created_at: DateTime
  - updated_at: DateTime
- **Relationships**:
  - Many-to-One: Conversation → User
  - One-to-Many: Conversation → Messages (optional, for storing chat history)

### Message
- **Description**: Represents a single message in a conversation
- **Fields**:
  - id: UUID (Primary Key)
  - conversation_id: UUID (Foreign Key to Conversation)
  - sender_type: String (Enum: 'user', 'ai')
  - content: Text (Required)
  - timestamp: DateTime
  - created_at: DateTime
- **Relationships**:
  - Many-to-One: Message → Conversation

## Validation Rules

### User
- Email must be a valid email format
- Email must be unique across all users
- Name must not exceed 255 characters if provided

### Todo/Task
- Title must be between 1 and 255 characters
- Status must be one of the defined enum values
- Priority must be one of the defined enum values
- Due date must be in the future if provided
- User_id must reference an existing user

### Conversation
- User_id must reference an existing user
- Context_data must be a valid JSON object
- Started_at must not be in the future
- Last_interaction_at must not be before started_at

### Message
- Conversation_id must reference an existing conversation
- Sender_type must be one of the defined enum values
- Content must not be empty
- Timestamp must not be in the future

## State Transitions

### Todo/Task Status Transitions
- 'pending' → 'in_progress': When user starts working on the task
- 'in_progress' → 'completed': When user marks task as completed
- 'in_progress' → 'pending': When user needs to go back to pending
- 'pending' → 'cancelled': When user cancels the task
- 'in_progress' → 'cancelled': When user cancels an in-progress task
- 'completed' → 'pending': When user reopens a completed task (optional)

## Indexes

### Todo/Task
- Index on user_id for efficient user-specific queries
- Index on status for filtering by status
- Index on due_date for date-based queries
- Composite index on (user_id, status) for common user-status queries

### Conversation
- Index on user_id for efficient user-specific queries
- Index on last_interaction_at for ordering conversations by recency

### Message
- Index on conversation_id for efficient conversation-specific queries
- Index on timestamp for ordering messages chronologically