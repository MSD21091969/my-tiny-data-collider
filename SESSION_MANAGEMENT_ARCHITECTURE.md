# Session Management Architecture

## Overview

This document details the enhanced session management architecture for the feature/src-services branch. The goal is to create a unified, context-aware session management system that supports rich metadata, state persistence, and integration with the execution pipeline.

## Architecture Goals

1. **Unified Session Interface**: Create a consistent session interface across the system
2. **Context Integration**: Tight integration with execution context
3. **Persistence Flexibility**: Support multiple storage backends for session data
4. **Rich Metadata**: Maintain detailed session metadata for analytics and debugging
5. **AI-Ready**: Include session information useful for AI decision-making
6. **Performance**: Efficient session retrieval and storage
7. **Scalability**: Support for distributed session management

## Key Components

### 1. Session Model

The core `Session` model encapsulates all session data and provides rich metadata:

```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import time
import uuid

class Session(BaseModel):
    """
    Session model with rich metadata.
    
    Represents a user session with contextual information.
    """
    
    # Session identifiers
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    
    # Session metadata
    created_at: float = Field(default_factory=time.time)
    last_accessed_at: float = Field(default_factory=time.time)
    expiry_at: Optional[float] = None
    
    # Session state
    state: Dict[str, Any] = Field(default_factory=dict)
    
    # Session preferences and settings
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    # Historical context
    history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Security information
    auth_info: Optional[Dict[str, Any]] = None
    
    # AI-related session data
    ai_context: Dict[str, Any] = Field(default_factory=dict)
    
    # Feature flags and experiments
    feature_flags: Dict[str, Any] = Field(default_factory=dict)
    
    # Device and environment information
    environment: Dict[str, Any] = Field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get session state value."""
        return self.state.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set session state value."""
        self.state[key] = value
        self.touch()
    
    def delete(self, key: str) -> None:
        """Delete session state value."""
        if key in self.state:
            del self.state[key]
            self.touch()
    
    def has(self, key: str) -> bool:
        """Check if session state has key."""
        return key in self.state
    
    def clear(self) -> None:
        """Clear all session state."""
        self.state.clear()
        self.touch()
    
    def touch(self) -> None:
        """Update last accessed time."""
        self.last_accessed_at = time.time()
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        if self.expiry_at is None:
            return False
        return time.time() > self.expiry_at
    
    def set_expiry(self, seconds: int) -> None:
        """Set session expiry time."""
        self.expiry_at = time.time() + seconds
    
    def add_history_entry(self, entry_type: str, data: Dict[str, Any]) -> None:
        """Add entry to session history."""
        self.history.append({
            "timestamp": time.time(),
            "type": entry_type,
            "data": data
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "last_accessed_at": self.last_accessed_at,
            "expiry_at": self.expiry_at,
            "state_keys": list(self.state.keys()),
            "preferences": self.preferences,
            "history_count": len(self.history),
            "environment": self.environment
        }
```

### 2. Session Store Interface

A flexible storage interface that allows for different backend implementations:

```python
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import time
import asyncio

class SessionStore(ABC):
    """
    Abstract session store interface.
    
    Implementations provide storage for session data.
    """
    
    @abstractmethod
    async def get(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def set(self, session: Session) -> None:
        """
        Save session.
        
        Args:
            session: Session to save
        """
        pass
    
    @abstractmethod
    async def delete(self, session_id: str) -> None:
        """
        Delete session.
        
        Args:
            session_id: Session identifier
        """
        pass
    
    @abstractmethod
    async def get_all(self, filter_func=None) -> List[Session]:
        """
        Get all sessions matching filter.
        
        Args:
            filter_func: Optional filter function
            
        Returns:
            List of matching sessions
        """
        pass
    
    @abstractmethod
    async def cleanup_expired(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        pass
```

### 3. Session Store Implementations

Implementations for different storage backends:

#### Memory Store

