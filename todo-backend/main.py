from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum
import uuid
from sqlmodel import SQLModel, Field, create_engine, Session, select
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from contextlib import contextmanager
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware
from api.chatbot import router as chatbot_router
from api.recurring_tasks import router as recurring_tasks_router
from api.reminders import router as reminders_router
from events.consumer import EventConsumer

# Import models from models directory
from models.user import User as UserModel
from models.todo import Todo as TodoModel
from models.conversation import Conversation as ConversationModel
from models.message import Message as MessageModel

# Load environment variables
load_dotenv()

# Configuration
# Use SQLite for development if no DATABASE_URL is provided, otherwise use PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_chatbot_dev.db")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
import bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = HTTPBearer()
security = HTTPBearer()

# Initialize FastAPI app
app = FastAPI(title="Todo App API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
from database import engine, get_session  # Import engine from centralized database module

# Models
class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)


class UserCreate(UserBase):
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    created_at: datetime

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = False
    due_date: Optional[datetime] = None
    priority: PriorityEnum = PriorityEnum.medium

class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    priority: Optional[PriorityEnum] = None

class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    completed: bool
    due_date: Optional[datetime] = None
    priority: PriorityEnum
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Use bcrypt directly to avoid passlib backend issues
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    # Truncate password to 72 bytes if necessary to avoid bcrypt error
    truncated_password = password[:72] if len(password) > 72 else password
    # Use bcrypt directly to avoid passlib backend issues
    return bcrypt.hashpw(truncated_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # Ensure the data values are properly serializable
    for key, value in to_encode.items():
        if isinstance(value, uuid.UUID):
            to_encode[key] = str(value)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        # Convert user_id to UUID to match the database field type
        user_id_uuid = uuid.UUID(user_id)
    except (JWTError, ValueError):
        raise credentials_exception

    with Session(engine) as session:
        user = session.exec(select(UserModel).where(UserModel.id == user_id_uuid)).first()
        if user is None:
            raise credentials_exception
        return user

def authenticate_user(email: str, password: str) -> Optional[UserModel]:
    with Session(engine) as session:
        user = session.exec(select(UserModel).where(UserModel.email == email)).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

# Create tables
@app.on_event("startup")
def on_startup():
    # Import here to avoid circular imports
    from database import engine
    from sqlmodel import SQLModel
    from sqlalchemy import text
    import time

    # Attempt to run alembic migrations to update the schema
    # If that fails, try direct schema updates for missing columns
    try:
        import subprocess
        import sys
        import os
        original_cwd = os.getcwd()
        os.chdir('/app')  # Change to app directory where alembic.ini is located

        # Run alembic upgrade to head to apply all pending migrations
        result = subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Alembic migration failed: {result.stderr}")
            print("Attempting direct schema updates...")

            # Direct schema update for missing columns
            with engine.connect() as conn:
                # Check and add missing columns to users table
                # Check if timezone column exists in users table
                tz_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'users' AND column_name = 'timezone'
                """)).fetchone()

                if not tz_result:
                    # Add timezone column with default value
                    conn.execute(text("ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC'"))
                    print("Added timezone column to users table")

                # Check if reminder_preferences column exists in users table
                rp_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'users' AND column_name = 'reminder_preferences'
                """)).fetchone()

                if not rp_result:
                    # Add reminder_preferences column
                    conn.execute(text("ALTER TABLE users ADD COLUMN reminder_preferences JSON"))
                    print("Added reminder_preferences column to users table")

                # Check and add missing columns to todos table
                # Check if priority column exists in todos table
                priority_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'todos' AND column_name = 'priority'
                """)).fetchone()

                if not priority_result:
                    # Add priority column with default value
                    conn.execute(text("ALTER TABLE todos ADD COLUMN priority VARCHAR(20) DEFAULT 'medium'"))
                    print("Added priority column to todos table")

                # Check if tags column exists in todos table
                tags_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'todos' AND column_name = 'tags'
                """)).fetchone()

                if not tags_result:
                    # Add tags column
                    conn.execute(text("ALTER TABLE todos ADD COLUMN tags JSON"))
                    print("Added tags column to todos table")

                # Check if due_date column exists in todos table
                due_date_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'todos' AND column_name = 'due_date'
                """)).fetchone()

                if not due_date_result:
                    # Add due_date column
                    conn.execute(text("ALTER TABLE todos ADD COLUMN due_date TIMESTAMP"))
                    print("Added due_date column to todos table")

                # Check if recurrence_pattern column exists in todos table
                recurrence_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'todos' AND column_name = 'recurrence_pattern'
                """)).fetchone()

                if not recurrence_result:
                    # Add recurrence_pattern column
                    conn.execute(text("ALTER TABLE todos ADD COLUMN recurrence_pattern TEXT"))
                    print("Added recurrence_pattern column to todos table")

                # Check if next_occurrence_date column exists in todos table
                next_occurrence_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'todos' AND column_name = 'next_occurrence_date'
                """)).fetchone()

                if not next_occurrence_result:
                    # Add next_occurrence_date column
                    conn.execute(text("ALTER TABLE todos ADD COLUMN next_occurrence_date TIMESTAMP"))
                    print("Added next_occurrence_date column to todos table")

                conn.commit()
        else:
            print("Alembic migrations applied successfully")
    except FileNotFoundError:
        print("Alembic not found, skipping migrations. Proceeding with direct schema updates...")
        # If alembic is not available, proceed with direct schema updates
        try:
            with engine.connect() as conn:
                # Check and add missing columns to users table
                # Check if timezone column exists in users table
                tz_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'users' AND column_name = 'timezone'
                """)).fetchone()

                if not tz_result:
                    # Add timezone column with default value
                    conn.execute(text("ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC'"))
                    print("Added timezone column to users table")

                # Check if reminder_preferences column exists in users table
                rp_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'users' AND column_name = 'reminder_preferences'
                """)).fetchone()

                if not rp_result:
                    # Add reminder_preferences column
                    conn.execute(text("ALTER TABLE users ADD COLUMN reminder_preferences JSON"))
                    print("Added reminder_preferences column to users table")

                # Check and add missing columns to todos table
                # Check if priority column exists in todos table
                priority_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'todos' AND column_name = 'priority'
                """)).fetchone()

                if not priority_result:
                    # Add priority column with default value
                    conn.execute(text("ALTER TABLE todos ADD COLUMN priority VARCHAR(20) DEFAULT 'medium'"))
                    print("Added priority column to todos table")

                # Check if tags column exists in todos table
                tags_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'todos' AND column_name = 'tags'
                """)).fetchone()

                if not tags_result:
                    # Add tags column
                    conn.execute(text("ALTER TABLE todos ADD COLUMN tags JSON"))
                    print("Added tags column to todos table")

                # Check if due_date column exists in todos table
                due_date_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'todos' AND column_name = 'due_date'
                """)).fetchone()

                if not due_date_result:
                    # Add due_date column
                    conn.execute(text("ALTER TABLE todos ADD COLUMN due_date TIMESTAMP"))
                    print("Added due_date column to todos table")

                # Check if recurrence_pattern column exists in todos table
                recurrence_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'todos' AND column_name = 'recurrence_pattern'
                """)).fetchone()

                if not recurrence_result:
                    # Add recurrence_pattern column
                    conn.execute(text("ALTER TABLE todos ADD COLUMN recurrence_pattern TEXT"))
                    print("Added recurrence_pattern column to todos table")

                # Check if next_occurrence_date column exists in todos table
                next_occurrence_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'todos' AND column_name = 'next_occurrence_date'
                """)).fetchone()

                if not next_occurrence_result:
                    # Add next_occurrence_date column
                    conn.execute(text("ALTER TABLE todos ADD COLUMN next_occurrence_date TIMESTAMP"))
                    print("Added next_occurrence_date column to todos table")

                conn.commit()
        except Exception as e2:
            print(f"Direct schema update failed: {e2}")
    except Exception as e:
        print(f"Error running alembic migrations: {e}")
        # Fallback: try direct schema updates
        try:
            with engine.connect() as conn:
                # Check and add missing columns to users table
                # Check if timezone column exists in users table
                tz_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'users' AND column_name = 'timezone'
                """)).fetchone()

                if not tz_result:
                    # Add timezone column with default value
                    conn.execute(text("ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC'"))
                    print("Added timezone column to users table")

                # Check if reminder_preferences column exists in users table
                rp_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'users' AND column_name = 'reminder_preferences'
                """)).fetchone()

                if not rp_result:
                    # Add reminder_preferences column
                    conn.execute(text("ALTER TABLE users ADD COLUMN reminder_preferences JSON"))
                    print("Added reminder_preferences column to users table")

                # Check and add missing columns to todos table
                # Check if priority column exists in todos table
                priority_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'todos' AND column_name = 'priority'
                """)).fetchone()

                if not priority_result:
                    # Add priority column with default value
                    conn.execute(text("ALTER TABLE todos ADD COLUMN priority VARCHAR(20) DEFAULT 'medium'"))
                    print("Added priority column to todos table")

                # Check if tags column exists in todos table
                tags_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'todos' AND column_name = 'tags'
                """)).fetchone()

                if not tags_result:
                    # Add tags column
                    conn.execute(text("ALTER TABLE todos ADD COLUMN tags JSON"))
                    print("Added tags column to todos table")

                # Check if due_date column exists in todos table
                due_date_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'todos' AND column_name = 'due_date'
                """)).fetchone()

                if not due_date_result:
                    # Add due_date column
                    conn.execute(text("ALTER TABLE todos ADD COLUMN due_date TIMESTAMP"))
                    print("Added due_date column to todos table")

                # Check if recurrence_pattern column exists in todos table
                recurrence_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'todos' AND column_name = 'recurrence_pattern'
                """)).fetchone()

                if not recurrence_result:
                    # Add recurrence_pattern column
                    conn.execute(text("ALTER TABLE todos ADD COLUMN recurrence_pattern TEXT"))
                    print("Added recurrence_pattern column to todos table")

                # Check if next_occurrence_date column exists in todos table
                next_occurrence_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'todos' AND column_name = 'next_occurrence_date'
                """)).fetchone()

                if not next_occurrence_result:
                    # Add next_occurrence_date column
                    conn.execute(text("ALTER TABLE todos ADD COLUMN next_occurrence_date TIMESTAMP"))
                    print("Added next_occurrence_date column to todos table")

                conn.commit()
        except Exception as e2:
            print(f"Fallback schema update also failed: {e2}")
    finally:
        os.chdir(original_cwd)  # Restore original working directory

    # Create all tables (this won't hurt and ensures any remaining tables are created)
    SQLModel.metadata.create_all(bind=engine)

    # Give a little time for schema changes to propagate
    time.sleep(1)

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    with Session(engine) as session:
        # Check if user already exists
        existing_user = session.exec(select(UserModel).where(UserModel.email == user.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = UserModel(email=user.email, password_hash=hashed_password)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

@app.post("/auth/login", response_model=Token)
def login(user_credentials: UserLogin):
    user = authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Task endpoints
@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(current_user: UserModel = Depends(get_current_user)):
    with Session(engine) as session:
        tasks = session.exec(
            select(TodoModel).where(TodoModel.user_id == current_user.id)
        ).all()
        # Convert TodoModel instances to match TaskResponse format
        task_responses = []
        for todo in tasks:
            task_response = TaskResponse(
                id=todo.id,
                title=todo.title,
                description=todo.description,
                completed=todo.status == "completed",
                due_date=todo.completed_at,
                priority=PriorityEnum.medium,  # Default priority
                user_id=todo.user_id,
                created_at=todo.created_at,
                updated_at=todo.created_at  # Using created_at as updated_at for now
            )
            task_responses.append(task_response)
        return task_responses

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, current_user: UserModel = Depends(get_current_user)):
    with Session(engine) as session:
        db_task = TodoModel(
            title=task.title,
            description=task.description,
            user_id=current_user.id,
            status="pending"  # Default status
        )
        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        # Convert to TaskResponse format
        task_response = TaskResponse(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            completed=db_task.status == "completed",
            due_date=db_task.completed_at,
            priority=PriorityEnum.medium,  # Default priority
            user_id=db_task.user_id,
            created_at=db_task.created_at,
            updated_at=db_task.created_at  # Using created_at as updated_at for now
        )
        return task_response

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: uuid.UUID, current_user: UserModel = Depends(get_current_user)):
    with Session(engine) as session:
        todo = session.exec(
            select(TodoModel).where(TodoModel.id == task_id, TodoModel.user_id == current_user.id)
        ).first()
        if not todo:
            raise HTTPException(status_code=404, detail="Task not found")

        # Convert to TaskResponse format
        task_response = TaskResponse(
            id=todo.id,
            title=todo.title,
            description=todo.description,
            completed=todo.status == "completed",
            due_date=todo.completed_at,
            priority=PriorityEnum.medium,  # Default priority
            user_id=todo.user_id,
            created_at=todo.created_at,
            updated_at=todo.created_at  # Using created_at as updated_at for now
        )
        return task_response

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: uuid.UUID, task_update: TaskUpdate, current_user: UserModel = Depends(get_current_user)):
    with Session(engine) as session:
        db_todo = session.exec(
            select(TodoModel).where(TodoModel.id == task_id, TodoModel.user_id == current_user.id)
        ).first()

        if not db_todo:
            raise HTTPException(status_code=404, detail="Task not found")

        # Update only provided fields
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "completed":
                # Map completed flag to status
                db_todo.status = "completed" if value else "pending"
            elif hasattr(db_todo, field):
                setattr(db_todo, field, value)

        session.add(db_todo)
        session.commit()
        session.refresh(db_todo)

        # Convert to TaskResponse format
        task_response = TaskResponse(
            id=db_todo.id,
            title=db_todo.title,
            description=db_todo.description,
            completed=db_todo.status == "completed",
            due_date=db_todo.completed_at,
            priority=PriorityEnum.medium,  # Default priority
            user_id=db_todo.user_id,
            created_at=db_todo.created_at,
            updated_at=db_todo.created_at  # Using created_at as updated_at for now
        )
        return task_response

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: uuid.UUID, current_user: UserModel = Depends(get_current_user)):
    with Session(engine) as session:
        todo = session.exec(
            select(TodoModel).where(TodoModel.id == task_id, TodoModel.user_id == current_user.id)
        ).first()

        if not todo:
            raise HTTPException(status_code=404, detail="Task not found")

        session.delete(todo)
        session.commit()
        return

# Include chatbot router
app.include_router(chatbot_router, prefix="", tags=["chat"])

# Include recurring tasks router
app.include_router(recurring_tasks_router, prefix="", tags=["recurring-tasks"])

# Include reminders router
app.include_router(reminders_router, prefix="", tags=["reminders"])

# Dapr subscription endpoint for pub/sub
@app.post("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr subscription endpoint to define which topics this service wants to subscribe to.
    """
    subscriptions = [
        {
            "pubsubname": "todo-pubsub",  # This should match the pubsub component name
            "topic": "task-events",
            "route": "/events/task"
        },
        {
            "pubsubname": "todo-pubsub",
            "topic": "reminders",
            "route": "/events/reminders"
        },
        {
            "pubsubname": "todo-pubsub",
            "topic": "recurring-tasks",
            "route": "/events/recurring-tasks"
        }
    ]
    return subscriptions

# Endpoint to handle incoming events from Dapr pub/sub
@app.post("/events/{topic}")
async def handle_topic_event(topic: str, request: Request):
    """
    Handle events from Dapr pub/sub for different topics.
    """
    return await EventConsumer.handle_dapr_subscription(request)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
