from sqlmodel import create_engine
from .config import settings


# Create the database engine
engine = create_engine(
    settings.database_url,
    echo=True,  # Set to False in production
    connect_args={"check_same_thread": False}  # Needed for SQLite
)


def get_session():
    """
    Get a database session
    """
    from sqlmodel import Session
    with Session(engine) as session:
        yield session