import argparse
import sys
import json
import os
from typing import List, Dict, Optional


class Task:
    """Represents a todo item with properties that allow users to track their tasks."""

    def __init__(self, task_id: int, title: str, description: str = "", completed: bool = False):
        self.id = task_id
        self.title = title
        self.description = description
        self.completed = completed


class TodoApp:
    """CLI Todo Application that stores tasks in memory."""

    def __init__(self):
        self.tasks: List[Dict] = []
        self.next_id = 1

    def add_task(self, title: str, description: str = "") -> Dict:
        """Add a new task to the todo list."""
        if not title.strip():
            raise ValueError("Task title cannot be empty")

        task = {
            "id": self.next_id,
            "title": title.strip(),
            "description": description.strip(),
            "completed": False
        }

        self.tasks.append(task)
        self.next_id += 1
        return task

    def list_tasks(self) -> List[Dict]:
        """Return all tasks in the todo list."""
        return self.tasks

    def get_task_by_id(self, task_id: int) -> Optional[Dict]:
        """Get a task by its ID."""
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def update_task(self, task_id: int, title: str = None, description: str = None) -> bool:
        """Update an existing task's title and/or description."""
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        if title is not None:
            title = title.strip()
            if title:
                task["title"] = title
            else:
                raise ValueError("Task title cannot be empty")

        if description is not None:
            task["description"] = description.strip()

        return True

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by its ID."""
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        self.tasks.remove(task)
        # Renumber remaining tasks to maintain sequential IDs
        self.renumber_tasks()
        return True

    def renumber_tasks(self):
        """Renumber all tasks to maintain sequential IDs starting from 1."""
        # Sort tasks by current ID to maintain consistent ordering
        self.tasks.sort(key=lambda x: x["id"])
        # Assign new sequential IDs starting from 1
        for i, task in enumerate(self.tasks):
            task["id"] = i + 1
        # Update next_id based on the number of tasks
        self.next_id = len(self.tasks) + 1

    def mark_task_complete(self, task_id: int) -> bool:
        """Mark a task as complete."""
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        task["completed"] = True
        return True

    def mark_task_incomplete(self, task_id: int) -> bool:
        """Mark a task as incomplete."""
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        task["completed"] = False
        return True


def setup_argparser():
    """Setup command-line argument parsing using argparse."""
    parser = argparse.ArgumentParser(
        description="CLI Todo Application - Manage your tasks from the command line"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("description", nargs="?", default="", help="Task description")

    # List command
    list_parser = subparsers.add_parser("list", help="List all tasks")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update a task")
    update_parser.add_argument("id", type=int, help="Task ID")
    update_parser.add_argument("--title", help="New task title")
    update_parser.add_argument("--description", help="New task description")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("id", type=int, help="Task ID")

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark a task as complete")
    complete_parser.add_argument("id", type=int, help="Task ID")

    # Incomplete command
    incomplete_parser = subparsers.add_parser("incomplete", help="Mark a task as incomplete")
    incomplete_parser.add_argument("id", type=int, help="Task ID")

    return parser



def load_tasks():
    """Load tasks from a JSON file if it exists."""
    if os.path.exists("tasks.json"):
        with open("tasks.json", "r") as f:
            data = json.load(f)
            return data.get("tasks", []), data.get("next_id", 1)
    return [], 1

def save_tasks(tasks, next_id):
    """Save tasks to a JSON file."""
    with open("tasks.json", "w") as f:
        json.dump({"tasks": tasks, "next_id": next_id}, f)

def interactive_mode(app):
    """Run the application in interactive mode."""
    print("Welcome to the Interactive Todo App!")
    print("Commands: add, list, update, delete, complete, incomplete, exit")
    print("Example: add 'Buy groceries' 'Milk and bread'")

    while True:
        try:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0].lower()

            if command == "exit":
                print("Goodbye!")
                break
            elif command == "list":
                tasks = app.list_tasks()
                if not tasks:
                    print("No tasks found.")
                else:
                    for task in tasks:
                        status = "X" if task["completed"] else "O"
                        print(f"{task['id']}. [{status}] {task['title']}")
                        if task['description']:
                            print(f"    {task['description']}")
            elif command == "add":
                if len(parts) >= 2:
                    # Join the remaining parts as the title (in case it has spaces)
                    title_parts = parts[1:]
                    # If there are quotes, handle them properly
                    title = ' '.join(title_parts)
                    # Remove quotes if present
                    if title.startswith('"') and title.endswith('"') and len(title) > 1:
                        title = title[1:-1]
                    elif title.startswith("'") and title.endswith("'") and len(title) > 1:
                        title = title[1:-1]

                    description = ""
                    # If there's a quoted description part after the title
                    if ' "' in user_input or " '" in user_input:
                        desc_start = user_input.find(' "')
                        if desc_start == -1:  # Try single quotes
                            desc_start = user_input.find(" '")
                        if desc_start != -1:
                            description = user_input[desc_start + 2:]  # Skip the quote and space
                            if description.endswith('"') or description.endswith("'"):
                                description = description[:-1]  # Remove trailing quote
                            title = user_input[len(command)+1:desc_start].strip().strip('"\'')

                    task = app.add_task(title, description)
                    save_tasks(app.tasks, app.next_id)  # Save after adding
                    print(f"Added task #{task['id']}: {task['title']}")
                else:
                    print("Usage: add 'title' ['description']")
            elif command in ["complete", "incomplete", "delete"]:
                if len(parts) == 2:
                    try:
                        task_id = int(parts[1])
                        if command == "complete":
                            success = app.mark_task_complete(task_id)
                            if success:
                                save_tasks(app.tasks, app.next_id)  # Save after marking complete
                                print(f"Marked task #{task_id} as complete")
                            else:
                                print(f"Error: Task with ID {task_id} not found")
                        elif command == "incomplete":
                            success = app.mark_task_incomplete(task_id)
                            if success:
                                save_tasks(app.tasks, app.next_id)  # Save after marking incomplete
                                print(f"Marked task #{task_id} as incomplete")
                            else:
                                print(f"Error: Task with ID {task_id} not found")
                        elif command == "delete":
                            success = app.delete_task(task_id)
                            if success:
                                save_tasks(app.tasks, app.next_id)  # Save after deleting
                                print(f"Deleted task #{task_id}")
                            else:
                                print(f"Error: Task with ID {task_id} not found")
                    except ValueError:
                        print(f"Error: Task ID must be a number")
                else:
                    print(f"Usage: {command} <task_id>")
            elif command == "update":
                if len(parts) >= 3:
                    try:
                        task_id = int(parts[1])
                        # For simplicity in interactive mode, we'll treat everything after task_id as the new title
                        new_title = ' '.join(parts[2:])
                        # Remove quotes if present
                        if new_title.startswith('"') and new_title.endswith('"') and len(new_title) > 1:
                            new_title = new_title[1:-1]
                        elif new_title.startswith("'") and new_title.endswith("'") and len(new_title) > 1:
                            new_title = new_title[1:-1]

                        success = app.update_task(task_id, new_title)
                        if success:
                            save_tasks(app.tasks, app.next_id)  # Save after updating
                            print(f"Updated task #{task_id}")
                        else:
                            print(f"Error: Task with ID {task_id} not found")
                    except ValueError:
                        print(f"Error: Task ID must be a number")
                else:
                    print(f"Usage: update <task_id> 'new_title'")
            else:
                print(f"Unknown command: {command}")
                print("Available commands: add, list, update, delete, complete, incomplete, exit")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def main():
    """Main application function."""
    parser = setup_argparser()
    args = parser.parse_args()

    # Load existing tasks and next ID
    tasks, next_id = load_tasks()

    # Create application instance with loaded data
    app = TodoApp()
    app.tasks = tasks
    app.next_id = next_id

    # If no command-line arguments provided, run in interactive mode
    if not args.command:
        interactive_mode(app)
        return

    try:
        if args.command == "add":
            task = app.add_task(args.title, args.description)
            save_tasks(app.tasks, app.next_id)  # Save after adding
            print(f"Added task #{task['id']}: {task['title']}")
        elif args.command == "list":
            tasks = app.list_tasks()
            if not tasks:
                print("No tasks found.")
            else:
                for task in tasks:
                    status = "X" if task["completed"] else "O"
                    print(f"{task['id']}. [{status}] {task['title']}")
                    if task['description']:
                        print(f"    {task['description']}")
        elif args.command == "update":
            # For update, title and description are optional arguments
            success = app.update_task(args.id, getattr(args, 'title', None), getattr(args, 'description', None))
            if success:
                save_tasks(app.tasks, app.next_id)  # Save after updating
                print(f"Updated task #{args.id}")
            else:
                print(f"Error: Task with ID {args.id} not found")
        elif args.command == "delete":
            success = app.delete_task(args.id)
            if success:
                save_tasks(app.tasks, app.next_id)  # Save after deleting
                print(f"Deleted task #{args.id}")
            else:
                print(f"Error: Task with ID {args.id} not found")
        elif args.command == "complete":
            success = app.mark_task_complete(args.id)
            if success:
                save_tasks(app.tasks, app.next_id)  # Save after marking complete
                print(f"Marked task #{args.id} as complete")
            else:
                print(f"Error: Task with ID {args.id} not found")
        elif args.command == "incomplete":
            success = app.mark_task_incomplete(args.id)
            if success:
                save_tasks(app.tasks, app.next_id)  # Save after marking incomplete
                print(f"Marked task #{args.id} as incomplete")
            else:
                print(f"Error: Task with ID {args.id} not found")
        else:
            parser.print_help()

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
