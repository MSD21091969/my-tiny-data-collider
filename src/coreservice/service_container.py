"""
Service Container and Dependency Injection for MDS Services.

This module provides centralized service management following DRY principles
and enabling proper dependency injection for testing and maintainability.
"""

import logging
from typing import Any

from casefileservice.repository import CasefileRepository
from casefileservice.service import CasefileService
from communicationservice.repository import ChatSessionRepository
from communicationservice.service import CommunicationService
from coreservice.id_service import get_id_service
from tool_sessionservice.repository import ToolSessionRepository
from tool_sessionservice.service import ToolSessionService

logger = logging.getLogger(__name__)


class ServiceContainer:
    """
    Centralized container for service registration and dependency injection.

    Provides DRY service instantiation with proper dependency management.
    Services are lazily instantiated and cached for reuse.
    """

    def __init__(self) -> None:
        """Initialize the service container."""
        self._services: dict[str, Any] = {}
        self._service_factories: dict[str, callable] = {}
        self._repositories: dict[str, Any] = {}

        # Register core services
        self._register_core_services()

    def _register_core_services(self) -> None:
        """Register all core services with their dependencies."""

        # Register repositories (leaf dependencies)
        self._service_factories['casefile_repository'] = lambda: CasefileRepository()
        self._service_factories['tool_session_repository'] = lambda: ToolSessionRepository()
        self._service_factories['chat_session_repository'] = lambda: ChatSessionRepository()
        self._service_factories['id_service'] = lambda: get_id_service()

        # Register services with dependencies
        self._service_factories['casefile_service'] = lambda: CasefileService(
            repository=self.get_service('casefile_repository')
        )
        self._service_factories['tool_session_service'] = lambda: ToolSessionService(
            repository=self.get_service('tool_session_repository'),
            id_service=self.get_service('id_service')
        )
        self._service_factories['communication_service'] = lambda: CommunicationService(
            repository=self.get_service('chat_session_repository'),
            tool_service=self.get_service('tool_session_service'),
            id_service=self.get_service('id_service')
        )

    def get_service(self, service_name: str) -> Any:
        """
        Get a service instance by name, creating it if necessary.

        Args:
            service_name: Name of the service to retrieve

        Returns:
            Service instance

        Raises:
            ValueError: If service is not registered
        """
        if service_name not in self._services:
            if service_name not in self._service_factories:
                raise ValueError(f"Service '{service_name}' is not registered")

            logger.debug(f"Creating service instance: {service_name}")
            self._services[service_name] = self._service_factories[service_name]()

        return self._services[service_name]

    def register_service(self, service_name: str, factory: callable) -> None:
        """
        Register a service factory function.

        Args:
            service_name: Name of the service
            factory: Factory function that creates the service
        """
        self._service_factories[service_name] = factory
        # Clear cached instance if it exists
        if service_name in self._services:
            del self._services[service_name]

    def has_service(self, service_name: str) -> bool:
        """
        Check if a service is registered.

        Args:
            service_name: Name of the service

        Returns:
            True if service is registered
        """
        return service_name in self._service_factories

    def clear_cache(self) -> None:
        """Clear all cached service instances."""
        self._services.clear()

    def get_registered_services(self) -> list[str]:
        """
        Get list of all registered service names.

        Returns:
            List of service names
        """
        return list(self._service_factories.keys())


class ServiceManager:
    """
    High-level service manager providing grouped access to related services.

    Groups services by domain and provides clean separation of concerns
    while maintaining centralized management.
    """

    def __init__(self, container: ServiceContainer | None = None) -> None:
        """
        Initialize the service manager.

        Args:
            container: Service container to use, creates default if None
        """
        self.container = container or ServiceContainer()

    @property
    def casefile_service(self) -> CasefileService:
        """Get the casefile service."""
        return self.container.get_service('casefile_service')

    @property
    def tool_session_service(self) -> ToolSessionService:
        """Get the tool session service."""
        return self.container.get_service('tool_session_service')

    @property
    def communication_service(self) -> CommunicationService:
        """Get the communication service."""
        return self.container.get_service('communication_service')

    @property
    def id_service(self):
        """Get the ID service."""
        return self.container.get_service('id_service')

    def get_service(self, service_name: str) -> Any:
        """
        Get any service by name.

        Args:
            service_name: Name of the service

        Returns:
            Service instance
        """
        return self.container.get_service(service_name)


# Global service locator for backward compatibility and convenience
_service_manager: ServiceManager | None = None


def get_service_manager() -> ServiceManager:
    """
    Get the global service manager instance.

    Creates default instance if not set.

    Returns:
        Global service manager
    """
    global _service_manager
    if _service_manager is None:
        _service_manager = ServiceManager()
    return _service_manager


def set_service_manager(manager: ServiceManager) -> None:
    """
    Set the global service manager instance.

    Args:
        manager: Service manager to set as global
    """
    global _service_manager
    _service_manager = manager


def reset_service_manager() -> None:
    """Reset the global service manager to None."""
    global _service_manager
    _service_manager = None