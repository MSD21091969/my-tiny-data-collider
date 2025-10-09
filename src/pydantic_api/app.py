"""
Main FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from .routers import tool_session, casefile
from coreservice.config import get_environment
from authservice.routes import router as auth_router

# Import the chat router conditionally to handle potential missing module
try:
    from .routers import chat
    has_chat_router = True
except ImportError:
    has_chat_router = False

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="MDS Objects API",
        description="Data-centric AI Tooling Framework with Pydantic Integration",
        version="0.1.0",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add routers
    app.include_router(tool_session.router)
    app.include_router(casefile.router)
    app.include_router(auth_router)
    
    # Add chat router if available
    if has_chat_router:
        app.include_router(chat.router)
    
    # Add health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> Dict[str, Any]:
        return {
            "status": "ok",
            "version": "0.1.0",
            "environment": get_environment()
        }
    
    return app

# Main application instance
app = create_app()