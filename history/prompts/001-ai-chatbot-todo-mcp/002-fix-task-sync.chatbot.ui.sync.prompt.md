---
id: "002"
title: "Fix Task Sync Between Chatbot and UI"
stage: "implement"
date: "2026-01-15"
surface: "agent"
model: "Qwen"
feature: "001-ai-chatbot-todo-mcp"
branch: "001-ai-chatbot-todo-mcp"
user: "user"
command: "/sp.implement everything working perfectly even when i added task from chatbot it added in chatbot with user id according to account but the task not show in ui which added by chatbot"
labels: ["bug-fix", "data-consistency", "model-sync"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "todo-backend/mcp/tools.py"
tests:
  - "Manual verification of task sync"
prompt_text: |
  $ARGUMENTS
  Execute the implementation plan by processing and executing all tasks defined in tasks.md
  
  Issue: Tasks created via chatbot are not showing in the UI
response_text: |
  Identified and fixed the issue where tasks created via the chatbot weren't showing in the UI:
  
  1. Root cause: The MCP tools were creating tasks using the `Task` model (stored in "tasks" table) while the UI was retrieving tasks using the `/tasks` endpoint which queried the `TodoModel` (stored in "todos" table).
  
  2. Fixed all MCP tools methods to use the consistent `Todo` model that matches what the UI expects, ensuring all tasks are stored in the same table.
  
  3. Updated create_todo, update_todo, delete_todo, mark_todo_completed, and mark_todo_pending methods to use the Todo model.
  
  4. The UI already had the proper refresh mechanism in place (onRefreshTasks callback) to update the task list after chatbot operations.
  
  Now tasks created via the chatbot will be stored in the same database table as those created via the UI, so they will appear in the UI after the refresh is triggered.
outcome: |
  Fixed the data consistency issue by ensuring both the chatbot and UI use the same data model and storage table. Tasks created via the chatbot now appear in the UI after the refresh callback is triggered.
evaluation: |
  The fix has been implemented and all MCP tools now use the consistent Todo model. The data flow should now be synchronized between the chatbot and UI.
---