```python
class MemorySessionStore(SessionStore):
    """In-memory session store implementation."""
    
    def __init__(self):
        """Initialize store."""
        self.sessions: Dict[str, Session] = {}
    
    async def get(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        session = self.sessions.get(session_id)
        
        if session and session.is_expired():
            # Remove expired session
            await self.delete(session_id)
            return None
        
        return session
    
    async def set(self, session: Session) -> None:
        """Save session."""
        self.sessions[session.session_id] = session
    
    async def delete(self, session_id: str) -> None:
        """Delete session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    async def get_all(self, filter_func=None) -> List[Session]:
        """Get all sessions matching filter."""
        if filter_func:
            return [s for s in self.sessions.values() if filter_func(s)]
        return list(self.sessions.values())
    
    async def cleanup_expired(self) -> int:
        """Clean up expired sessions."""
        expired_ids = [
            sid for sid, session in self.sessions.items()
            if session.is_expired()
        ]
        
        for sid in expired_ids:
            await self.delete(sid)
        
        return len(expired_ids)
```

#### Redis Store

```python
import aioredis
import json

class RedisSessionStore(SessionStore):
    """Redis session store implementation."""
    
    def __init__(
        self, 
        redis_url: str,
        prefix: str = "session:"
    ):
        """
        Initialize store.
        
        Args:
            redis_url: Redis connection URL
            prefix: Key prefix for sessions
        """
        self.redis_url = redis_url
        self.prefix = prefix
        self.redis = None
    
    async def initialize(self):
        """Initialize Redis connection."""
        if self.redis is None:
            self.redis = await aioredis.create_redis_pool(self.redis_url)
    
    async def get(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        await self.initialize()
        
        # Get session data from Redis
        key = f"{self.prefix}{session_id}"
        data = await self.redis.get(key)
        
        if not data:
            return None
        
        # Parse session data
        try:
            session_data = json.loads(data)
            session = Session(**session_data)
            
            if session.is_expired():
                # Remove expired session
                await self.delete(session_id)
                return None
            
            return session
        except Exception as e:
            print(f"Error deserializing session: {e}")
            return None
    
    async def set(self, session: Session) -> None:
        """Save session."""
        await self.initialize()
        
        # Serialize session data
        try:
            data = session.json()
            key = f"{self.prefix}{session.session_id}"
            
            # Set expiry if available
            if session.expiry_at:
                ttl = max(1, int(session.expiry_at - time.time()))
                await self.redis.setex(key, ttl, data)
            else:
                await self.redis.set(key, data)
        except Exception as e:
            print(f"Error serializing session: {e}")
    
    async def delete(self, session_id: str) -> None:
        """Delete session."""
        await self.initialize()
        
        key = f"{self.prefix}{session_id}"
        await self.redis.delete(key)
    
    async def get_all(self, filter_func=None) -> List[Session]:
        """Get all sessions matching filter."""
        await self.initialize()
        
        # Get all keys with prefix
        keys = await self.redis.keys(f"{self.prefix}*")
        sessions = []
        
        for key in keys:
            # Extract session ID from key
            session_id = key.decode('utf-8')[len(self.prefix):]
            
            # Get session
            session = await self.get(session_id)
            
            if session and (filter_func is None or filter_func(session)):
                sessions.append(session)
        
        return sessions
    
    async def cleanup_expired(self) -> int:
        """Clean up expired sessions."""
        # Redis automatically removes expired keys
        return 0
    
    async def close(self):
        """Close Redis connection."""
        if self.redis is not None:
            self.redis.close()
            await self.redis.wait_closed()
            self.redis = None
```

#### Database Store

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SessionEntity(Base):
    """Session entity for database storage."""
    
    __tablename__ = "sessions"
    
    session_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)
    created_at = Column(Float, nullable=False)
    last_accessed_at = Column(Float, nullable=False)
    expiry_at = Column(Float, nullable=True)
    data = Column(Text, nullable=False)  # JSON serialized session data


