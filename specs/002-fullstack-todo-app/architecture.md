# System Architecture: Todo App (Full-Stack Web Application)

## Overview

The Todo App Phase II follows a client-server architecture with a clear separation between the frontend and backend. The system is designed as a stateless backend service that communicates with a database and serves a Next.js frontend application.

## Frontend / Backend Separation

### Frontend (Next.js App Router)
- Built with Next.js using the App Router pattern
- Hosts the user interface and handles user interactions
- Makes API calls to the backend for data operations
- Manages client-side state and routing
- Responsive design for various device sizes

### Backend (FastAPI)
- RESTful API built with FastAPI
- Handles business logic and data validation
- Manages authentication and authorization
- Interfaces with the database via SQLModel ORM
- Stateless design for scalability

## Request Flow

1. **User Interaction**: User performs an action in the Next.js frontend
2. **API Request**: Frontend makes HTTP request to backend API endpoint
3. **Authentication Check**: Backend validates JWT token from request headers
4. **Authorization Check**: Backend verifies user permissions for requested operation
5. **Business Logic**: Backend processes request according to domain rules
6. **Database Operation**: Backend uses SQLModel to interact with Neon PostgreSQL database
7. **Response**: Backend returns JSON response to frontend
8. **UI Update**: Frontend updates UI based on response

## Stateless Backend Principles

- No server-side session storage
- All authentication state managed via JWT tokens
- Each request contains all necessary information for processing
- Backend can be scaled horizontally without shared state concerns
- API endpoints are idempotent where applicable

## Authentication Flow Using JWT

1. **Registration**: User provides credentials to registration endpoint
2. **JWT Creation**: Backend creates JWT with user identifier and claims
3. **Token Storage**: Frontend stores JWT (likely in memory or secure cookie)
4. **Request Authentication**: Frontend includes JWT in Authorization header for protected endpoints
5. **Token Validation**: Backend validates JWT signature and checks expiration
6. **User Context**: Backend extracts user information from JWT claims
7. **Token Refresh**: System handles token expiration with refresh mechanism

## Monorepo Layout

```
todo-app-monorepo/
├── backend/              # FastAPI application
│   ├── main.py          # API entry point
│   ├── models/          # SQLModel database models
│   ├── api/             # API route definitions
│   ├── auth/            # Authentication logic
│   └── config/          # Configuration files
├── frontend/            # Next.js application
│   ├── app/             # App Router pages
│   ├── components/      # Reusable UI components
│   ├── lib/             # Client utilities
│   └── public/          # Static assets
└── shared/              # Shared types, constants (optional)
```

## Technology Stack

- **Frontend**: Next.js (React) with App Router
- **Backend**: FastAPI (Python)
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel
- **Authentication**: Better Auth (JWT-based)
- **Deployment**: Vercel (Frontend) + Railway/Hetzner (Backend) or similar platforms