"""
Firestore client initialization.
"""

import logging
import os

from google.cloud import firestore

logger = logging.getLogger(__name__)

_FIRESTORE_CLIENT = None
DEFAULT_DATABASE = "mds-objects"


def get_firestore_client() -> firestore.Client:
    """Get a Firestore client instance (singleton).

    Returns:
        Firestore client
    """
    global _FIRESTORE_CLIENT

    if _FIRESTORE_CLIENT is None:
        try:
            # Check for project ID in environment
            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
            database_id = os.environ.get("FIRESTORE_DATABASE", DEFAULT_DATABASE)

            # Log database selection
            if database_id and database_id != "default":
                logger.info(f"Using Firestore database: {database_id}")

            if project_id:
                _FIRESTORE_CLIENT = firestore.Client(project=project_id, database=database_id)
                logger.info(f"Initialized Firestore client for project {project_id}")
            else:
                # Use default credentials and project
                _FIRESTORE_CLIENT = firestore.Client(database=database_id)
                logger.info("Initialized Firestore client with default credentials")

        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            raise

    return _FIRESTORE_CLIENT