class DatabaseSessionStore(SessionStore):
    """Database session store implementation."""
    
    def __init__(self, db_url: str):
        """
        Initialize store.
        
        Args:
            db_url: Database connection URL
        """
        self.db_url = db_url
        self.engine = None
        self.session_factory = None
    
    async def initialize(self):
        """Initialize database connection."""
        if self.engine is None:
            self.engine = create_async_engine(self.db_url)
            self.session_factory = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
            
            # Create tables if they don't exist
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
    
    async def get(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        await self.initialize()
        
        async with self.session_factory() as db_session:
            # Query session entity
            entity = await db_session.get(SessionEntity, session_id)
            
            if not entity:
                return None
            
            # Parse session data
            try:
                session_data = json.loads(entity.data)
                session = Session(**session_data)
                
                if session.is_expired():
                    # Remove expired session
                    await self.delete(session_id)
                    return None
                
                return session
            except Exception as e:
                print(f"Error deserializing session: {e}")
                return None
    
    async def set(self, session: Session) -> None:
        """Save session."""
        await self.initialize()
        
        async with self.session_factory() as db_session:
            # Serialize session data
            try:
                data = session.json()
                
                # Create or update session entity
                entity = await db_session.get(SessionEntity, session.session_id)
                
                if entity:
                    # Update existing entity
                    entity.user_id = session.user_id
                    entity.last_accessed_at = session.last_accessed_at
                    entity.expiry_at = session.expiry_at
                    entity.data = data
                else:
                    # Create new entity
                    entity = SessionEntity(
                        session_id=session.session_id,
                        user_id=session.user_id,
                        created_at=session.created_at,
                        last_accessed_at=session.last_accessed_at,
                        expiry_at=session.expiry_at,
                        data=data
                    )
                    db_session.add(entity)
                
                await db_session.commit()
            except Exception as e:
                await db_session.rollback()
                print(f"Error serializing session: {e}")
    
    async def delete(self, session_id: str) -> None:
        """Delete session."""
        await self.initialize()
        
        async with self.session_factory() as db_session:
            # Delete session entity
            entity = await db_session.get(SessionEntity, session_id)
            
            if entity:
                await db_session.delete(entity)
                await db_session.commit()
    
    async def get_all(self, filter_func=None) -> List[Session]:
        """Get all sessions matching filter."""
        await self.initialize()
        
        async with self.session_factory() as db_session:
            # Query all session entities
            stmt = select(SessionEntity)
            result = await db_session.execute(stmt)
            entities = result.scalars().all()
            
            sessions = []
            
            for entity in entities:
                try:
                    session_data = json.loads(entity.data)
                    session = Session(**session_data)
                    
                    if session.is_expired():
                        continue
                    
                    if filter_func is None or filter_func(session):
                        sessions.append(session)
                except Exception as e:
                    print(f"Error deserializing session: {e}")
            
            return sessions
    
    async def cleanup_expired(self) -> int:
        """Clean up expired sessions."""
        await self.initialize()
        
        async with self.session_factory() as db_session:
            # Query expired session entities
            now = time.time()
            stmt = select(SessionEntity).where(
                SessionEntity.expiry_at < now
            )
            result = await db_session.execute(stmt)
            entities = result.scalars().all()
            
            # Delete expired sessions
            for entity in entities:
                await db_session.delete(entity)
            
            await db_session.commit()
            
            return len(entities)
    
    async def close(self):
        """Close database connection."""
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
```

### 4. Session Manager

The `SessionManager` provides high-level session management:

```python
class SessionManager:
    """
    Session manager for lifecycle management.
    
    Handles session creation, retrieval, and expiration.
    """
    
    def __init__(
        self,
        store: SessionStore,
        session_lifetime: int = 3600,  # 1 hour default
        cleanup_interval: int = 300,   # 5 minutes default
        auto_cleanup: bool = True
    ):
        """
        Initialize manager.
        
        Args:
            store: Session store
            session_lifetime: Default session lifetime in seconds
            cleanup_interval: Interval between cleanup runs in seconds
            auto_cleanup: Whether to automatically clean up expired sessions
        """
        self.store = store
        self.session_lifetime = session_lifetime
        self.cleanup_interval = cleanup_interval
        self.auto_cleanup = auto_cleanup
        self.last_cleanup: float = time.time()
        self.cleanup_task = None
    
    async def start(self):
        """Start session manager."""
        if self.auto_cleanup:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop(self):
        """Stop session manager."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            
        # Close store if needed
        if hasattr(self.store, 'close'):
            await self.store.close()
    
    async def get_session(
        self,
        session_id: str,
        create_if_missing: bool = False
    ) -> Optional[Session]:
        """
        Get session by ID.
        
        Args:
            session_id: Session identifier
            create_if_missing: Whether to create a new session if not found
            
        Returns:
            Session if found or created, None otherwise
        """
        # Try to get existing session
        session = await self.store.get(session_id)
        
        if session:
            # Update last accessed time
            session.touch()
            await self.store.set(session)
            
            # Check if cleanup is needed
            await self._maybe_cleanup()
            
            return session
        
        if create_if_missing:
            # Create new session
            return await self.create_session()
        
        return None
    
    async def create_session(
        self,
        user_id: Optional[str] = None,
        data: Dict[str, Any] = None
    ) -> Session:
        """
        Create new session.
        
        Args:
            user_id: Optional user identifier
            data: Optional initial session data
            
        Returns:
            New session
        """
        # Create session with default lifetime
        session = Session(
            user_id=user_id,
            expiry_at=time.time() + self.session_lifetime
        )
        
        # Add initial data
        if data:
            session.state.update(data)
        
        # Save session
        await self.store.set(session)
        
        # Check if cleanup is needed
        await self._maybe_cleanup()
        
        return session
    
    async def update_session(self, session: Session) -> None:
        """
        Update session.
        
        Args:
            session: Session to update
        """
        # Update last accessed time
        session.touch()
        
        # Save session
        await self.store.set(session)
        
        # Check if cleanup is needed
        await self._maybe_cleanup()
    
    async def refresh_session(
        self,
        session_id: str,
        extend_lifetime: bool = True
    ) -> Optional[Session]:
        """
        Refresh session.
        
        Args:
            session_id: Session identifier
            extend_lifetime: Whether to extend session lifetime
            
        Returns:
            Refreshed session if found, None otherwise
        """
        # Get session
        session = await self.store.get(session_id)
        
        if not session:
            return None
        
        # Update last accessed time
        session.touch()
        
        # Extend lifetime if requested
        if extend_lifetime and session.expiry_at:
            session.set_expiry(self.session_lifetime)
        
        # Save session
        await self.store.set(session)
        
        return session
    
    async def delete_session(self, session_id: str) -> None:
        """
        Delete session.
        
        Args:
            session_id: Session identifier
        """
        await self.store.delete(session_id)
    
    async def get_user_sessions(self, user_id: str) -> List[Session]:
        """
        Get sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of user sessions
        """
        return await self.store.get_all(
            lambda s: s.user_id == user_id
        )
    
    async def _maybe_cleanup(self):
        """Clean up expired sessions if needed."""
        if not self.auto_cleanup:
            return
            
        now = time.time()
        
        if (now - self.last_cleanup) >= self.cleanup_interval:
            await self.cleanup()
    
    async def cleanup(self, force: bool = False) -> int:
        """
        Clean up expired sessions.
        
        Args:
            force: Force cleanup regardless of interval
            
        Returns:
            Number of sessions cleaned up
        """
        now = time.time()
        
        # Check if cleanup is needed
        if not force and (now - self.last_cleanup) < self.cleanup_interval:
            return 0
        
        # Cleanup expired sessions
        count = await self.store.cleanup_expired()
        
        # Update last cleanup time
        self.last_cleanup = now
        
        return count
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                # Sleep until next cleanup
                await asyncio.sleep(self.cleanup_interval)
                
                # Clean up expired sessions
                await self.cleanup(force=True)
            except asyncio.CancelledError:
                # Task cancelled, exit loop
                break
            except Exception as e:
                # Log error and continue
                print(f"Error during session cleanup: {e}")
```

### 5. Session Middleware

Middleware for FastAPI that integrates with the session manager:

```python
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class SessionMiddleware(BaseHTTPMiddleware):
    """
    Session middleware for FastAPI.
    
    Handles session retrieval and storage in HTTP requests.
    """
    
    def __init__(
        self,
        app,
        session_manager: SessionManager,
        cookie_name: str = "session_id",
        cookie_max_age: Optional[int] = None,
        cookie_path: str = "/",
        cookie_domain: Optional[str] = None,
        cookie_secure: bool = False,
        cookie_httponly: bool = True,
        cookie_samesite: str = "lax",
        header_name: Optional[str] = "X-Session-ID",
        create_session: bool = True
    ):
        """
        Initialize middleware.
        
        Args:
            app: FastAPI application
            session_manager: Session manager
            cookie_name: Name of the session cookie
            cookie_max_age: Max age of the cookie in seconds
            cookie_path: Cookie path
            cookie_domain: Cookie domain
            cookie_secure: Whether the cookie is secure
            cookie_httponly: Whether the cookie is HTTP only
            cookie_samesite: SameSite cookie policy
            header_name: Name of the session header
            create_session: Whether to create a session if missing
        """
        super().__init__(app)
        self.session_manager = session_manager
        self.cookie_name = cookie_name
        self.cookie_max_age = cookie_max_age
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite
        self.header_name = header_name
        self.create_session = create_session
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request.
        
        Args:
            request: HTTP request
            call_next: Next middleware in chain
            
        Returns:
            HTTP response
        """
        # Get session ID from cookie or header
        session_id = self._get_session_id(request)
        
        # Get session from store
        session = None
        
        if session_id:
            session = await self.session_manager.get_session(session_id)
        
        if not session and self.create_session:
            # Create new session
            session = await self.session_manager.create_session()
        
        if session:
            # Add session to request state
            request.state.session = session
            request.state.session_id = session.session_id
        
        # Process request
        response = await call_next(request)
        
        if session:
            # Update session
            await self.session_manager.update_session(session)
            
            # Set session ID in cookie or header
            self._set_session_id(response, session.session_id)
        
        return response
    
    def _get_session_id(self, request: Request) -> Optional[str]:
        """
        Get session ID from request.
        
        Args:
            request: HTTP request
            
        Returns:
            Session ID if found, None otherwise
        """
        # Try to get session ID from cookie
        session_id = request.cookies.get(self.cookie_name)
        
        # If not found and header name is set, try to get from header
        if not session_id and self.header_name:
            session_id = request.headers.get(self.header_name)
        
        return session_id
    
    def _set_session_id(self, response: Response, session_id: str) -> None:
        """
        Set session ID in response.
        
        Args:
            response: HTTP response
            session_id: Session ID
        """
        # Set session ID in cookie
        response.set_cookie(
            key=self.cookie_name,
            value=session_id,
            max_age=self.cookie_max_age,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite
        )
        
        # If header name is set, set in header as well
        if self.header_name:
            response.headers[self.header_name] = session_id
```

### 6. Session Context Integration

Integration of session with execution context:

```python
class SessionContextProvider:
    """
    Provider for session context integration.
    
    Integrates session with execution context.
    """
    
    def __init__(self, session_manager: SessionManager):
        """
        Initialize provider.
        
        Args:
            session_manager: Session manager
        """
        self.session_manager = session_manager
    
    async def enrich_context(
        self,
        context: ExecutionContext,
        session_id: Optional[str] = None
    ) -> ExecutionContext:
        """
        Enrich context with session information.
        
        Args:
            context: Execution context
            session_id: Optional session ID
            
        Returns:
            Enriched context
        """
        # If no session ID provided, use from context
        if not session_id:
            session_id = context.session_id
        
        if not session_id:
            return context
        
        # Get session
        session = await self.session_manager.get_session(session_id)
        
        if not session:
            return context
        
        # Add session information to context
        context.session_id = session.session_id
        context.user_id = session.user_id or context.user_id
        
        # Add session properties to context
        for key, value in session.state.items():
            if key.startswith("context:"):
                # Add to context properties
                property_key = key[8:]  # Remove "context:" prefix
                context.add_property(property_key, value)
        
        # Add session preferences
        if session.preferences:
            context.add_property("preferences", session.preferences)
        
        # Add session AI context
        if session.ai_context:
            context.ai_metadata.update(session.ai_context)
        
        # Add session feature flags
        if session.feature_flags:
            context.add_property("feature_flags", session.feature_flags)
        
        return context
    
    async def update_session_from_context(
        self,
        context: ExecutionContext,
        session_id: Optional[str] = None
    ) -> Optional[Session]:
        """
        Update session from context.
        
        Args:
            context: Execution context
            session_id: Optional session ID
            
        Returns:
            Updated session if found, None otherwise
        """
        # If no session ID provided, use from context
        if not session_id:
            session_id = context.session_id
        
        if not session_id:
            return None
        
        # Get session
        session = await self.session_manager.get_session(session_id)
        
        if not session:
            return None
        
        # Update session from context
        if context.user_id:
            session.user_id = context.user_id
        
        # Add context properties to session
        for key, value in context.properties.items():
            if key.startswith("session:"):
                # Add to session state
                state_key = key[8:]  # Remove "session:" prefix
                session.set(state_key, value)
        
        # Update session preferences
        if context.has_property("preferences"):
            preferences = context.get_property("preferences")
            if isinstance(preferences, dict):
                session.preferences.update(preferences)
        
        # Update session AI context
        if context.ai_metadata:
            session.ai_context.update(context.ai_metadata)
        
        # Add context event to session history
        session.add_history_entry("context", {
            "context_id": context.context_id,
            "tool_name": context.tool_name,
            "duration": context.duration()
        })
        
        # Update session
        await self.session_manager.update_session(session)
        
        return session
```

### 7. Session-Based Service Configurator

A service configurator that customizes service behavior based on session data:

```python
class SessionServiceConfigurator:
    """
    Session-based service configurator.
    
    Customizes service behavior based on session data.
    """
    
    def __init__(
        self,
        session_manager: SessionManager,
        dependency_container: SmartDependencyContainer
    ):
        """
        Initialize configurator.
        
        Args:
            session_manager: Session manager
            dependency_container: Dependency container
        """
        self.session_manager = session_manager
        self.dependency_container = dependency_container
    
    async def configure_service(
        self,
        service: ContextAwareService,
        context: ExecutionContext
    ) -> ContextAwareService:
        """
        Configure service based on session.
        
        Args:
            service: Service to configure
            context: Execution context
            
        Returns:
            Configured service
        """
        if not context.session_id:
            # No session, return service as is
            return service
        
        # Get session
        session = await self.session_manager.get_session(context.session_id)
        
        if not session:
            # No session found, return service as is
            return service
        
        # Create service with context
        contextualized_service = await service.with_context(context)
        
        # Apply session-specific configuration
        if "service_config" in session.state:
            config = session.state["service_config"]
            
            if isinstance(config, dict) and service.__class__.__name__ in config:
                # Get service-specific configuration
                service_config = config[service.__class__.__name__]
                
                # Apply configuration to service
                if hasattr(contextualized_service, "configure") and callable(contextualized_service.configure):
                    contextualized_service.configure(service_config)
        
        return contextualized_service
```

## Usage Examples

### 1. Basic Session Usage in FastAPI

```python
from fastapi import FastAPI, Request, Depends

app = FastAPI()

# Create session manager
session_store = MemorySessionStore()
session_manager = SessionManager(session_store)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    session_manager=session_manager,
    cookie_name="session_id",
    cookie_max_age=3600,
    cookie_secure=False,
    cookie_httponly=True
)

