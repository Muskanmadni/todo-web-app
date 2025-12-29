# Quickstart Guide: Full-Stack Todo App

## Prerequisites

- Node.js 18+ (for Next.js frontend)
- Python 3.11+ (for FastAPI backend)
- PostgreSQL (or Neon Serverless PostgreSQL account)
- Git

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Backend Setup (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
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
   # Or if using pyproject.toml:
   pip install poetry
   poetry install
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and other settings
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```

### 3. Frontend Setup (Next.js)

1. Navigate to the frontend directory:
   ```bash
   cd ../todo-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your backend API URL and other settings
   ```

4. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

## API Endpoints

The backend API will be available at `http://localhost:8000` by default.

- Authentication: `/auth/register`, `/auth/login`, `/auth/logout`
- Tasks: `/tasks` (GET, POST), `/tasks/{id}` (GET, PUT, DELETE)

## Database Setup

1. Create a Neon Serverless PostgreSQL database or set up a local PostgreSQL instance
2. Update your backend `.env` file with the database connection string:
   ```
   DATABASE_URL=postgresql://username:password@host:port/database_name
   ```
3. Run the database migrations as described in the backend setup

## Running Tests

### Backend Tests
```bash
cd backend
# With virtual environment activated
pytest
```

### Frontend Tests
```bash
cd todo-frontend
npm run test
# or
yarn test
```

## Environment Variables

### Backend (.env)
- `DATABASE_URL`: Connection string for PostgreSQL database
- `SECRET_KEY`: Secret key for JWT token signing
- `ALGORITHM`: Algorithm for JWT encoding (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL`: URL of the backend API (e.g., http://localhost:8000)

## Development Workflow

1. Make changes to the specification in `/specs/002-fullstack-todo-app/spec.md`
2. Generate implementation from the spec using Claude Code
3. Run tests to ensure functionality works as expected
4. Commit changes with descriptive commit messages

## Troubleshooting

- If you get database connection errors, verify your PostgreSQL server is running and credentials are correct
- If the frontend can't connect to the backend, check that both servers are running and the API URL is correctly configured
- For authentication issues, ensure JWT settings match between frontend and backend