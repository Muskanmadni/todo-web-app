# Quickstart Guide: AI-Powered Todo Chatbot

## Overview
This guide will help you set up and run the AI-powered todo chatbot interface locally. The system consists of a frontend chat interface and a backend API with MCP tools for AI agents.

## Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL (or use Neon Serverless PostgreSQL as specified)
- OpenAI API key
- An API key for the MCP server

## Setup Instructions

### 1. Clone and Navigate to the Repository
```bash
git clone [repository-url]
cd [repository-name]
```

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
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
   # If no requirements.txt exists, install the needed packages:
   pip install fastapi uvicorn sqlmodel openai python-multipart python-jose[cryptography] passlib[bcrypt] better-auth
   ```

4. Set up environment variables by creating a `.env` file:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/dbname
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_secret_key_for_jwt
   MCP_SERVER_KEY=your_mcp_server_key
   ```

5. Run database migrations (if using SQLModel):
   ```bash
   # This command would run the SQLModel migrations
   python -m todo-backend.db.init_db
   ```

6. Start the backend server:
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

### 3. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd todo-chatbot-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or if using yarn
   yarn install
   ```

3. Set up environment variables by creating a `.env` file:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   VITE_OPENAI_API_KEY=your_openai_api_key
   ```

4. Start the frontend development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

### 4. MCP Server Setup
1. The MCP server is integrated into the backend. Ensure the backend is running with the proper configuration.

2. The MCP tools are available at the `/tools/` endpoints as defined in the contracts.

### 5. OpenAI Agent Configuration
1. The agent is configured to use the MCP tools defined in the contracts. Make sure the tools are accessible when the agent runs.

2. Configure the agent to use the appropriate tools for todo management.

## Running the Application
1. Make sure both the backend and frontend are running.
2. Open your browser and navigate to `http://localhost:5173` (or the port specified by the frontend).
3. Sign in or create an account.
4. Start interacting with the chatbot using natural language to manage your todos.

## Testing the API
You can test the API endpoints using the interactive documentation available at `http://localhost:8000/docs` when the backend is running.

## Testing MCP Tools
MCP tools can be tested at the `/tools/` endpoints. The OpenAPI specification for these tools is available in the contracts directory.

## Troubleshooting
- If you encounter database connection issues, verify your `DATABASE_URL` in the `.env` file.
- If the AI agent doesn't respond, check that your OpenAI API key is valid and properly configured.
- If authentication fails, ensure Better Auth is properly configured with the correct secrets.

## Next Steps
- Explore the API documentation at `/docs`
- Review the data models in `data-model.md`
- Check the API contracts in the `contracts/` directory
- Review the task breakdown in `tasks.md` for implementation details