# Todo App Backend

This is the backend API for the Todo application, built with FastAPI and SQLModel.

## Features

- User authentication (register/login)
- Task management (CRUD operations)
- JWT-based authentication
- SQLite database (with option to use PostgreSQL)

## Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get JWT token

### Tasks
- `GET /tasks` - Get all tasks for the authenticated user
- `POST /tasks` - Create a new task
- `GET /tasks/{task_id}` - Get a specific task
- `PUT /tasks/{task_id}` - Update a specific task
- `DELETE /tasks/{task_id}` - Delete a specific task

### Health Check
- `GET /health` - Check API health status

## Setup

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Set up environment variables in `.env` file

3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## Tech Stack

- FastAPI
- SQLModel
- JWT for authentication
- SQLite (default) or PostgreSQL
- Passlib for password hashing
- uvicorn ASGI server