# REST API Behavior: Todo Application

## Endpoint List

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

### Task Management Endpoints
- `GET /api/tasks` - Get all tasks for authenticated user
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{task_id}` - Get a specific task
- `PUT /api/tasks/{task_id}` - Update a specific task
- `DELETE /api/tasks/{task_id}` - Delete a specific task

## HTTP Methods

### GET
- Used for retrieving resources
- Should be idempotent and safe (no side effects)
- Returns requested data in JSON format
- Uses query parameters for filtering, pagination

### POST
- Used for creating new resources
- Contains request body with resource data
- Returns created resource with assigned ID
- May return validation errors if request is invalid

### PUT
- Used for updating existing resources
- Contains complete resource representation in request body
- Returns updated resource
- May return validation errors if request is invalid

### DELETE
- Used for deleting resources
- Returns success confirmation or error
- Idempotent operation (calling multiple times should have same effect)

## Request/Response Semantics

### Request Format
- Content-Type: application/json for POST/PUT requests
- Authentication via Bearer token in Authorization header
- URL parameters for resource identification
- Query parameters for filtering and pagination

### Response Format
- Content-Type: application/json
- Success responses include relevant data
- Error responses follow consistent format
- HTTP status codes indicate operation result

## Authentication Requirements

### Public Endpoints (No Authentication Required)
- `POST /api/auth/register`
- `POST /api/auth/login`

### Protected Endpoints (Authentication Required)
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/tasks`
- `POST /api/tasks`
- `GET /api/tasks/{task_id}`
- `PUT /api/tasks/{task_id}`
- `DELETE /api/tasks/{task_id}`

## Error Response Standards

### Standard Error Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Optional additional details"
  }
}
```

### Common HTTP Status Codes
- `200 OK`: Successful GET, PUT, DELETE requests
- `201 Created`: Successful POST request with resource creation
- `400 Bad Request`: Invalid request format or validation errors
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Valid authentication but insufficient permissions
- `404 Not Found`: Requested resource does not exist
- `500 Internal Server Error`: Server-side error

### Specific Error Codes
- `VALIDATION_ERROR`: Request data failed validation
- `AUTHENTICATION_ERROR`: Authentication token is invalid or expired
- `AUTHORIZATION_ERROR`: User lacks permission for requested action
- `RESOURCE_NOT_FOUND`: Requested resource does not exist
- `DUPLICATE_RESOURCE`: Attempt to create resource that already exists

## User Isolation Rules

### Data Access
- Users can only access their own tasks
- API filters all queries by authenticated user ID
- Attempting to access another user's data returns 403 Forbidden
- No direct way to access tasks belonging to other users

### Ownership
- All created tasks are automatically assigned to authenticated user
- Task ownership cannot be transferred to another user
- Users cannot modify ownership properties of tasks
- User ID is automatically set from JWT claims, not request body

### Cross-User Security
- Backend validation prevents user ID manipulation in requests
- All endpoints verify that requested resources belong to authenticated user
- No endpoints expose other users' data or allow cross-user operations