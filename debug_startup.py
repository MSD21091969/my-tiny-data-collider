"""
Debug startup script.
"""

import logging
from src.pydantic_api import app

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("Starting app debug...")

try:
    logger.info("App created successfully")
    logger.info(f"App routes: {[route.path for route in app.routes]}")
    
    # Test our auth imports
    from src.authservice.token import create_token
    token = create_token("sam123", "Sam")
    logger.info(f"Token generated successfully: {token[:20]}...")
    
    logger.info("All imports and token generation successful")
except Exception as e:
    logger.error(f"Error during startup: {str(e)}", exc_info=True)