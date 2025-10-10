# Service Architecture Refactoring Plan

## Overview

This document outlines the refactoring plan for the `/src` directory structure to better support tool engineering, AI integration, and context-aware session management. The goal is to create a modular, extensible architecture that can efficiently handle smart dependencies, context propagation, and adaptive service behavior.

## Current Architecture Limitations

The current service architecture has several limitations:

1. **Limited Context Awareness**: Services have minimal understanding of execution context
2. **Static Dependency Injection**: Dependencies are statically configured at startup
3. **Rigid Session Management**: Session data is not fully integrated with the execution flow
4. **Isolated Tool Execution**: Tools operate without shared contextual information
5. **Limited AI Integration Points**: Missing infrastructure for AI-driven behavior

## Refactoring Goals

1. **Context-Aware Service Layer**: Enhance services to adapt based on execution context
2. **Smart Dependency Resolution**: Create dynamic dependencies based on contextual needs
3. **Integrated Session Management**: Unify session handling across the execution pipeline
4. **Service Discovery & Registry**: Implement automatic service discovery and registration
5. **AI Integration Framework**: Establish patterns for AI service integration
6. **Metadata-Driven Architecture**: Use Pydantic models to describe and validate service behavior

## New Directory Structure

```
src/
├── pydantic_ai_integration/
│   ├── tool_decorator.py             # Tool registration and decoration
│   ├── execution/                    # Execution engine components
│   │   ├── context.py                # Enhanced execution context
│   │   ├── chain_executor.py         # Chain execution with context awareness
│   │   ├── resilience/               # Resilience patterns
│   │   └── types/                    # Execution types
│   ├── services/                     # Service layer
│   │   ├── registry.py               # Service discovery and registration
│   │   ├── factory.py                # Context-aware service factory
│   │   ├── context.py                # Service context propagation
│   │   ├── base.py                   # Base service class with context handling
│   │   ├── dependencies/             # Smart dependency resolution
│   │   │   ├── container.py          # Dynamic dependency container
│   │   │   ├── resolver.py           # Context-aware dependency resolver
│   │   │   └── providers/            # Dependency providers
│   │   ├── session/                  # Session management
│   │   │   ├── manager.py            # Session lifecycle manager
│   │   │   ├── store.py              # Session storage abstraction
│   │   │   └── middleware.py         # Session middleware
│   │   └── domain/                   # Domain-specific services
│   │       ├── data_processing/      # Data processing services
│   │       ├── integration/          # External integration services
│   │       └── ai/                   # AI-specific services
│   ├── models/                       # Pydantic models
│   │   ├── context.py                # Context models
│   │   ├── session.py                # Session models
│   │   ├── config.py                 # Configuration models
│   │   └── domain/                   # Domain-specific models
│   │       ├── tool_definitions.py   # Tool definition models
│   │       ├── requests.py           # Request models
│   │       └── responses.py          # Response models
│   └── utils/                        # Utility functions and helpers
│       ├── context.py                # Context utilities
│       ├── metadata.py               # Metadata extraction and handling
│       ├── reflection.py             # Reflection and introspection utilities
│       └── validation.py             # Enhanced validation utilities
└── api/                              # API layer
    ├── endpoints/                    # API endpoints
    ├── middleware/                   # API middleware
    ├── routers/                      # API routers
    ├── dependencies/                 # FastAPI dependencies
    └── models/                       # API-specific models
```

## Key Components

### 1. Enhanced Execution Context

The `ExecutionContext` class will be extended to include:

