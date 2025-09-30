"""
Repository for chat sessions.
"""

from typing import Dict, Any, List, Optional
import logging

from ..pydantic_models.communication.models import ChatSession

logger = logging.getLogger(__name__)

class ChatSessionRepository:
    """Repository for chat sessions using either mock or Firestore storage."""
    
    def __init__(self, use_mocks: bool = False):
        """Initialize the repository.
        
        Args:
            use_mocks: Whether to use mock storage instead of Firestore
        """
        self.use_mocks = use_mocks
        self.mock_sessions = {}  # Used when use_mocks is True
        
        if not use_mocks:
            # Initialize Firestore client
            try:
                from ..persistence.firestore import get_firestore_client
                self.db = get_firestore_client()
                self.collection = self.db.collection('chat_sessions')
            except Exception as e:
                logger.warning(f"Failed to initialize Firestore, falling back to mock: {e}")
                self.use_mocks = True
    
    async def create_session(self, session: ChatSession) -> None:
        """Create a new chat session.
        
        Args:
            session: The session to create
        """
        if self.use_mocks:
            self.mock_sessions[session.session_id] = session
        else:
            doc_ref = self.collection.document(session.session_id)
            await doc_ref.set(session.model_dump(mode="json"))
    
    async def update_session(self, session: ChatSession) -> None:
        """Update an existing chat session.
        
        Args:
            session: The session to update
        """
        if self.use_mocks:
            self.mock_sessions[session.session_id] = session
        else:
            doc_ref = self.collection.document(session.session_id)
            await doc_ref.set(session.model_dump(mode="json"))
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            The session or None if not found
        """
        if self.use_mocks:
            session_data = self.mock_sessions.get(session_id)
            return ChatSession.model_validate(session_data) if session_data else None
        else:
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
        if self.use_mocks:
            sessions = list(self.mock_sessions.values())
            
            # Apply filters
            if user_id:
                sessions = [s for s in sessions if s.user_id == user_id]
            if casefile_id:
                sessions = [s for s in sessions if s.casefile_id == casefile_id]
                
            return sessions
        else:
            query = self.collection
            
            # Apply filters
            if user_id:
                query = query.where('user_id', '==', user_id)
            if casefile_id:
                query = query.where('casefile_id', '==', casefile_id)
                
            docs = await query.get()
            return [ChatSession.model_validate(doc.to_dict()) for doc in docs]