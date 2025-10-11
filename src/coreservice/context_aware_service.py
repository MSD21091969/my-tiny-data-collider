"""
Context-Aware Services for MDS Architecture.

This module provides the ContextAwareService base class that enables services to:
- Manage execution context across service calls
- Propagate context information (user, session, request IDs)
- Implement cross-cutting concerns (logging, metrics, tracing)
- Integrate with service registry for context-aware discovery
"""

import logging
import time
from abc import ABC, abstractmethod
from contextvars import ContextVar
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ServiceContext(BaseModel):
    """
    Context model for service operations.

    Contains all the contextual information needed for service execution,
    including user identity, session info, request tracing, and metadata.
    """

    # Request identification
    request_id: UUID = Field(default_factory=uuid4, description="Unique request identifier")
    correlation_id: Optional[UUID] = Field(None, description="Correlation ID for distributed tracing")

    # User and session information
    user_id: Optional[str] = Field(None, description="Authenticated user ID")
    session_id: Optional[str] = Field(None, description="User session ID")
    tenant_id: Optional[str] = Field(None, description="Multi-tenant identifier")

    # Service information
    service_name: str = Field(..., description="Name of the executing service")
    service_version: str = Field(..., description="Version of the executing service")
    operation: str = Field(..., description="Current operation being performed")

    # Timing and performance
    start_time: float = Field(default_factory=time.time, description="Operation start timestamp")
    timeout: Optional[float] = Field(None, description="Operation timeout in seconds")

    # Metadata and tags
    tags: Dict[str, str] = Field(default_factory=dict, description="Context tags for categorization")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")

    # Parent context for nested calls
    parent_context: Optional["ServiceContext"] = Field(None, description="Parent context for nested operations")

    def get_elapsed_time(self) -> float:
        """Get elapsed time since context creation."""
        return time.time() - self.start_time

    def is_expired(self) -> bool:
        """Check if the context has exceeded its timeout."""
        if self.timeout is None:
            return False
        return self.get_elapsed_time() > self.timeout

    def create_child_context(self, operation: str, **kwargs) -> "ServiceContext":
        """Create a child context for nested operations."""
        child_data = self.model_dump()
        child_data.update(kwargs)
        child_data["operation"] = operation
        child_data["parent_context"] = self
        child_data["start_time"] = time.time()

        return ServiceContext(**child_data)

    def get_trace_path(self) -> list[str]:
        """Get the execution trace path."""
        path = [f"{self.service_name}:{self.operation}"]
        if self.parent_context:
            path = self.parent_context.get_trace_path() + path
        return path


# Context variable for current service context
_current_context: ContextVar[Optional[ServiceContext]] = ContextVar('current_context', default=None)


class ContextProvider(ABC):
    """Abstract base class for context providers."""

    @abstractmethod
    async def enrich_context(self, context: ServiceContext) -> ServiceContext:
        """Enrich the service context with additional information."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of this context provider."""
        pass


class UserContextProvider(ContextProvider):
    """Context provider for user information."""

    def get_provider_name(self) -> str:
        return "user_provider"

    async def enrich_context(self, context: ServiceContext) -> ServiceContext:
        """Enrich context with user information from authentication."""
        # This would typically get user info from JWT token, session, etc.
        # For now, we'll add some basic user context if available
        if not context.user_id:
            # Try to get from environment or headers (placeholder)
            context.user_id = context.metadata.get("user_id")

        return context


class SessionContextProvider(ContextProvider):
    """Context provider for session information."""

    def get_provider_name(self) -> str:
        return "session_provider"

    async def enrich_context(self, context: ServiceContext) -> ServiceContext:
        """Enrich context with session information."""
        if not context.session_id:
            # Try to get from context metadata
            context.session_id = context.metadata.get("session_id")

        return context


class RequestContextProvider(ContextProvider):
    """Context provider for request information."""

    def get_provider_name(self) -> str:
        return "request_provider"

    async def enrich_context(self, context: ServiceContext) -> ServiceContext:
        """Enrich context with request information."""
        # Add request-specific metadata
        if "user_agent" not in context.metadata:
            context.metadata["user_agent"] = "unknown"

        if "client_ip" not in context.metadata:
            context.metadata["client_ip"] = "unknown"

        return context


