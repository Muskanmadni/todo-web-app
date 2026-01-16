---
id: "2"
title: "Update-Frontend-API-Endpoints-To-Localhost"
stage: "refactor"
date: "2026-01-07"
model: "Claude 3.5 Sonnet"
feature: "ai-chatbot-todo"
branch: "001-ai-chatbot-todo-mcp"
user: "user"
command: "/sp.implement"
labels: ["frontend", "api", "configuration", "refactor"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "todo-frontend/my-app/app/page.tsx"
  - "todo-frontend/my-app/.env.local"
  - "todo-frontend/my-app/app/api/chat/conversation/route.ts"
tests: []
---

# Prompt History Record

## User Input

```
/sp.implement  error is in my-app/page.tsx todo-frontend change url in localhost 8000 for fetch data
```

## Response

I have successfully updated all the API endpoints in the frontend to use localhost:8000 instead of the deployed URL. Here's what was accomplished:

1. Changed all hardcoded URLs in page.tsx from `https://todo-web-app-nvu7.onrender.com/` to `http://localhost:8000/`
2. Implemented environment variable configuration using NEXT_PUBLIC_API_BASE_URL to make the API base URL configurable
3. Updated the .env.local file to include the NEXT_PUBLIC_API_BASE_URL variable
4. Updated the Next.js API route for chat to also use the environment variable
5. Fixed the package.json JSON syntax error that was preventing the application from starting

The frontend now properly connects to the local backend running on port 8000, allowing for local development and testing.

## Outcome

The frontend application now connects to the local backend API instead of the deployed version, resolving the connection issues when running the application locally.