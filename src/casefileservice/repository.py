"""
Repository for casefile data persistence.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import logging

from ..pydantic_models.casefile.models import CasefileModel, CasefileSummary

logger = logging.getLogger(__name__)

class CasefileRepository:
    """Repository for casefile data persistence."""
    
    def __init__(self, use_mocks: bool = False):
        """Initialize the repository.
        
        Args:
            use_mocks: Whether to use mock implementations
        """
        self.use_mocks = use_mocks
        if use_mocks:
            self._init_mock_storage()
        else:
            self._init_firestore()
    
    def _init_mock_storage(self):
        """Initialize mock storage."""
        self.casefiles = {}  # In-memory storage for casefiles
    
    def _init_firestore(self):
        """Initialize Firestore client."""
        try:
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
            
        except ImportError as e:
            # Fallback to mock if firebase-admin is not installed
            logger.warning(f"firebase-admin package not found ({str(e)}), falling back to mock storage")
            self.use_mocks = True
            self._init_mock_storage()
        except Exception as e:
            # Fallback to mock for any initialization error
            logger.error(f"Error initializing Firestore: {str(e)}")
            import traceback
            traceback.print_exc()
            self.use_mocks = True
            self._init_mock_storage()
    
    async def create_casefile(self, casefile: CasefileModel) -> str:
        """Create a new casefile.
        
        Args:
            casefile: The casefile to create
            
        Returns:
            ID of the created casefile
        """
        casefile_id = casefile.id  # Now it's already a string
        
        if self.use_mocks:
            self.casefiles[casefile_id] = casefile
        else:
            # Convert to dict for Firestore
            casefile_dict = casefile.model_dump()
            casefile_dict["sessions"] = list(casefile.sessions)

            self.casefiles_collection.document(casefile_id).set(casefile_dict)
        
        return casefile_id
    
    async def get_casefile(self, casefile_id: str) -> Optional[CasefileModel]:
        """Get a casefile by ID.
        
        Args:
            casefile_id: ID of the casefile to retrieve
            
        Returns:
            The casefile, or None if not found
        """
        if self.use_mocks:
            return self.casefiles.get(casefile_id)
        else:
            doc = self.casefiles_collection.document(casefile_id).get()
            if doc.exists:
                # Convert back to CasefileModel
                casefile_data = doc.to_dict()
                casefile_data["sessions"] = casefile_data.get("sessions", [])

                return CasefileModel.model_validate(casefile_data)
            return None
    
    async def update_casefile(self, casefile: CasefileModel) -> None:
        """Update a casefile.
        
        Args:
            casefile: The casefile to update
        """
        if self.use_mocks:
            self.casefiles[casefile.id] = casefile
        else:
            # Convert to dict for Firestore
            casefile_dict = casefile.model_dump()
            casefile_dict["sessions"] = list(casefile.sessions)

            self.casefiles_collection.document(casefile.id).set(casefile_dict)
    
    async def list_casefiles(self, user_id: Optional[str] = None) -> List[CasefileSummary]:
        """List casefiles, optionally filtered by user.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of casefile summaries
        """
        if self.use_mocks:
            casefiles = list(self.casefiles.values())
            # Apply filter
            if user_id:
                casefiles = [c for c in casefiles if c.metadata.created_by == user_id]
                
            # Convert to summaries
            return [
                CasefileSummary(
                    id=c.id,
                    title=c.metadata.title,
                    description=c.metadata.description,
                    tags=c.metadata.tags,
                    created_at=c.metadata.created_at,
                    resource_count=c.resource_count,
                    session_count=len(c.sessions)
                )
                for c in casefiles
            ]
        else:
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
                data["sessions"] = data.get("sessions", [])

                casefile = CasefileModel.model_validate(data)
                
                results.append(
                    CasefileSummary(
                        id=casefile.id,
                        title=casefile.metadata.title,
                        description=casefile.metadata.description,
                        tags=casefile.metadata.tags,
                        created_at=casefile.metadata.created_at,
                        resource_count=casefile.resource_count,
                        session_count=len(casefile.sessions)
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
        if self.use_mocks:
            if casefile_id in self.casefiles:
                del self.casefiles[casefile_id]
                return True
            return False
        else:
            try:
                self.casefiles_collection.document(casefile_id).delete()
                return True
            except Exception as e:
                logger.error(f"Error deleting casefile {casefile_id}: {e}")
                return False