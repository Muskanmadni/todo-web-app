# CLI Command Interface Specification

## Command Structure
The application follows the pattern: `python main.py <command> [arguments]`

## Commands

### ADD Command
- **Signature**: `python main.py add <title> [description]`
- **Purpose**: Add a new task to the todo list
- **Parameters**:
  - `title` (required): Task title as a string
  - `description` (optional): Task description as a string
- **Response**: Success message with assigned task ID or error message

### LIST Command
- **Signature**: `python main.py list`
- **Purpose**: Display all tasks with their details and status
- **Parameters**: None
- **Response**: Formatted list of all tasks with ID, title, description, and completion status

### UPDATE Command
- **Signature**: `python main.py update <id> <new_title> [new_description]`
- **Purpose**: Update an existing task's title and/or description
- **Parameters**:
  - `id` (required): Task ID as integer
  - `new_title` (required): New task title as string
  - `new_description` (optional): New task description as string
- **Response**: Success message or error message if task ID not found

### DELETE Command
- **Signature**: `python main.py delete <id>`
- **Purpose**: Remove a task from the todo list
- **Parameters**:
  - `id` (required): Task ID as integer
- **Response**: Success message or error message if task ID not found

### COMPLETE Command
- **Signature**: `python main.py complete <id>`
- **Purpose**: Mark a task as complete
- **Parameters**:
  - `id` (required): Task ID as integer
- **Response**: Success message or error message if task ID not found

### INCOMPLETE Command
- **Signature**: `python main.py incomplete <id>`
- **Purpose**: Mark a task as incomplete
- **Parameters**:
  - `id` (required): Task ID as integer
- **Response**: Success message or error message if task ID not found

## Error Handling
- Invalid commands will result in a help message display
- Invalid task IDs will result in "Task not found" error message
- Missing required arguments will result in usage instructions