import pytest
import sys
import os
from io import StringIO

# Add the src directory to the path so we can import main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from main import TodoApp, Task


class TestTodoApp:
    """Unit tests for the TodoApp class."""
    
    def setup_method(self):
        """Set up a fresh TodoApp instance for each test."""
        self.app = TodoApp()
    
    def test_add_task_with_title_and_description(self):
        """Test adding a task with both title and description."""
        task = self.app.add_task("Test title", "Test description")
        
        assert task["id"] == 1
        assert task["title"] == "Test title"
        assert task["description"] == "Test description"
        assert task["completed"] is False
        assert len(self.app.tasks) == 1
    
    def test_add_task_with_title_only(self):
        """Test adding a task with only a title."""
        task = self.app.add_task("Test title")
        
        assert task["id"] == 1
        assert task["title"] == "Test title"
        assert task["description"] == ""
        assert task["completed"] is False
        assert len(self.app.tasks) == 1
    
    def test_add_task_with_empty_title_raises_error(self):
        """Test that adding a task with an empty title raises an error."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            self.app.add_task("")
    
    def test_add_task_with_whitespace_only_title_raises_error(self):
        """Test that adding a task with only whitespace in title raises an error."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            self.app.add_task("   ")
    
    def test_list_tasks_initially_empty(self):
        """Test that the task list is initially empty."""
        tasks = self.app.list_tasks()
        
        assert tasks == []
    
    def test_list_tasks_after_adding_tasks(self):
        """Test that added tasks appear in the task list."""
        self.app.add_task("Task 1", "Description 1")
        self.app.add_task("Task 2", "Description 2")
        
        tasks = self.app.list_tasks()
        
        assert len(tasks) == 2
        assert tasks[0]["title"] == "Task 1"
        assert tasks[1]["title"] == "Task 2"
    
    def test_get_task_by_id_exists(self):
        """Test getting a task by its ID when it exists."""
        self.app.add_task("Test task", "Test description")
        task = self.app.get_task_by_id(1)
        
        assert task is not None
        assert task["id"] == 1
        assert task["title"] == "Test task"
    
    def test_get_task_by_id_not_exists(self):
        """Test getting a task by its ID when it doesn't exist."""
        task = self.app.get_task_by_id(999)
        
        assert task is None
    
    def test_update_task_title(self):
        """Test updating a task's title."""
        self.app.add_task("Original title", "Original description")
        success = self.app.update_task(1, "New title")
        
        assert success is True
        assert self.app.tasks[0]["title"] == "New title"
        assert self.app.tasks[0]["description"] == "Original description"
    
    def test_update_task_description(self):
        """Test updating a task's description."""
        self.app.add_task("Original title", "Original description")
        success = self.app.update_task(1, description="New description")
        
        assert success is True
        assert self.app.tasks[0]["title"] == "Original title"
        assert self.app.tasks[0]["description"] == "New description"
    
    def test_update_task_title_and_description(self):
        """Test updating both a task's title and description."""
        self.app.add_task("Original title", "Original description")
        success = self.app.update_task(1, "New title", "New description")
        
        assert success is True
        assert self.app.tasks[0]["title"] == "New title"
        assert self.app.tasks[0]["description"] == "New description"
    
    def test_update_task_not_exists(self):
        """Test updating a task that doesn't exist."""
        success = self.app.update_task(999, "New title")
        
        assert success is False
    
    def test_update_task_with_empty_title_raises_error(self):
        """Test that updating a task with an empty title raises an error."""
        self.app.add_task("Original title", "Original description")
        
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            self.app.update_task(1, "")
    
    def test_delete_task_exists(self):
        """Test deleting a task that exists."""
        self.app.add_task("Test task", "Test description")
        success = self.app.delete_task(1)
        
        assert success is True
        assert len(self.app.tasks) == 0
    
    def test_delete_task_not_exists(self):
        """Test deleting a task that doesn't exist."""
        success = self.app.delete_task(999)
        
        assert success is False
    
    def test_mark_task_complete(self):
        """Test marking a task as complete."""
        self.app.add_task("Test task", "Test description")
        success = self.app.mark_task_complete(1)
        
        assert success is True
        assert self.app.tasks[0]["completed"] is True
    
    def test_mark_task_incomplete(self):
        """Test marking a task as incomplete."""
        self.app.add_task("Test task", "Test description")
        self.app.mark_task_complete(1)  # First mark as complete
        success = self.app.mark_task_incomplete(1)  # Then mark as incomplete
        
        assert success is True
        assert self.app.tasks[0]["completed"] is False
    
    def test_mark_task_complete_not_exists(self):
        """Test marking a task as complete when it doesn't exist."""
        success = self.app.mark_task_complete(999)
        
        assert success is False
    
    def test_mark_task_incomplete_not_exists(self):
        """Test marking a task as incomplete when it doesn't exist."""
        success = self.app.mark_task_incomplete(999)
        
        assert success is False