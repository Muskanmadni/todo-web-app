from sqlmodel import create_engine, Session, SQLModel
from pydantic_settings import BaseSettings
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./todo_chatbot_dev.db")
    secret_key: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    better_auth_secret: str = os.getenv("BETTER_AUTH_SECRET", "your-better-auth-secret")
    dapr_sidecar_port: int = int(os.getenv("DAPR_SIDECAR_PORT", "3500"))


settings = Settings()

# Use connect_args for PostgreSQL compatibility
connect_args = {}
if settings.database_url.startswith("postgresql"):
    connect_args = {
        "connect_timeout": 10,
    }
elif settings.database_url.startswith("sqlite"):
    # For SQLite, use check_same_thread for compatibility with FastAPI
    connect_args = {"check_same_thread": False}

# Create engine with connection pooling settings for Neon (only for PostgreSQL)
if settings.database_url.startswith("postgresql"):
    engine = create_engine(
        settings.database_url,
        # Add connection pooling settings appropriate for Neon Serverless
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        echo=False,          # Set to True for debugging
        connect_args=connect_args
    )
else:
    # For SQLite, use simpler configuration
    engine = create_engine(settings.database_url, connect_args=connect_args, echo=True)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """
    Creates all database tables based on the SQLModel models.
    This should be called when the application starts.
    """
    # For SQLite, we can use create_all which works fine for simple schema updates
    if settings.database_url.startswith("sqlite"):
        SQLModel.metadata.create_all(engine)
    else:
        # For PostgreSQL, we need to be more careful about schema updates
        # In a real application, you'd use Alembic for proper migrations
        # For now, we'll try to create missing tables and warn about schema mismatches
        from sqlmodel import create_engine as sqlmodel_create_engine
        from sqlalchemy import inspect

        # Check if tables exist and create them if they don't
        SQLModel.metadata.create_all(engine)

        # For a more robust solution, we'd use Alembic migrations
        # But for this demo, we'll just ensure the basic tables exist


# Initialize the database and tables when this module is imported
def init_db():
    create_db_and_tables()