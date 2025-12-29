# Data Model: Full-Stack Todo App

## Overview
This document defines the data models for the full-stack todo application with user authentication and task management.

## Entity: User

### Fields
- `id`: UUID (Primary Key, auto-generated)
- `email`: String (Required, Unique, Valid email format)
- `password_hash`: String (Required, hashed password)
- `created_at`: DateTime (Auto-generated timestamp)
- `updated_at`: DateTime (Auto-generated timestamp, updated on change)

### Relationships
- One-to-Many: User has many Tasks

### Validation Rules
- Email must be a valid email format
- Email must be unique across all users
- Password must meet strength requirements (min 8 characters)
- Created_at and updated_at are automatically managed

## Entity: Task

### Fields
- `id`: UUID (Primary Key, auto-generated)
- `title`: String (Required, max 200 characters)
- `description`: Text (Optional, max 1000 characters)
- `completed`: Boolean (Default: false)
- `due_date`: DateTime (Optional)
- `priority`: String (Enum: 'low', 'medium', 'high'; Default: 'medium')
- `user_id`: UUID (Foreign Key, references User.id)
- `created_at`: DateTime (Auto-generated timestamp)
- `updated_at`: DateTime (Auto-generated timestamp, updated on change)

### Relationships
- Many-to-One: Task belongs to one User

### Validation Rules
- Title is required and must be between 1-200 characters
- Description is optional, max 1000 characters if provided
- Completed defaults to false
- Priority must be one of 'low', 'medium', 'high'
- Due date must be a valid future date if provided
- User_id must reference an existing user
- Created_at and updated_at are automatically managed

## State Transitions

### Task State Transitions
- `incomplete` → `completed` (when user marks task as done)
- `completed` → `incomplete` (when user unmarks task as done)

### Business Rules
- Users can only view, create, update, and delete their own tasks
- Tasks cannot be created without an associated user
- Tasks must have a title
- Tasks are created in 'incomplete' state by default