"""
Repository for chat sessions (Firestore only).
"""

from typing import Dict, Any, List, Optional
import logging

from ..pydantic_models.communication.models import ChatSession

logger = logging.getLogger(__name__)

class ChatSessionRepository:
    """Repository for chat sessions using Firestore storage."""
    
    def __init__(self):
        """Initialize the repository."""
        # Initialize Firestore client
        from ..persistence.firestore import get_firestore_client
        self.db = get_firestore_client()
        self.collection = self.db.collection('chat_sessions')
    
    async def create_session(self, session: ChatSession) -> None:
        """Create a new chat session.
        
        Args:
            session: The session to create
        """
        doc_ref = self.collection.document(session.session_id)
        await doc_ref.set(session.model_dump(mode="json"))
    
    async def update_session(self, session: ChatSession) -> None:
        """Update an existing chat session.
        
        Args:
            session: The session to update
        """
        doc_ref = self.collection.document(session.session_id)
        await doc_ref.set(session.model_dump(mode="json"))
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            The session or None if not found
        """
        doc_ref = self.collection.document(session_id)
        doc = await doc_ref.get()
        
        if doc.exists:
            return ChatSession.model_validate(doc.to_dict())
        return None
    
    async def list_sessions(self, user_id: Optional[str] = None, 
                          casefile_id: Optional[str] = None) -> List[ChatSession]:
        """List sessions, optionally filtered by user or casefile.
        
        Args:
            user_id: Optional user ID to filter by
            casefile_id: Optional casefile ID to filter by
            
        Returns:
            List of matching sessions
        """
        query = self.collection
        
        # Apply filters
        if user_id:
            query = query.where('user_id', '==', user_id)
        if casefile_id:
            query = query.where('casefile_id', '==', casefile_id)
            
        docs = await query.get()
        return [ChatSession.model_validate(doc.to_dict()) for doc in docs]