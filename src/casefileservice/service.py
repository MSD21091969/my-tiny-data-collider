"""
Service for managing casefiles.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..pydantic_models.casefile.models import CasefileModel, CasefileMetadata
from .repository import CasefileRepository

logger = logging.getLogger(__name__)

class CasefileService:
    """Service for managing casefiles (Firestore only)."""
    
    def __init__(self):
        """Initialize the service."""
        self.repository = CasefileRepository()
        
    async def create_casefile(self, user_id: str, title: str, description: str = "", tags: List[str] = None) -> Dict[str, str]:
        """Create a new casefile.
        
        Args:
            user_id: ID of the user creating the casefile
            title: Title of the casefile
            description: Description of the casefile
            tags: Optional tags for the casefile
            
        Returns:
            Dictionary with the casefile ID
        """
        # Create metadata
        metadata = CasefileMetadata(
            title=title,
            description=description,
            tags=tags or [],
            created_by=user_id
        )
        
        # Create casefile
        casefile = CasefileModel(
            metadata=metadata
        )
        
        # Store in repository
        casefile_id = await self.repository.create_casefile(casefile)
        
        return {"casefile_id": casefile_id}
    
    async def get_casefile(self, casefile_id: str) -> Dict[str, Any]:
        """Get a casefile by ID.
        
        Args:
            casefile_id: ID of the casefile to retrieve
            
        Returns:
            The casefile data
            
        Raises:
            ValueError: If casefile not found
        """
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            raise ValueError(f"Casefile {casefile_id} not found")
            
        return casefile.model_dump()
    
    async def update_casefile(self, casefile_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a casefile.
        
        Args:
            casefile_id: ID of the casefile to update
            updates: Dictionary of fields to update
            
        Returns:
            The updated casefile data
            
        Raises:
            ValueError: If casefile not found
        """
        # Get existing casefile
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            raise ValueError(f"Casefile {casefile_id} not found")
        
        # Update metadata fields
        metadata = casefile.metadata
        if "title" in updates:
            metadata.title = updates["title"]
        if "description" in updates:
            metadata.description = updates["description"]
        if "tags" in updates:
            metadata.tags = updates["tags"]
            
        # Update notes
        if "notes" in updates:
            casefile.notes = updates["notes"]
            
        # Update timestamp
        metadata.updated_at = datetime.now().isoformat()
        
        # Store updated casefile
        await self.repository.update_casefile(casefile)
        
        return casefile.model_dump()
    
    async def list_casefiles(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List casefiles, optionally filtered by user.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of casefile summaries
        """
        summaries = await self.repository.list_casefiles(user_id=user_id)
        return [summary.model_dump() for summary in summaries]
    
    async def delete_casefile(self, casefile_id: str) -> Dict[str, Any]:
        """Delete a casefile.
        
        Args:
            casefile_id: ID of the casefile to delete
            
        Returns:
            Status information
            
        Raises:
            ValueError: If casefile not found
        """
        # Verify casefile exists
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            raise ValueError(f"Casefile {casefile_id} not found")
            
        # Delete casefile
        success = await self.repository.delete_casefile(casefile_id)
        
        if not success:
            raise ValueError(f"Failed to delete casefile {casefile_id}")
            
        return {
            "casefile_id": casefile_id,
            "status": "deleted"
        }
        
    async def add_session_to_casefile(self, casefile_id: str, session_id: str) -> Dict[str, Any]:
        """Add a session to a casefile.
        
        Args:
            casefile_id: ID of the casefile
            session_id: ID of the session to add
            
        Returns:
            Updated casefile data
            
        Raises:
            ValueError: If casefile not found
        """
        # Get existing casefile
        casefile = await self.repository.get_casefile(casefile_id)
        if not casefile:
            raise ValueError(f"Casefile {casefile_id} not found")
            
        # Add session if not already present
        if session_id not in casefile.session_ids:
            casefile.session_ids.append(session_id)
            casefile.metadata.updated_at = datetime.now().isoformat()
            
            # Store updated casefile
            await self.repository.update_casefile(casefile)
            
        return casefile.model_dump()