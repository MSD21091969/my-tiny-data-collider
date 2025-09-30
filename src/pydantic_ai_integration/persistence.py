"""
Persistence mechanisms for MDSContext.

This module provides different persistence implementations for storing 
and retrieving MDSContext objects.
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List, Callable
from uuid import UUID
import time
from datetime import datetime
from functools import wraps
import threading
import traceback

logger = logging.getLogger(__name__)

class ContextPersistenceProvider:
    """Base class for context persistence providers."""
    
    def save_context(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Save context data for a session.
        
        Args:
            session_id: The session identifier
            data: Serialized context data
            
        Returns:
            Whether save was successful
        """
        raise NotImplementedError("Subclasses must implement save_context")
        
    def load_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load context data for a session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            The loaded context data or None if not found
        """
        raise NotImplementedError("Subclasses must implement load_context")
        
    def delete_context(self, session_id: str) -> bool:
        """Delete context data for a session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Whether deletion was successful
        """
        raise NotImplementedError("Subclasses must implement delete_context")
        
    def list_sessions(self) -> List[str]:
        """List all available session IDs.
        
        Returns:
            List of session IDs
        """
        raise NotImplementedError("Subclasses must implement list_sessions")

class FileSystemPersistenceProvider(ContextPersistenceProvider):
    """Persistence provider that uses the local file system."""
    
    def __init__(self, base_dir: str = None):
        """Initialize the provider.
        
        Args:
            base_dir: Base directory for storing context files
        """
        self.base_dir = base_dir or os.path.join(os.getcwd(), "mds_context")
        os.makedirs(self.base_dir, exist_ok=True)
        logger.info(f"FileSystem persistence initialized with base directory: {self.base_dir}")
        
    def _get_context_path(self, session_id: str) -> str:
        """Get the file path for a session context.
        
        Args:
            session_id: The session identifier
            
        Returns:
            File path for the context
        """
        return os.path.join(self.base_dir, f"{session_id}.json")
        
    def save_context(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Save context data to a JSON file.
        
        Args:
            session_id: The session identifier
            data: Serialized context data
            
        Returns:
            Whether save was successful
        """
        try:
            file_path = self._get_context_path(session_id)
            
            # Add metadata
            data["_persistence"] = {
                "saved_at": datetime.now().isoformat(),
                "provider": "filesystem"
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved context for session {session_id} to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save context for session {session_id}: {e}")
            logger.debug(traceback.format_exc())
            return False
        
    def load_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load context data from a JSON file.
        
        Args:
            session_id: The session identifier
            
        Returns:
            The loaded context data or None if not found
        """
        file_path = self._get_context_path(session_id)
        if not os.path.exists(file_path):
            logger.warning(f"No saved context found for session {session_id}")
            return None
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            logger.debug(f"Loaded context for session {session_id} from {file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load context for session {session_id}: {e}")
            return None
        
    def delete_context(self, session_id: str) -> bool:
        """Delete context data file.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Whether deletion was successful
        """
        file_path = self._get_context_path(session_id)
        if not os.path.exists(file_path):
            logger.warning(f"No saved context found for session {session_id}")
            return False
            
        try:
            os.remove(file_path)
            logger.debug(f"Deleted context for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete context for session {session_id}: {e}")
            return False
        
    def list_sessions(self) -> List[str]:
        """List all available session IDs.
        
        Returns:
            List of session IDs
        """
        try:
            files = os.listdir(self.base_dir)
            session_ids = [os.path.splitext(f)[0] for f in files if f.endswith('.json')]
            return session_ids
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []

class InMemoryPersistenceProvider(ContextPersistenceProvider):
    """Persistence provider that keeps context in memory."""
    
    def __init__(self):
        """Initialize the provider."""
        self.contexts = {}
        logger.info("InMemory persistence initialized")
        
    def save_context(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Save context data to memory.
        
        Args:
            session_id: The session identifier
            data: Serialized context data
            
        Returns:
            Whether save was successful
        """
        try:
            # Add metadata
            data["_persistence"] = {
                "saved_at": datetime.now().isoformat(),
                "provider": "in_memory"
            }
            
            self.contexts[session_id] = data
            logger.debug(f"Saved context for session {session_id} to memory")
            return True
        except Exception as e:
            logger.error(f"Failed to save context for session {session_id}: {e}")
            return False
        
    def load_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load context data from memory.
        
        Args:
            session_id: The session identifier
            
        Returns:
            The loaded context data or None if not found
        """
        if session_id not in self.contexts:
            logger.warning(f"No saved context found for session {session_id}")
            return None
            
        logger.debug(f"Loaded context for session {session_id} from memory")
        return self.contexts[session_id]
        
    def delete_context(self, session_id: str) -> bool:
        """Delete context data from memory.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Whether deletion was successful
        """
        if session_id not in self.contexts:
            logger.warning(f"No saved context found for session {session_id}")
            return False
            
        del self.contexts[session_id]
        logger.debug(f"Deleted context for session {session_id}")
        return True
        
    def list_sessions(self) -> List[str]:
        """List all available session IDs.
        
        Returns:
            List of session IDs
        """
        return list(self.contexts.keys())

class AutoSaveContextManager:
    """Manager that automatically saves context periodically."""
    
    def __init__(self, provider: ContextPersistenceProvider, interval_seconds: int = 60):
        """Initialize the manager.
        
        Args:
            provider: The persistence provider to use
            interval_seconds: How often to auto-save in seconds
        """
        self.provider = provider
        self.interval = interval_seconds
        self.contexts = {}  # Maps session_id to context
        self.running = False
        self.thread = None
        logger.info(f"AutoSaveContextManager initialized with interval {interval_seconds}s")
        
    def register_context(self, context):
        """Register a context for auto-saving.
        
        Args:
            context: The context to auto-save
        """
        session_id = str(context.session_id)
        self.contexts[session_id] = context
        
        # Set up the persistence handler
        context.set_persistence_handler(
            lambda data: self.provider.save_context(session_id, data),
            auto_persist=False  # Don't auto-persist on every change, we'll do it on interval
        )
        
        logger.debug(f"Registered context for session {session_id} for auto-save")
        
    def unregister_context(self, session_id: str):
        """Unregister a context.
        
        Args:
            session_id: The session identifier
        """
        if session_id in self.contexts:
            # Final save
            context = self.contexts[session_id]
            self.provider.save_context(str(session_id), context.to_dict())
            del self.contexts[session_id]
            logger.debug(f"Unregistered context for session {session_id}")
        
    def start(self):
        """Start the auto-save thread."""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._auto_save_loop, daemon=True)
        self.thread.start()
        logger.info("Started auto-save thread")
        
    def stop(self):
        """Stop the auto-save thread."""
        if not self.running:
            return
            
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
        
        # Final save for all contexts
        for session_id, context in self.contexts.items():
            try:
                self.provider.save_context(session_id, context.to_dict())
            except Exception as e:
                logger.error(f"Failed to save context on shutdown: {e}")
                
        logger.info("Stopped auto-save thread")
        
    def _auto_save_loop(self):
        """Background thread that saves contexts periodically."""
        while self.running:
            try:
                # Sleep first to allow initial setup to complete
                for _ in range(self.interval):
                    if not self.running:
                        break
                    time.sleep(1)
                
                if not self.running:
                    break
                
                # Save all registered contexts
                for session_id, context in list(self.contexts.items()):
                    try:
                        logger.debug(f"Auto-saving context for session {session_id}")
                        self.provider.save_context(session_id, context.to_dict())
                    except Exception as e:
                        logger.error(f"Failed to auto-save context for session {session_id}: {e}")
                        
            except Exception as e:
                logger.error(f"Error in auto-save loop: {e}")


# Global providers
_DEFAULT_PROVIDER = None
_AUTO_SAVE_MANAGER = None

def get_persistence_provider(provider_type: str = None) -> ContextPersistenceProvider:
    """Get a persistence provider of the specified type.
    
    Args:
        provider_type: Type of provider ('filesystem', 'in_memory', 'firestore')
        
    Returns:
        A persistence provider instance
    """
    global _DEFAULT_PROVIDER
    
    if _DEFAULT_PROVIDER is not None:
        return _DEFAULT_PROVIDER
        
    if provider_type is None:
        # Check environment variable
        provider_type = os.environ.get("MDS_PERSISTENCE_TYPE", "in_memory")
        
    if provider_type == "filesystem":
        base_dir = os.environ.get("MDS_PERSISTENCE_DIR", None)
        _DEFAULT_PROVIDER = FileSystemPersistenceProvider(base_dir)
    elif provider_type == "firestore":
        try:
            # Import here to avoid requiring Firestore library if not used
            from ..persistence.firestore.context_persistence import FirestorePersistenceProvider
            _DEFAULT_PROVIDER = FirestorePersistenceProvider()
        except ImportError:
            logger.error("Failed to load Firestore persistence provider. Falling back to in-memory.")
            _DEFAULT_PROVIDER = InMemoryPersistenceProvider()
    else:
        _DEFAULT_PROVIDER = InMemoryPersistenceProvider()
        
    return _DEFAULT_PROVIDER

def get_auto_save_manager(interval_seconds: int = None) -> AutoSaveContextManager:
    """Get the auto-save context manager.
    
    Args:
        interval_seconds: How often to auto-save in seconds
        
    Returns:
        The auto-save manager instance
    """
    global _AUTO_SAVE_MANAGER
    
    if _AUTO_SAVE_MANAGER is not None:
        return _AUTO_SAVE_MANAGER
        
    if interval_seconds is None:
        try:
            interval_seconds = int(os.environ.get("MDS_AUTOSAVE_INTERVAL", "60"))
        except ValueError:
            interval_seconds = 60
            
    provider = get_persistence_provider()
    _AUTO_SAVE_MANAGER = AutoSaveContextManager(provider, interval_seconds)
    _AUTO_SAVE_MANAGER.start()
    
    return _AUTO_SAVE_MANAGER

def with_auto_persistence(context_factory):
    """Decorator for functions that create MDSContext to auto-register for persistence.
    
    Args:
        context_factory: Function that returns an MDSContext
        
    Returns:
        Wrapped function
    """
    @wraps(context_factory)
    def wrapper(*args, **kwargs):
        context = context_factory(*args, **kwargs)
        
        # Register with auto-save manager
        auto_save = get_auto_save_manager()
        auto_save.register_context(context)
        
        return context
    return wrapper