# Start session manager
@app.on_event("startup")
async def startup():
    await session_manager.start()

# Stop session manager
@app.on_event("shutdown")
async def shutdown():
    await session_manager.stop()

# Session dependency
async def get_session(request: Request):
    if hasattr(request.state, "session"):
        return request.state.session
    return None

# Endpoint with session
@app.get("/api/user/preferences")
async def get_preferences(session: Session = Depends(get_session)):
    if not session:
        return {"preferences": {}}
    
    return {"preferences": session.preferences}

# Update preferences endpoint
@app.post("/api/user/preferences")
async def update_preferences(
    preferences: Dict[str, Any],
    session: Session = Depends(get_session)
):
    if not session:
        return {"error": "No session"}
    
    # Update preferences
    session.preferences.update(preferences)
    
    # Update session
    await session_manager.update_session(session)
    
    return {"status": "success", "preferences": session.preferences}
```

### 2. Session Integration with Tool Execution

```python
from pydantic_ai_integration.tool_decorator import tool

@tool(name="get_user_preferences")
async def get_user_preferences(ctx: ExecutionContext):
    """Get user preferences from session."""
    if not ctx.session_id:
        return {"preferences": {}}
    
    # Get session manager
    session_manager = ctx.get_property("session_manager")
    
    if not session_manager:
        return {"error": "Session manager not available"}
    
    # Get session
    session = await session_manager.get_session(ctx.session_id)
    
    if not session:
        return {"preferences": {}}
    
    return {"preferences": session.preferences}

