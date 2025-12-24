# Data Model: CLI Todo Application

## Task Entity

**Definition**: Represents a todo item with properties that allow users to track their tasks.

**Fields**:
- `id`: Integer (auto-incrementing unique identifier)
- `title`: String (non-empty, required)
- `description`: String (optional, can be empty)
- `completed`: Boolean (default: False)

**Relationships**: None (standalone entity)

**Validation Rules**:
- `id` must be unique and auto-generated
- `title` must be a non-empty string
- `completed` must be a boolean value (True/False)

**State Transitions**:
- Default state: `completed = False`
- State change: `completed` can be toggled between True and False

## In-Memory Storage Structure

**Implementation**: A Python list of dictionaries where each dictionary represents a Task entity.

**Example Structure**:
```python
tasks = [
    {
        "id": 1,
        "title": "Sample task",
        "description": "This is a sample task description",
        "completed": False
    },
    {
        "id": 2,
        "title": "Another task",
        "description": "This is another task",
        "completed": True
    }
]
```

**Operations**:
- CREATE: Add a new dictionary to the list with a unique ID
- READ: Access tasks by iterating through the list
- UPDATE: Modify fields of a specific task dictionary by ID
- DELETE: Remove a specific task dictionary from the list by ID