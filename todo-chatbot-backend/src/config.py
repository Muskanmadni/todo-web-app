from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    database_url: str = "sqlite:///./todo_chatbot.db"
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    openai_api_key: Optional[str] = None
    mcp_server_key: str = "your-mcp-server-key-change-in-production"
    
    class Config:
        env_file = ".env"


settings = Settings()