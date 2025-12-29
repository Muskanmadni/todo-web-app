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

# Load environment variables
load_dotenv()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_ywfK5ROea2kh@ep-hidden-paper-adebc1e9-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
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
# Use connect_args for PostgreSQL compatibility
connect_args = {}
if DATABASE_URL.startswith("postgresql"):
    connect_args = {"connect_timeout": 10}

engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

# Models
class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)

class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> User:
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
        user = session.exec(select(User).where(User.id == user_id_uuid)).first()
        if user is None:
            raise credentials_exception
        return user

def authenticate_user(email: str, password: str) -> Optional[User]:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
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
        existing_user = session.exec(select(User).where(User.email == user.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(email=user.email, password_hash=hashed_password)
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
def get_tasks(current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        tasks = session.exec(
            select(Task).where(Task.user_id == current_user.id)
        ).all()
        return tasks

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        db_task = Task(
            **task.dict(),
            user_id=current_user.id
        )
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: uuid.UUID, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        ).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: uuid.UUID, task_update: TaskUpdate, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        db_task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        ).first()

        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Update only provided fields
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)

        db_task.updated_at = datetime.utcnow()
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: uuid.UUID, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        session.delete(task)
        session.commit()
        return

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
