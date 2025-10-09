"""
Repository for casefile data persistence (Firestore only).
"""

from typing import Dict, List, Optional
import os
import logging

from pydantic_models.canonical.casefile import CasefileModel
from pydantic_models.views.casefile_views import CasefileSummary

logger = logging.getLogger(__name__)

class CasefileRepository:
    """Repository for casefile data persistence (Firestore only)."""
    
    def __init__(self):
        """Initialize the repository."""
        self.mode = os.environ.get("CASEFILE_REPOSITORY_MODE", "firestore").lower()
        self._store: Dict[str, CasefileModel] = {}

        if self.mode == "memory":
            logger.info("CasefileRepository running in in-memory mode")
            return

        try:
            self._init_firestore()
        except ModuleNotFoundError as exc:
            logger.warning(
                "Firebase Admin SDK not available (%s); falling back to in-memory repository",
                exc,
            )
            self.mode = "memory"
        except Exception as exc:  # pragma: no cover - defensive logging for environments without Firestore
            logger.warning(
                "Failed to initialize Firestore repository (%s); falling back to in-memory repository",
                exc,
            )
            self.mode = "memory"

        if self.mode == "memory":
            logger.info("CasefileRepository initialized with in-memory backend after Firestore failure")
    
    def _init_firestore(self):
        """Initialize Firestore client."""
        import firebase_admin
        from firebase_admin import firestore
        
        logger.info("Initializing Firestore for CasefileRepository")
        
        # Initialize Firebase app if not already initialized
        try:
            self.app = firebase_admin.get_app()
            logger.info("Using existing Firebase app")
        except ValueError:
            # Use application default credentials
            cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            if cred_path:
                logger.info(f"Initializing Firebase app with credentials from {cred_path}")
            else:
                logger.warning("No GOOGLE_APPLICATION_CREDENTIALS found, using default credentials")
            
            self.app = firebase_admin.initialize_app()
        
        # Get database name from environment
        database_id = os.environ.get("FIRESTORE_DATABASE", "mds-objects")
        logger.info(f"Using Firestore database: {database_id}")
        
        # Initialize Firestore client with specific database
        if database_id and database_id != "(default)":
            self.db = firestore.client(database_id=database_id)
            logger.info(f"Connected to Firestore database: {database_id}")
        else:
            self.db = firestore.client()
            logger.info("Connected to default Firestore database")
        
        # Define collections
        self.casefiles_collection = self.db.collection("casefiles")
        
        logger.info("Firestore initialized successfully for casefiles")
    
    async def create_casefile(self, casefile: CasefileModel) -> str:
        """Create a new casefile.
        
        Args:
            casefile: The casefile to create
            
        Returns:
            ID of the created casefile
        """
        if self.mode == "memory":
            stored = casefile.model_copy(deep=True)
            self._store[stored.id] = stored
            return stored.id

        casefile_id = casefile.id  # Now it's already a string

        # Convert to dict for Firestore
        casefile_dict = casefile.model_dump(exclude_none=True)
        casefile_dict["session_ids"] = list(casefile.session_ids)

        self.casefiles_collection.document(casefile_id).set(casefile_dict)
        
        return casefile_id
    
    async def get_casefile(self, casefile_id: str) -> Optional[CasefileModel]:
        """Get a casefile by ID.
        
        Args:
            casefile_id: ID of the casefile to retrieve
            
        Returns:
            The casefile, or None if not found
        """
        if self.mode == "memory":
            if casefile_id not in self._store:
                return None
            return self._store[casefile_id].model_copy(deep=True)

        doc = self.casefiles_collection.document(casefile_id).get()
        if doc.exists:
            # Convert back to CasefileModel
            casefile_data = doc.to_dict()
            if "sessions" in casefile_data and "session_ids" not in casefile_data:
                casefile_data["session_ids"] = casefile_data.pop("sessions")
            casefile_data.setdefault("session_ids", [])

            return CasefileModel.model_validate(casefile_data)
        return None
    
    async def update_casefile(self, casefile: CasefileModel) -> None:
        """Update a casefile.
        
        Args:
            casefile: The casefile to update
        """
        if self.mode == "memory":
            self._store[casefile.id] = casefile.model_copy(deep=True)
            return

        # Convert to dict for Firestore
        casefile_dict = casefile.model_dump(exclude_none=True)
        casefile_dict["session_ids"] = list(casefile.session_ids)

        self.casefiles_collection.document(casefile.id).set(casefile_dict)
    
    async def list_casefiles(self, user_id: Optional[str] = None) -> List[CasefileSummary]:
        """List casefiles, optionally filtered by user.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of casefile summaries
        """
        if self.mode == "memory":
            summaries: List[CasefileSummary] = []
            for stored in self._store.values():
                if user_id and stored.metadata.created_by != user_id:
                    continue
                summaries.append(
                    CasefileSummary(
                        casefile_id=stored.id,
                        title=stored.metadata.title,
                        description=stored.metadata.description,
                        tags=stored.metadata.tags,
                        created_at=stored.metadata.created_at,
                        resource_count=stored.resource_count,
                        session_count=len(stored.session_ids),
                    )
                )
            return summaries

        # Build query
        query = self.casefiles_collection
        if user_id:
            query = query.where("metadata.created_by", "==", user_id)
            
        # Execute query
        docs = query.get()
        
        # Convert to summaries
        results = []
        for doc in docs:
            data = doc.to_dict()

            # Convert sessions back to UUIDs for model validation
            if "sessions" in data and "session_ids" not in data:
                data["session_ids"] = data.pop("sessions")
            data.setdefault("session_ids", [])

            casefile = CasefileModel.model_validate(data)
            
            results.append(
                CasefileSummary(
                    casefile_id=casefile.id,
                    title=casefile.metadata.title,
                    description=casefile.metadata.description,
                    tags=casefile.metadata.tags,
                    created_at=casefile.metadata.created_at,
                    resource_count=casefile.resource_count,
                    session_count=len(casefile.session_ids)
                )
            )
            
        return results
    
    async def delete_casefile(self, casefile_id: str) -> bool:
        """Delete a casefile.
        
        Args:
            casefile_id: ID of the casefile to delete
            
        Returns:
            Whether deletion was successful
        """
        if self.mode == "memory":
            return self._store.pop(casefile_id, None) is not None

        try:
            self.casefiles_collection.document(casefile_id).delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting casefile {casefile_id}: {e}")
            return False