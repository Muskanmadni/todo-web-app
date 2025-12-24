import subprocess
import sys
import os
import tempfile
from unittest.mock import patch
import pytest


def test_add_command():
    """Integration test for add command."""
    # Test adding a task
    result = subprocess.run([
        sys.executable, "main.py", "add", "Test Task", "Test Description"
    ], capture_output=True, text=True, cwd="console-todo-app")
    
    assert result.returncode == 0
    assert "Added task" in result.stdout


def test_list_command():
    """Integration test for list command."""
    # First add a task
    add_result = subprocess.run([
        sys.executable, "main.py", "add", "Test Task", "Test Description"
    ], capture_output=True, text=True, cwd="console-todo-app")
    
    assert add_result.returncode == 0
    
    # Then list tasks
    list_result = subprocess.run([
        sys.executable, "main.py", "list"
    ], capture_output=True, text=True, cwd="console-todo-app")
    
    assert list_result.returncode == 0
    assert "Test Task" in list_result.stdout


def test_complete_command():
    """Integration test for complete command."""
    # First add a task
    add_result = subprocess.run([
        sys.executable, "main.py", "add", "Test Task"
    ], capture_output=True, text=True, cwd="console-todo-app")
    
    assert add_result.returncode == 0
    assert "Added task" in add_result.stdout
    
    # Extract task ID from the output (it should be 1)
    # Then mark as complete
    complete_result = subprocess.run([
        sys.executable, "main.py", "complete", "1"
    ], capture_output=True, text=True, cwd="console-todo-app")
    
    assert complete_result.returncode == 0
    assert "Marked task #1 as complete" in complete_result.stdout


def test_delete_command():
    """Integration test for delete command."""
    # First add a task
    add_result = subprocess.run([
        sys.executable, "main.py", "add", "Test Task to Delete"
    ], capture_output=True, text=True, cwd="console-todo-app")
    
    assert add_result.returncode == 0
    assert "Added task" in add_result.stdout
    
    # Then delete the task
    delete_result = subprocess.run([
        sys.executable, "main.py", "delete", "1"
    ], capture_output=True, text=True, cwd="console-todo-app")
    
    assert delete_result.returncode == 0
    assert "Deleted task #1" in delete_result.stdout


def test_update_command():
    """Integration test for update command."""
    # First add a task
    add_result = subprocess.run([
        sys.executable, "main.py", "add", "Old Title", "Old Description"
    ], capture_output=True, text=True, cwd="console-todo-app")
    
    assert add_result.returncode == 0
    assert "Added task" in add_result.stdout
    
    # Then update the task
    update_result = subprocess.run([
        sys.executable, "main.py", "update", "1", "--title", "New Title", "--description", "New Description"
    ], capture_output=True, text=True, cwd="console-todo-app")
    
    assert update_result.returncode == 0
    assert "Updated task #1" in update_result.stdout