class ContextAwareService(ABC):
    """
    Base class for context-aware services.

    Provides context management, lifecycle hooks, and cross-cutting concerns
    integration for all MDS services.
    """

    def __init__(self, service_name: str, service_version: str = "1.0.0"):
        """Initialize the context-aware service."""
        self.service_name = service_name
        self.service_version = service_version
        self._context_providers: list[ContextProvider] = []
        self._metrics_collector = None
        self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

        # Register default context providers
        self._register_default_providers()

    def _register_default_providers(self) -> None:
        """Register default context providers."""
        self.register_context_provider(UserContextProvider())
        self.register_context_provider(SessionContextProvider())
        self.register_context_provider(RequestContextProvider())

    def register_context_provider(self, provider: ContextProvider) -> None:
        """Register a context provider."""
        self._context_providers.append(provider)
        self._logger.debug(f"Registered context provider: {provider.get_provider_name()}")

    async def _enrich_context(self, context: ServiceContext) -> ServiceContext:
        """Enrich the context using all registered providers."""
        for provider in self._context_providers:
            try:
                context = await provider.enrich_context(context)
            except Exception as e:
                self._logger.warning(f"Context provider {provider.get_provider_name()} failed: {e}")

        return context

    async def execute_with_context(
        self,
        operation: str,
        operation_func,
        *args,
        context: Optional[ServiceContext] = None,
        **kwargs
    ) -> Any:
        """
        Execute an operation with full context management.

        Args:
            operation: Name of the operation being performed
            operation_func: The async function to execute
            context: Optional existing context (will create new if None)
            *args: Arguments to pass to the operation function
            **kwargs: Keyword arguments to pass to the operation function

        Returns:
            Result of the operation function
        """
        # Create or inherit context
        if context is None:
            context = ServiceContext(
                service_name=self.service_name,
                service_version=self.service_version,
                operation=operation
            )
        else:
            context = context.create_child_context(operation)

        # Enrich context
        context = await self._enrich_context(context)

        # Set context in context variable
        token = _current_context.set(context)

        try:
            # Pre-execution hook
            await self._pre_execute_hook(context)

            # Execute operation with timing
            start_time = time.time()
            result = await operation_func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Post-execution hook
            await self._post_execute_hook(context, result, execution_time, None)

            # Record metrics
            await self._record_metrics(context, execution_time, success=True)

            return result

        except Exception as e:
            execution_time = time.time() - context.start_time

            # Error hook
            await self._error_hook(context, e, execution_time)

            # Record error metrics
            await self._record_metrics(context, execution_time, success=False, error=e)

            raise

        finally:
            # Restore previous context
            _current_context.reset(token)

    async def _pre_execute_hook(self, context: ServiceContext) -> None:
        """Hook called before operation execution."""
        self._logger.info(
            f"Starting operation: {context.operation}",
            extra={
                "request_id": str(context.request_id),
                "correlation_id": str(context.correlation_id) if context.correlation_id else None,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "service": context.service_name,
                "operation": context.operation,
                "trace_path": " -> ".join(context.get_trace_path())
            }
        )

    async def _post_execute_hook(
        self,
        context: ServiceContext,
        result: Any,
        execution_time: float,
        error: Optional[Exception]
    ) -> None:
        """Hook called after successful operation execution."""
        self._logger.info(
            f"Completed operation: {context.operation} in {execution_time:.3f}s",
            extra={
                "request_id": str(context.request_id),
                "execution_time": execution_time,
                "success": True
            }
        )

    async def _error_hook(
        self,
        context: ServiceContext,
        error: Exception,
        execution_time: float
    ) -> None:
        """Hook called when operation fails."""
        self._logger.error(
            f"Operation failed: {context.operation} after {execution_time:.3f}s - {str(error)}",
            extra={
                "request_id": str(context.request_id),
                "execution_time": execution_time,
                "error_type": type(error).__name__,
                "success": False
            },
            exc_info=True
        )

    @abstractmethod
    async def _record_metrics(
        self,
        context: ServiceContext,
        execution_time: float,
        success: bool,
        error: Optional[Exception] = None
    ) -> None:
        """Record operation metrics."""
        pass

    @staticmethod
    def get_current_context() -> Optional[ServiceContext]:
        """Get the current service context."""
        return _current_context.get()

    async def call_service_with_context(
        self,
        service_name: str,
        operation: str,
        service_call_func,
        *args,
        **kwargs
    ) -> Any:
        """
        Call another service while propagating context.

        Args:
            service_name: Name of the service being called
            operation: Operation being performed on the service
            service_call_func: The service call function
            *args: Arguments for the service call
            **kwargs: Keyword arguments for the service call

        Returns:
            Result from the service call
        """
        current_context = self.get_current_context()

        if current_context:
            # Create child context for the service call
            service_context = current_context.create_child_context(
                f"call_{service_name}_{operation}",
                service_name=service_name,
                operation=operation
            )

            # Add service call metadata
            service_context.metadata["called_service"] = service_name
            service_context.metadata["called_operation"] = operation

            # Execute with context
            return await self.execute_with_context(
                f"call_{service_name}",
                service_call_func,
                *args,
                context=service_context,
                **kwargs
            )
        else:
            # No current context, execute normally
            return await service_call_func(*args, **kwargs)


def get_current_service_context() -> Optional[ServiceContext]:
    """Global function to get the current service context."""
    return _current_context.get()


def create_service_context(
    service_name: str,
    operation: str,
    service_version: str = "1.0.0",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    correlation_id: Optional[UUID] = None,
    **metadata
) -> ServiceContext:
    """Create a new service context."""
    return ServiceContext(
        service_name=service_name,
        service_version=service_version,
        operation=operation,
        user_id=user_id,
        session_id=session_id,
        correlation_id=correlation_id,
        metadata=metadata
    )