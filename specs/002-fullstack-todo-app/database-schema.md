# Persistent Data Model: Todo Application

## Users Entity (Externally Managed)

The Users entity is managed externally by Better Auth, which handles authentication-related data. The system will use the user identifier provided by Better Auth for associating tasks with users.

### External User Attributes
- `id`: Unique identifier provided by Better Auth (string)
- `email`: User's email address (string, unique)
- `name`: User's display name (string, optional)
- `created_at`: Account creation timestamp (datetime)
- `updated_at`: Last account update timestamp (datetime)

## Tasks Entity

### Field Definitions and Constraints

#### Primary Key
- `id`: Unique identifier for the task (UUID, primary key, auto-generated)

#### Core Attributes
- `title`: Task title or description (string, max 255 characters, not null)
- `description`: Detailed task description (text, optional)
- `completed`: Task completion status (boolean, default false)
- `due_date`: Optional deadline for the task (datetime, optional)
- `priority`: Task priority level (enum: low, medium, high, default: medium)

#### Metadata
- `user_id`: Foreign key linking task to owner user (string, not null, references Better Auth user ID)
- `created_at`: Task creation timestamp (datetime, not null, default now)
- `updated_at`: Last update timestamp (datetime, not null, default now, auto-updated)

#### Constraints
- `title` must not be empty or contain only whitespace
- `user_id` must reference a valid user in the authentication system
- `due_date` must be a future date if provided
- `priority` must be one of the allowed values

## Relationships and Indexes

### Relationships
- One User (managed by Better Auth) to Many Tasks (one-to-many)
- Foreign key relationship: Tasks.user_id → Better Auth User.id

### Indexes
- Index on `user_id` for efficient retrieval of user-specific tasks
- Index on `completed` for filtering completed/incomplete tasks
- Index on `due_date` for sorting and filtering by deadline
- Composite index on `(user_id, completed)` for common query patterns
- Index on `created_at` for chronological ordering

## Ownership Enforcement Rules

### Data Access
- All queries must filter by `user_id` to ensure users only see their own tasks
- Creation operations must set `user_id` to the authenticated user's ID
- Update and delete operations must verify the task belongs to the authenticated user

### Business Logic
- Tasks cannot be transferred between users
- Only the owner of a task can modify or delete it
- System automatically assigns `user_id` during task creation based on authenticated user
- User ID cannot be changed after task creation

### Security
- Database queries must always include user ID in WHERE clauses
- Direct database access (if needed for admin operations) must still respect ownership rules
- No database-level permissions should allow cross-user data access
- Audit trail should be maintained for any operations affecting task ownership