```python
class ExecutionContext(BaseModel):
    """
    Enhanced execution context with rich metadata support.
    
    Serves as the backbone for context propagation throughout the execution pipeline.
    """
    
    # Unique identifiers for tracing and correlation
    context_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_context_id: Optional[str] = None
    request_id: Optional[str] = None
    
    # User and session information
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Execution metadata
    tool_name: Optional[str] = None
    start_time: float = Field(default_factory=time.time)
    end_time: Optional[float] = None
    
    # Contextual properties that influence behavior
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    # AI-related context
    ai_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Tags for filtering and categorization
    tags: List[str] = Field(default_factory=list)
    
    # Security context
    security_context: Optional[Dict[str, Any]] = None
    
    # Tracking and metrics
    events: List[Dict[str, Any]] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    
    # Historical context for informed decisions
    history: List[Dict[str, Any]] = Field(default_factory=list)
    
    def track_event(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Track an event during execution."""
        self.events.append({
            "timestamp": time.time(),
            "event_type": event_type,
            "data": data or {}
        })
    
    def add_property(self, key: str, value: Any) -> None:
        """Add a contextual property."""
        self.properties[key] = value
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a contextual property."""
        return self.properties.get(key, default)
    
    def has_property(self, key: str) -> bool:
        """Check if a contextual property exists."""
        return key in self.properties
    
    def add_tag(self, tag: str) -> None:
        """Add a tag for filtering and categorization."""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if a tag exists."""
        return tag in self.tags
    
    def create_child_context(self, **kwargs) -> 'ExecutionContext':
        """Create a child context for nested execution."""
        child = ExecutionContext(
            parent_context_id=self.context_id,
            request_id=self.request_id,
            user_id=self.user_id,
            session_id=self.session_id,
            **kwargs
        )
        
        # Copy relevant properties to child context
        for key, value in self.properties.items():
            if key.startswith("inherited_"):
                child.properties[key] = value
        
        return child
    
    def complete(self) -> None:
        """Mark context as complete."""
        self.end_time = time.time()
    
    def duration(self) -> float:
        """Get execution duration."""
        end = self.end_time or time.time()
        return end - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "context_id": self.context_id,
            "parent_context_id": self.parent_context_id,
            "request_id": self.request_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "tool_name": self.tool_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration(),
            "properties": self.properties,
            "tags": self.tags,
            "events_count": len(self.events)
        }
```

### 2. Smart Dependency Container

The `SmartDependencyContainer` enables dynamic, context-aware dependency resolution:

```python
class DependencyProvider(Protocol):
    """Protocol for dependency providers."""
    
    def can_provide(self, dependency_type: Type, context: ExecutionContext) -> bool:
        """Determine if provider can provide dependency."""
        ...
    
    def provide(self, dependency_type: Type, context: ExecutionContext) -> Any:
        """Provide dependency instance."""
        ...


class SmartDependencyContainer:
    """
    Smart dependency container with context awareness.
    
    Resolves dependencies based on execution context, enabling
    dynamic service behavior.
    """
    
    def __init__(self):
        """Initialize container."""
        self.instances: Dict[str, Any] = {}
        self.factories: Dict[str, Callable[..., Any]] = {}
        self.providers: List[DependencyProvider] = []
        self.type_mappings: Dict[Type, Type] = {}
    
    def register_instance(self, key: str, instance: Any) -> None:
        """Register singleton instance."""
        self.instances[key] = instance
    
    def register_factory(self, key: str, factory: Callable[..., Any]) -> None:
        """Register factory function."""
        self.factories[key] = factory
    
    def register_provider(self, provider: DependencyProvider) -> None:
        """Register dependency provider."""
        self.providers.append(provider)
    
    def register_type_mapping(self, interface: Type, implementation: Type) -> None:
        """Register type mapping."""
        self.type_mappings[interface] = implementation
    
    def get(self, key: str, context: Optional[ExecutionContext] = None) -> Any:
        """Get dependency by key."""
        if key in self.instances:
            return self.instances[key]
        
        if key in self.factories:
            # Create instance with factory
            instance = self.factories[key](context)
            
            # Cache instance if not transient
            if not key.startswith("transient:"):
                self.instances[key] = instance
            
            return instance
        
        raise KeyError(f"Dependency '{key}' not registered")
    
    def resolve(self, dependency_type: Type, context: ExecutionContext) -> Any:
        """Resolve dependency by type."""
        # Check type mappings
        if dependency_type in self.type_mappings:
            # Resolve mapped type instead
            return self.resolve(self.type_mappings[dependency_type], context)
        
        # Try providers
        for provider in self.providers:
            if provider.can_provide(dependency_type, context):
                return provider.provide(dependency_type, context)
        
        # Try to instantiate directly
        try:
            return dependency_type()
        except Exception as e:
            raise DependencyResolutionError(
                f"Could not resolve dependency of type {dependency_type.__name__}",
                original_exception=e
            )
    
    def inject(self, func: Callable, context: ExecutionContext) -> Callable:
        """Create wrapper that injects dependencies."""
        sig = inspect.signature(func)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            injected_kwargs = {}
            
            for param_name, param in sig.parameters.items():
                # Skip if already provided
                if param_name in kwargs:
                    continue
                
                # Skip *args and **kwargs
                if param.kind == param.VAR_POSITIONAL or param.kind == param.VAR_KEYWORD:
                    continue
                
                # Get annotation or default to Any
                annotation = param.annotation if param.annotation is not inspect.Parameter.empty else Any
                
                # Skip if no annotation and no default
                if annotation is Any and param.default is inspect.Parameter.empty:
                    continue
                
                try:
                    # Try to resolve by type
                    injected_kwargs[param_name] = self.resolve(annotation, context)
                except DependencyResolutionError:
                    # If has default, skip
                    if param.default is not inspect.Parameter.empty:
                        continue
                    
                    # Re-raise
                    raise
            
            # Call function with injected dependencies
            return func(*args, **{**injected_kwargs, **kwargs})
        
        return wrapper
```

