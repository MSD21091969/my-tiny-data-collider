"""
Main application entry point.
"""

import uvicorn
import os
import logging

from dotenv import load_dotenv
from src.pydantic_api import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

def main():
    """Run the application."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    # Log startup
    logger.info(f"Starting MDS Objects API on port {port}")
    
    # Run the server
    uvicorn.run(
        "src.pydantic_api:app",
        host="0.0.0.0",
        port=port,
        reload=os.environ.get("ENVIRONMENT", "development") == "development"
    )

if __name__ == "__main__":
    main()
