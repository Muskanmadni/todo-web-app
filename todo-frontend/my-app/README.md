# Todo App Frontend

This is the frontend for the full-stack todo application built with Next.js 14+.

## Features

- User registration and login
- Create, read, update, and delete tasks
- Task priority levels (low, medium, high)
- Responsive design for all screen sizes
- JWT-based authentication

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your backend API URL and other settings
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:3000`.

## Environment Variables

- `NEXT_PUBLIC_API_URL`: URL of the backend API (e.g., http://localhost:8000)