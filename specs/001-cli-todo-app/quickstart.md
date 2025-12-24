# Quickstart Guide: CLI Todo Application

## Prerequisites
- Python 3.13 or higher
- UV package manager (for dependency management if needed)

## Setup
1. Clone the repository
2. Navigate to the project directory
3. Ensure Python 3.13+ is installed and accessible

## Running the Application
Execute the application from the project root:
```bash
cd src
python main.py
```

## Basic Usage Commands

### Add a new task
```bash
python main.py add "Task Title" "Task Description"
```

### View all tasks
```bash
python main.py list
```

### Update a task
```bash
python main.py update <task_id> "New Title" "New Description"
```

### Delete a task
```bash
python main.py delete <task_id>
```

### Mark a task as complete
```bash
python main.py complete <task_id>
```

### Mark a task as incomplete
```bash
python main.py incomplete <task_id>
```

## Example Workflow
1. Add a task: `python main.py add "Buy groceries" "Milk, bread, eggs"`
2. View tasks: `python main.py list`
3. Mark as complete: `python main.py complete 1`
4. Update task: `python main.py update 1 "Buy groceries" "Milk, bread, eggs, fruits"`
5. Delete task: `python main.py delete 1`

## Notes
- All data is stored in memory and will be lost when the application exits
- Task IDs are auto-generated and sequential
- The application provides user-friendly error messages for invalid operations