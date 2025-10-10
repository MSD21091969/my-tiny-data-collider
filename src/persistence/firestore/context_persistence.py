"""
Firestore implementation of context persistence.
"""

import logging
import os
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

from google.cloud.firestore_v1.base_query import FieldFilter

from ...pydantic_ai_integration.persistence import ContextPersistenceProvider
from ..firestore import DEFAULT_DATABASE, get_firestore_client

logger = logging.getLogger(__name__)

# Constants
CONTEXT_COLLECTION = "mds_contexts"
MAX_LIST_LIMIT = 100
CHUNK_SIZE = 1000000  # ~1MB
MAX_DOCUMENT_SIZE = 1048576  # Firestore's 1MB limit

class FirestorePersistenceProvider(ContextPersistenceProvider):
    """Persistence provider that uses Firestore."""
    
    def __init__(self):
        """Initialize the provider."""
        self.db = None
        try:
            self.db = get_firestore_client()
            database_id = os.environ.get("FIRESTORE_DATABASE", DEFAULT_DATABASE)
            logger.info(f"Firestore persistence provider initialized with database: {database_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore persistence provider: {e}")
            logger.debug(traceback.format_exc())
    
    def _get_context_ref(self, session_id: str):
        """Get the document reference for a session context.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Firestore document reference
        """
        return self.db.collection(CONTEXT_COLLECTION).document(session_id)
    
    def _split_large_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Split large context data into chunks if needed.
        
        Args:
            data: The context data to potentially split
            
        Returns:
            Potentially modified context with chunked data
        """
        # Check if we need to chunk any large collections
        for field_name in ["tool_events", "conversation_history", "related_documents"]:
            if field_name in data and len(str(data[field_name])) > CHUNK_SIZE:
                # Create reference to chunked data
                chunk_collection = f"{field_name}_chunks"
                data[f"{field_name}_chunked"] = True
                
                # Store the count but remove the actual data
                data[f"{field_name}_count"] = len(data[field_name])
                chunks = data.pop(field_name)
                
                # Return the chunks separately
                return data, field_name, chunks
        
        # No chunking needed
        return data, None, None
    
    def _store_chunks(self, session_id: str, field_name: str, chunks: List[Any]):
        """Store large data chunks in separate documents.
        
        Args:
            session_id: The session identifier
            field_name: The field name for the chunks
            chunks: The data chunks to store
        """
        chunk_collection = self.db.collection(CONTEXT_COLLECTION).document(session_id).collection(f"{field_name}_chunks")
        
        # Clear existing chunks
        existing = chunk_collection.limit(100).stream()
        for doc in existing:
            doc.reference.delete()
        
        # Store in batches of 500 (Firestore batch limit)
        batch_size = 500
        for i in range(0, len(chunks), batch_size):
            batch = self.db.batch()
            batch_chunks = chunks[i:i+batch_size]
            
            for j, chunk in enumerate(batch_chunks):
                chunk_id = f"{i+j:08d}"  # Pad with zeros for correct ordering
                chunk_ref = chunk_collection.document(chunk_id)
                batch.set(chunk_ref, {"data": chunk, "index": i+j})
            
            batch.commit()
            logger.debug(f"Stored {len(batch_chunks)} chunks for {session_id}/{field_name}")
    
    def _retrieve_chunks(self, session_id: str, field_name: str) -> List[Any]:
        """Retrieve chunked data from separate documents.
        
        Args:
            session_id: The session identifier
            field_name: The field name for the chunks
            
        Returns:
            The reassembled data
        """
        chunk_collection = self.db.collection(CONTEXT_COLLECTION).document(session_id).collection(f"{field_name}_chunks")
        chunks = []
        
        # Query chunks ordered by ID (which we padded with zeros)
        query = chunk_collection.order_by("index").stream()
        
        for doc in query:
            chunk_data = doc.to_dict().get("data")
            if chunk_data:
                chunks.append(chunk_data)
        
        logger.debug(f"Retrieved {len(chunks)} chunks for {session_id}/{field_name}")
        return chunks
    
    def save_context(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Save context data to Firestore.
        
        Args:
            session_id: The session identifier
            data: Serialized context data
            
        Returns:
            Whether save was successful
        """
        if not self.db:
            logger.error("Cannot save: Firestore client not initialized")
            return False
            
        try:
            # Add metadata
            data["_persistence"] = {
                "saved_at": datetime.now().isoformat(),
                "provider": "firestore"
            }
            
            # Check if we need to split large collections
            main_data, chunk_field, chunks = self._split_large_context(data)
            
            # Save main context document
            self._get_context_ref(session_id).set(main_data)
            
            # Store chunks if needed
            if chunk_field and chunks:
                self._store_chunks(session_id, chunk_field, chunks)
                
            logger.debug(f"Saved context for session {session_id} to Firestore")
            return True
        except Exception as e:
            logger.error(f"Failed to save context for session {session_id}: {e}")
            logger.debug(traceback.format_exc())
            return False
        
    def load_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load context data from Firestore.
        
        Args:
            session_id: The session identifier
            
        Returns:
            The loaded context data or None if not found
        """
        if not self.db:
            logger.error("Cannot load: Firestore client not initialized")
            return None
            
        try:
            # Get main document
            doc = self._get_context_ref(session_id).get()
            if not doc.exists:
                logger.warning(f"No saved context found for session {session_id}")
                return None
                
            data = doc.to_dict()
            
            # Check for chunked fields and retrieve if needed
            for field_name in ["tool_events", "conversation_history", "related_documents"]:
                if data.get(f"{field_name}_chunked"):
                    chunks = self._retrieve_chunks(session_id, field_name)
                    data[field_name] = chunks
                    
                    # Clean up chunk metadata
                    data.pop(f"{field_name}_chunked", None)
                    data.pop(f"{field_name}_count", None)
            
            logger.debug(f"Loaded context for session {session_id} from Firestore")
            return data
        except Exception as e:
            logger.error(f"Failed to load context for session {session_id}: {e}")
            logger.debug(traceback.format_exc())
            return None
        
    def delete_context(self, session_id: str) -> bool:
        """Delete context data from Firestore.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Whether deletion was successful
        """
        if not self.db:
            logger.error("Cannot delete: Firestore client not initialized")
            return False
            
        try:
            # Check for chunked collections and delete those first
            doc = self._get_context_ref(session_id).get()
            if doc.exists:
                data = doc.to_dict()
                
                # Delete any chunk collections
                for field_name in ["tool_events", "conversation_history", "related_documents"]:
                    if data.get(f"{field_name}_chunked"):
                        chunk_collection = self._get_context_ref(session_id).collection(f"{field_name}_chunks")
                        self._delete_collection(chunk_collection)
            
            # Delete the main document
            self._get_context_ref(session_id).delete()
            
            logger.debug(f"Deleted context for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete context for session {session_id}: {e}")
            return False
    
    def _delete_collection(self, collection, batch_size=50):
        """Delete a collection in batches to avoid timeout.
        
        Args:
            collection: The collection reference
            batch_size: The batch size
        """
        docs = collection.limit(batch_size).stream()
        deleted = 0
        
        for doc in docs:
            doc.reference.delete()
            deleted += 1
            
        if deleted >= batch_size:
            # Recursive call to delete more
            self._delete_collection(collection, batch_size)
        
    def list_sessions(self) -> List[str]:
        """List all available session IDs.
        
        Returns:
            List of session IDs
        """
        if not self.db:
            logger.error("Cannot list: Firestore client not initialized")
            return []
            
        try:
            query = self.db.collection(CONTEXT_COLLECTION).limit(MAX_LIST_LIMIT).stream()
            session_ids = [doc.id for doc in query]
            return session_ids
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []
    
    def list_sessions_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """List sessions for a specific user.
        
        Args:
            user_id: The user ID to filter by
            
        Returns:
            List of session metadata
        """
        if not self.db:
            logger.error("Cannot list: Firestore client not initialized")
            return []
            
        try:
            query = (self.db.collection(CONTEXT_COLLECTION)
                    .where(filter=FieldFilter("user_id", "==", user_id))
                    .limit(MAX_LIST_LIMIT)
                    .stream())
                    
            sessions = []
            for doc in query:
                data = doc.to_dict()
                sessions.append({
                    "session_id": doc.id,
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "casefile_id": data.get("casefile_id")
                })
                
            return sessions
        except Exception as e:
            logger.error(f"Failed to list sessions for user {user_id}: {e}")
            return []