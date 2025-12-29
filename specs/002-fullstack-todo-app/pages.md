# Application Pages: Todo Application UI

## Authentication Pages

### Sign Up Page (`/signup`)
- Form with email, password, and confirm password fields
- Client-side validation for email format and password requirements
- Link to sign in page for existing users
- Error display for registration issues (e.g., duplicate email)
- Redirect to dashboard after successful registration

### Sign In Page (`/signin`)
- Form with email and password fields
- Link to sign up page for new users
- Link to password reset page (if implemented)
- Error display for authentication failures
- Redirect to dashboard after successful authentication

### Password Reset Page (`/reset-password`) (Optional)
- Form with email field to initiate reset
- Form with new password fields when using reset token
- Success messages for different stages of reset process
- Link back to sign in page

## Task List Page (`/tasks` or `/dashboard`)

### Main Task List View
- Header with user information and logout option
- Add new task form with title and optional description
- Filter controls (show all, show completed, show active)
- Sort options (by date created, due date, priority)
- List of tasks with:
  - Title and description
  - Completion checkbox
  - Priority indicator
  - Due date (if set)
  - Edit and delete buttons
- Empty state message when no tasks exist
- Loading state during data fetch

### Task Creation/Editing
- Inline form for creating new tasks
- Modal or inline editing for updating existing tasks
- Form validation for required fields
- Error display for API failures

## Task Create/Edit Behavior

### Create Task
- Form appears at top of task list or as modal
- Fields: title (required), description (optional), due date (optional), priority (optional)
- Validation to prevent empty titles
- Immediate addition to list after successful API call
- Error handling if creation fails

### Edit Task
- Edit form appears inline or as modal when edit button clicked
- Pre-populated with current task values
- Same fields as create but with existing values
- Save and cancel options
- Error handling if update fails

## Access Control Rules

### Unauthenticated Access
- Only sign up and sign in pages are accessible
- All other pages redirect to sign in page
- No API access without valid authentication token

### Authenticated Access
- Users can access their own task list
- Users can create, update, and delete their own tasks
- Users cannot access other users' tasks or data
- Logout functionality available from all authenticated pages

### Navigation
- Persistent navigation between authenticated views
- Clear indication of current page/section
- Easy access to user profile/logout from all authenticated pages

## Empty and Loading States

### Empty States
- Task list shows friendly message when no tasks exist
- Call-to-action to create first task
- Possibly helpful tips or onboarding information

### Loading States
- Skeleton loaders while fetching tasks
- Loading indicators during API operations
- Optimistic updates where appropriate (e.g., when marking tasks complete)
- Error states if operations fail

### Error States
- Network error messages when API calls fail
- Clear messaging for authentication failures
- Graceful degradation when individual operations fail
- Option to retry failed operations