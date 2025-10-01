"""
Main application entry point.
"""

import uvicorn
import os
import sys
import logging

# Add parent directory to path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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
    logger.info(f"Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    logger.info(f"Swagger UI will be available at: http://localhost:{port}/docs")
    
    # Run the server
    try:
        uvicorn.run(
            "src.pydantic_api:app",
            host="0.0.0.0",
            port=port,
            reload=os.environ.get("ENVIRONMENT", "development") == "development"
        )
    except OSError as e:
        if "address already in use" in str(e).lower() or "10013" in str(e):
            logger.error(f"Port {port} is already in use!")
            logger.info(f"Try: Stop the other process or set a different PORT in .env")
            logger.info(f"Example: export PORT=8001  (or add PORT=8001 to .env file)")
        raise

if __name__ == "__main__":
    main()