@tool(name="update_user_preferences")
async def update_user_preferences(ctx: ExecutionContext, preferences: Dict[str, Any]):
    """Update user preferences in session."""
    if not ctx.session_id:
        return {"error": "No session"}
    
    # Get session manager
    session_manager = ctx.get_property("session_manager")
    
    if not session_manager:
        return {"error": "Session manager not available"}
    
    # Get session
    session = await session_manager.get_session(ctx.session_id)
    
    if not session:
        return {"error": "Session not found"}
    
    # Update preferences
    session.preferences.update(preferences)
    
    # Update session
    await session_manager.update_session(session)
    
    return {"status": "success", "preferences": session.preferences}
```

### 3. Session-Aware Service Configuration

```python
@service(name="recommendations")
class RecommendationService(ContextAwareService):
    """Service for providing recommendations."""
    
    def __init__(
        self,
        dependency_container: SmartDependencyContainer = None,
        default_algorithm: str = "collaborative"
    ):
        """Initialize service."""
        super().__init__(dependency_container)
        self.default_algorithm = default_algorithm
        self.algorithm = default_algorithm
        self.personalization_enabled = True
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure service."""
        if "algorithm" in config:
            self.algorithm = config["algorithm"]
        
        if "personalization_enabled" in config:
            self.personalization_enabled = config["personalization_enabled"]
    
    async def get_recommendations(
        self,
        user_id: str,
        item_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations for a user.
        
        Args:
            user_id: User ID
            item_id: Optional item ID for similar items
            limit: Maximum number of recommendations
            
        Returns:
            List of recommendations
        """
        # Get context
        context = getattr(self, "_context", None)
        session_id = context.session_id if context else None
        
        # Determine algorithm based on configuration
        algorithm = self.algorithm
        personalization = self.personalization_enabled
        
        # Get recommendations using the selected algorithm
        if algorithm == "collaborative":
            return await self._get_collaborative_recommendations(
                user_id, item_id, limit, session_id, personalization
            )
        elif algorithm == "content_based":
            return await self._get_content_based_recommendations(
                user_id, item_id, limit, session_id, personalization
            )
        else:
            return await self._get_default_recommendations(
                user_id, limit
            )
    
    async def _get_collaborative_recommendations(
        self,
        user_id: str,
        item_id: Optional[str],
        limit: int,
        session_id: Optional[str],
        personalization: bool
    ) -> List[Dict[str, Any]]:
        """Get collaborative filtering recommendations."""
        # Implementation details...
        pass
    
    async def _get_content_based_recommendations(
        self,
        user_id: str,
        item_id: Optional[str],
        limit: int,
        session_id: Optional[str],
        personalization: bool
    ) -> List[Dict[str, Any]]:
        """Get content-based recommendations."""
        # Implementation details...
        pass
    
    async def _get_default_recommendations(
        self,
        user_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get default recommendations."""
        # Implementation details...
        pass
```

## Implementation Strategy

### Phase 1: Core Session Components

1. Implement `Session` model with rich metadata
2. Create `SessionStore` interface
3. Implement `MemorySessionStore` for development
4. Develop `SessionManager` for lifecycle management

### Phase 2: Session Middleware

1. Implement `SessionMiddleware` for FastAPI
2. Add session dependency for API endpoints
3. Create session context integration
4. Add session manager lifecycle hooks

### Phase 3: Service Integration

1. Enhance `ExecutionContext` with session awareness
2. Implement `SessionContextProvider` for context enrichment
3. Create `SessionServiceConfigurator` for service customization
4. Update service discovery to use session configuration

### Phase 4: Advanced Storage

1. Implement `RedisSessionStore` for distributed sessions
2. Develop `DatabaseSessionStore` for persistent sessions
3. Add session migration utilities
4. Create session backup and restore functionality

### Phase 5: AI Integration

1. Add AI-specific session metadata
2. Implement session history analysis
3. Create personalization utilities
4. Add context-based recommendation system

## Conclusion

The enhanced session management architecture provides a robust foundation for context-aware services and AI integration. By unifying session handling across the system and integrating it with the execution pipeline, we can create more intelligent and adaptive services that respond to user needs.

The architecture supports various storage backends, rich metadata, and seamless integration with the execution context. This flexibility allows us to build sophisticated applications that maintain user state, preferences, and history across multiple interactions.

As we implement this architecture, we'll create a more cohesive system where services can adapt their behavior based on session context, leading to a more personalized and efficient user experience.