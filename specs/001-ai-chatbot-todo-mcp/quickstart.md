# Quickstart Guide: AI-Powered Chatbot for Todo Management

## Overview
This guide provides instructions for setting up and running the AI-powered chatbot for todo management application.

## Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn
- PostgreSQL (or Neon Serverless PostgreSQL account)
- Google Gemini API key
- Better Auth compatible environment

## Backend Setup (todo-backend)

1. **Navigate to the backend directory**
   ```bash
   cd todo-backend
   ```

2. **Create a virtual environment and activate it**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the `todo-backend` directory with the following:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/todo_chatbot
   # If using Neon:
   # DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/todo_chatbot?sslmode=require
   
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_secret_key_here
   BETTER_AUTH_SECRET=your_better_auth_secret_here
   ```

5. **Run database migrations**
   ```bash
   python -m alembic upgrade head
   ```

6. **Start the backend server**
   ```bash
   python main.py
   # Or using uvicorn:
   uvicorn main:app --reload --port 8000
   ```

## Frontend Setup (todo-frontend)

1. **Navigate to the frontend directory**
   ```bash
   cd todo-frontend/my-app
   ```

2. **Install dependencies**
   ```bash
   npm install
   # Or if using yarn:
   yarn install
   ```

3. **Set up environment variables**
   Create a `.env.local` file in the `todo-frontend/my-app` directory with the following:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Run the development server**
   ```bash
   npm run dev
   # Or if using yarn:
   yarn dev
   ```

5. **Open your browser**
   Visit [http://localhost:3000](http://localhost:3000) to see the application.

## Using the Chatbot

1. **Authentication**: Sign in using the authentication system.

2. **Starting a conversation**: 
   - Navigate to the chatbot interface
   - Type a natural language command like "Add a todo: Buy groceries"

3. **Supported commands**:
   - "Add a todo: [title]" - Creates a new todo
   - "Mark '[todo title]' as complete" - Marks a todo as completed
   - "Delete '[todo title]'" - Deletes a todo
   - "Show my todos" - Lists all todos
   - "Update '[todo title]' to '[new title]'" - Updates a todo title

## Development

### Backend Development
- The main application logic is in `main.py`
- API endpoints are defined in the `api/` directory
- Database models are in the `models/` directory
- MCP tools are implemented in the `mcp/` directory

### Frontend Development
- The main page is in `app/page.tsx`
- Chatbot component is in `components/Chatbot/index.tsx`
- API calls are handled in `lib/api.ts`

## API Documentation
The API follows the OpenAPI specification in `contracts/chatbot-api.yaml`.
After starting the backend server, you can view the interactive API documentation at `http://localhost:8000/docs`.

## Testing
- Backend tests: `pytest tests/`
- Frontend tests: `npm run test` or `yarn test`

## Deployment
1. **Backend**: Deploy to a cloud provider that supports Python applications (AWS, GCP, Azure, or platforms like Railway, Heroku)
2. **Frontend**: Deploy to Vercel, Netlify, or similar platforms that support Next.js applications

## Troubleshooting

### Common Issues
1. **Database connection errors**: Ensure your PostgreSQL server is running and credentials are correct
2. **API key errors**: Verify your Google Gemini API key is valid and properly set in environment variables
3. **CORS errors**: Check that your frontend URL is allowed in the backend CORS settings

### Getting Help
- Check the logs in your terminal for error messages
- Verify all environment variables are set correctly
- Ensure all dependencies are installed properly