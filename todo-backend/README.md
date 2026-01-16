# AI-Powered Todo Chatbot Backend

This project implements an AI-powered chatbot interface for managing todos through natural language using MCP (Model Context Protocol) server architecture.

## Overview

The backend provides a FastAPI application that allows users to interact with their todo list through a conversational AI interface. Users can speak to the chatbot in natural language to create, update, and manage their todo items.

## Features

- Natural language processing for todo management
- MCP (Model Context Protocol) tools for standardized operations
- Conversation persistence and context management
- Analytics and monitoring for usage tracking
- User authentication and data isolation

## Architecture

- **Backend**: Python with FastAPI
- **Database**: PostgreSQL with SQLModel
- **AI Integration**: Google Gemini AI with MCP tools
- **Frontend**: Next.js with chat interface (separate repository)

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (or Neon Serverless PostgreSQL account)
- Google Gemini API key
- Better Auth compatible environment

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd todo-backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the `todo-backend` directory with the following:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/todo_chatbot
   # If using Neon:
   # DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/todo_chatbot?sslmode=require

   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_secret_key_here
   BETTER_AUTH_SECRET=your_better_auth_secret_here
   ```

5. Run database migrations:
   ```bash
   python -m alembic upgrade head
   ```

6. Start the backend server:
   ```bash
   python main.py
   # Or using uvicorn:
   uvicorn main:app --reload --port 8000
   ```

## Usage

### API Endpoints

- `POST /api/chat/conversation` - Send a message to the chatbot and receive a response
- `GET /health` - Health check endpoint
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /tasks` - Get user's tasks
- `POST /tasks` - Create a new task

### Natural Language Commands

The chatbot supports the following natural language commands:

- **Create Todo**: "Add a todo: Buy groceries" or "Create todo: Complete project"
- **Complete Todo**: "Mark 'Buy groceries' as complete" or "Complete 'Complete project'"
- **Delete Todo**: "Delete 'Buy groceries'" or "Remove 'Complete project'"
- **Show Todos**: "Show my todos" or "What are my todos?"

### MCP Tools

The system implements the following MCP tools:

- `create_todo`: Creates a new todo item
- `update_todo`: Updates an existing todo item
- `delete_todo`: Deletes a todo item
- `mark_todo_completed`: Marks a todo as completed
- `mark_todo_pending`: Marks a todo as pending

## Analytics and Monitoring

The system tracks the following events:

- Chat requests and responses
- Todo creation, updates, and deletions
- Error occurrences
- User engagement metrics

Analytics are logged via the `AnalyticsService` and can be extended to integrate with external analytics platforms.

## Testing

Run the unit and integration tests:

```bash
pytest tests/
```

## Environment Variables

- `DATABASE_URL`: Database connection string
- `GEMINI_API_KEY`: Google Gemini API key for AI functionality
- `SECRET_KEY`: Secret key for JWT tokens
- `BETTER_AUTH_SECRET`: Secret key for Better Auth

## Troubleshooting

### Common Issues

1. **Database connection errors**: Ensure your PostgreSQL server is running and credentials are correct
2. **API key errors**: Verify your Google Gemini API key is valid and properly set in environment variables
3. **CORS errors**: Check that your frontend URL is allowed in the backend CORS settings

### Getting Help

- Check the logs in your terminal for error messages
- Verify all environment variables are set correctly
- Ensure all dependencies are installed properly

## Development

### Backend Development
- The main application logic is in `main.py`
- API endpoints are defined in the `api/` directory
- Database models are in the `models/` directory
- MCP tools are implemented in the `mcp/` directory

### Running in Development

```bash
uvicorn main:app --reload --port 8000
```

## Deployment

1. **Backend**: Deploy to a cloud provider that supports Python applications (AWS, GCP, Azure, or platforms like Railway, Heroku)
2. **Frontend**: Deploy to Vercel, Netlify, or similar platforms that support Next.js applications