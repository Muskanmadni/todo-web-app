# Data Model: Advanced AI-Powered Todo Chatbot

## Entity: Task

### Fields
- `id` (UUID, Primary Key): Unique identifier for the task
- `title` (String, Required): Title of the task
- `description` (Text, Optional): Detailed description of the task
- `completed` (Boolean, Default: false): Completion status
- `due_date` (DateTime, Optional): Date and time when the task is due
- `priority` (Enum: 'low' | 'medium' | 'high', Default: 'medium'): Priority level
- `tags` (JSON Array, Optional): Array of tag strings for categorization
- `recurrence_pattern` (JSON Object, Optional): Defines recurrence rules (frequency, interval, end conditions)
- `user_id` (UUID, Foreign Key): References the user who owns the task
- `created_at` (DateTime, Auto-generated): Timestamp when task was created
- `updated_at` (DateTime, Auto-generated): Timestamp when task was last updated
- `next_occurrence_date` (DateTime, Optional): For recurring tasks, when the next occurrence is due

### Relationships
- Belongs to: User (many tasks to one user)
- Has many: Reminders (one task to many reminders)

### Validation Rules
- Title must be between 1 and 255 characters
- Due date must be in the future if provided
- Priority must be one of the allowed values
- Recurrence pattern must follow a valid format when present

## Entity: User

### Fields
- `id` (UUID, Primary Key): Unique identifier for the user
- `email` (String, Required, Unique): User's email address
- `hashed_password` (String, Required): Hashed password
- `created_at` (DateTime, Auto-generated): Timestamp when user was created
- `updated_at` (DateTime, Auto-generated): Timestamp when user was last updated
- `preferences` (JSON Object, Optional): User preferences including reminder settings

### Relationships
- Has many: Tasks (one user to many tasks)
- Has many: Conversations (one user to many conversations)

### Validation Rules
- Email must be a valid email format
- Email must be unique
- Password must meet security requirements

## Entity: Conversation

### Fields
- `id` (UUID, Primary Key): Unique identifier for the conversation
- `user_id` (UUID, Foreign Key): References the user who owns the conversation
- `title` (String, Optional): Title of the conversation
- `created_at` (DateTime, Auto-generated): Timestamp when conversation was created
- `updated_at` (DateTime, Auto-generated): Timestamp when conversation was last updated

### Relationships
- Belongs to: User (many conversations to one user)
- Has many: Messages (one conversation to many messages)

### Validation Rules
- Title must be between 0 and 255 characters if provided

## Entity: Message

### Fields
- `id` (UUID, Primary Key): Unique identifier for the message
- `conversation_id` (UUID, Foreign Key): References the conversation this message belongs to
- `content` (Text, Required): Content of the message
- `role` (Enum: 'user' | 'assistant' | 'system'): Role of the sender
- `timestamp` (DateTime, Auto-generated): When the message was sent
- `metadata` (JSON Object, Optional): Additional metadata about the message

### Relationships
- Belongs to: Conversation (many messages to one conversation)

### Validation Rules
- Content must not be empty
- Role must be one of the allowed values

## Entity: Reminder

### Fields
- `id` (UUID, Primary Key): Unique identifier for the reminder
- `task_id` (UUID, Foreign Key): References the task this reminder is for
- `scheduled_time` (DateTime, Required): When the reminder should be triggered
- `sent_status` (Enum: 'pending' | 'sent' | 'failed', Default: 'pending'): Status of the reminder
- `delivery_attempts` (Integer, Default: 0): Number of delivery attempts
- `last_attempt_time` (DateTime, Optional): When the last delivery attempt was made
- `created_at` (DateTime, Auto-generated): Timestamp when reminder was created

### Relationships
- Belongs to: Task (many reminders to one task)

### Validation Rules
- Scheduled time must be in the future
- Delivery attempts must be non-negative

## Entity: Event

### Fields
- `id` (UUID, Primary Key): Unique identifier for the event
- `event_type` (String, Required): Type of the event (e.g., 'task-created', 'task-updated', 'reminder-scheduled')
- `payload` (JSON, Required): Event data payload
- `source` (String, Required): Source service that generated the event
- `correlation_id` (UUID, Optional): Correlation ID for tracing
- `processed_status` (Enum: 'pending' | 'processing' | 'processed' | 'failed', Default: 'pending'): Processing status
- `created_at` (DateTime, Auto-generated): Timestamp when event was created
- `processed_at` (DateTime, Optional): Timestamp when event was processed

### Validation Rules
- Event type must be one of the predefined types
- Payload must be valid JSON