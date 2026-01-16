from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum
import uuid
from sqlmodel import SQLModel, Field, create_engine, Session, select
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from contextlib import contextmanager
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware
from api.chatbot import router as chatbot_router

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
    SQLModel.metadata.create_all(bind=engine)

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

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
