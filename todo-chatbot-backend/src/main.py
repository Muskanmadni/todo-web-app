from fastapi import FastAPI
from .config import settings
from .db.session import engine
from sqlmodel import SQLModel


def create_app():
    """
    Create and configure the FastAPI application
    """
    app = FastAPI(
        title="AI-Powered Todo Chatbot API",
        description="API for managing todos through natural language chatbot interface",
        version="1.0.0"
    )
    
    # Import and include API routes
    from .api import todo_routes, conversation_routes
    app.include_router(todo_routes.router, prefix="/api", tags=["todos"])
    app.include_router(conversation_routes.router, prefix="/api", tags=["conversations"])
    
    # Initialize database
    @app.on_event("startup")
    def on_startup():
        # Create database tables
        SQLModel.metadata.create_all(bind=engine)
    
    # Health check endpoint
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "service": "todo-chatbot-backend"}
    
    return app


app = create_app()