### 3. Session Management

The `SessionManager` provides unified session handling across the execution pipeline:

```python
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "last_accessed_at": self.last_accessed_at,
            "expiry_at": self.expiry_at,
            "state_keys": list(self.state.keys()),
            "preferences": self.preferences
        }


class SessionStore(ABC):
    """
    Abstract session store interface.
    
    Implementations provide storage for session data.
    """
    
    @abstractmethod
    async def get(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        pass
    
    @abstractmethod
    async def set(self, session: Session) -> None:
        """Save session."""
        pass
    
    @abstractmethod
    async def delete(self, session_id: str) -> None:
        """Delete session."""
        pass
    
    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Clean up expired sessions and return count."""
        pass


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
    
    async def cleanup_expired(self) -> int:
        """Clean up expired sessions and return count."""
        expired_ids = [
            sid for sid, session in self.sessions.items()
            if session.is_expired()
        ]
        
        for sid in expired_ids:
            await self.delete(sid)
        
        return len(expired_ids)


class SessionManager:
    """
    Session manager for lifecycle management.
    
    Handles session creation, retrieval, and expiration.
    """
    
    def __init__(
        self,
        store: SessionStore,
        session_lifetime: int = 3600,  # 1 hour default
        cleanup_interval: int = 300    # 5 minutes default
    ):
        """Initialize manager."""
        self.store = store
        self.session_lifetime = session_lifetime
        self.cleanup_interval = cleanup_interval
        self.last_cleanup: float = time.time()
    
    async def get_session(
        self,
        session_id: str,
        create_if_missing: bool = False
    ) -> Optional[Session]:
        """Get session by ID."""
        # Try to get existing session
        session = await self.store.get(session_id)
        
        if session:
            # Update last accessed time
            session.touch()
            await self.store.set(session)
            return session
        
        if create_if_missing:
            # Create new session
            return await self.create_session()
        
        return None
    
    async def create_session(self, user_id: Optional[str] = None) -> Session:
        """Create new session."""
        session = Session(
            user_id=user_id,
            expiry_at=time.time() + self.session_lifetime
        )
        
        await self.store.set(session)
        return session
    
    async def update_session(self, session: Session) -> None:
        """Update session."""
        session.touch()
        await self.store.set(session)
    
    async def delete_session(self, session_id: str) -> None:
        """Delete session."""
        await self.store.delete(session_id)
    
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
```

### 4. Context-Aware Service Base

The `ContextAwareService` base class enables services to adapt based on execution context:

```python
class ContextAwareService:
    """
    Base class for context-aware services.
    
    Provides context handling and dependency injection.
    """
    
    def __init__(self, dependency_container: SmartDependencyContainer = None):
        """Initialize service."""
        self.dependency_container = dependency_container or SmartDependencyContainer()
    
    async def with_context(self, context: ExecutionContext) -> 'ContextAwareService':
        """
        Create service instance with context.
        
        Creates a new instance with the provided context, allowing
        for contextual behavior.
        
        Args:
            context: Execution context
            
        Returns:
            New service instance with context
        """
        # Create new instance
        service = self.__class__(dependency_container=self.dependency_container)
        
        # Set context
        service._context = context
        
        # Initialize with context
        await service.initialize(context)
        
        return service
    
    async def initialize(self, context: ExecutionContext) -> None:
        """
        Initialize service with context.
        
        Override in subclasses to perform context-specific initialization.
        
        Args:
            context: Execution context
        """
        pass
    
    def inject(self, func: Callable) -> Callable:
        """
        Inject dependencies into function.
        
        Creates a wrapper that injects dependencies from the container.
        
        Args:
            func: Function to inject dependencies into
            
        Returns:
            Wrapper function with injected dependencies
        """
        if not hasattr(self, '_context'):
            raise ValueError("Service must have context before injection")
            
        return self.dependency_container.inject(func, self._context)
```

### 5. Metadata-Driven Models

Pydantic models with enhanced metadata support for AI integration:

```python
class AIMetadata(BaseModel):
    """
    Metadata for AI integration.
    
    Provides information for AI components to understand
    the purpose and behavior of a model.
    """
    
    description: str = ""
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    generated_by: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    priority: int = 0
    requires_context: bool = False
    provides_context: bool = False


class MetadataModel(BaseModel):
    """
    Base model with enhanced metadata.
    
    Provides rich metadata for reflection and AI integration.
    """
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }
        
        # Custom metadata
        metadata = {
            "ai": AIMetadata()
        }
    
    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """Get model metadata."""
        return cls.Config.metadata
    
    @classmethod
    def get_ai_metadata(cls) -> AIMetadata:
        """Get AI metadata."""
        return cls.Config.metadata.get("ai", AIMetadata())
    
    @classmethod
    def describe(cls) -> Dict[str, Any]:
        """
        Describe model schema with metadata.
        
        Returns a detailed description of the model schema,
        including field metadata.
        
        Returns:
            Model schema with metadata
        """
        schema = cls.schema()
        
        # Add metadata
        schema["metadata"] = cls.get_metadata()
        
        # Add field-level metadata
        for field_name, field in cls.__fields__.items():
            if "properties" in schema and field_name in schema["properties"]:
                schema["properties"][field_name]["metadata"] = field.field_info.extra
        
        return schema


class ToolParameter(MetadataModel):
    """
    Tool parameter model.
    
    Represents a parameter for a tool with rich metadata.
    """
    
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    format: Optional[str] = None
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    examples: List[Any] = Field(default_factory=list)


class ToolDefinition(MetadataModel):
    """
    Tool definition model.
    
    Represents a tool with rich metadata for AI integration.
    """
    
    name: str
    description: str
    parameters: Dict[str, ToolParameter] = Field(default_factory=dict)
    required_parameters: List[str] = Field(default_factory=list)
    returns: Dict[str, Any] = Field(default_factory=dict)
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    execution_type: str = "method_wrapper"
    implementation_config: Dict[str, Any] = Field(default_factory=dict)
    resilience: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        metadata = {
            "ai": AIMetadata(
                description="Defines a tool that can be executed by the system",
                requires_context=True,
                provides_context=True
            )
        }
```

## Implementation Strategy

### Phase 1: Core Framework

1. Implement enhanced `ExecutionContext` with rich metadata support
2. Create the `SmartDependencyContainer` for context-aware dependency resolution
3. Develop the `SessionManager` for unified session handling
4. Implement the `ContextAwareService` base class

### Phase 2: Service Architecture

1. Refactor existing services to use the `ContextAwareService` base class
2. Implement service discovery and registration
3. Create context providers for common dependencies
4. Add session integration to services

### Phase 3: Domain Models

1. Develop metadata-driven Pydantic models
2. Implement domain-specific models with AI metadata
3. Create validation utilities for enhanced model validation
4. Add contextual model transformation

### Phase 4: AI Integration

1. Create AI metadata extractors
2. Implement AI service integration points
3. Develop utilities for AI-driven behavior
4. Add AI-specific context providers

### Phase 5: Testing & Documentation

1. Create comprehensive test suite for new components
2. Update existing tests to use new architecture
3. Document new architecture and integration points
4. Create examples of AI-driven service behavior

## Migration Strategy

To minimize disruption, we'll follow this migration strategy:

1. Create new components alongside existing ones
2. Introduce adapters to bridge old and new architectures
3. Gradually migrate services to the new architecture
4. Update tools to use enhanced context and session management
5. Replace old components once migration is complete

## Expected Benefits

1. **Improved Context Awareness**: Services can adapt behavior based on execution context
2. **Dynamic Dependencies**: Smart dependency resolution based on context
3. **Unified Session Handling**: Consistent session management across the execution pipeline
4. **Enhanced AI Integration**: Clear integration points for AI-driven behavior
5. **Better Testability**: More modular architecture with clear boundaries
6. **Increased Developer Productivity**: Less boilerplate through metadata-driven patterns

## Conclusion

This refactoring plan will transform the `/src` directory into a modular, extensible architecture that supports context-aware services, smart dependencies, and AI integration. The enhanced execution context and session management will provide the foundation for more intelligent tool behavior, while the metadata-driven models will enable better AI integration.

By following this plan, we'll create a robust architecture that can adapt to changing requirements and support the upcoming tool engineering and AI initiatives.