"""Model-to-model transformation utilities for RAR orchestration.

This module provides the foundation for explicit bidirectional transformations
between DTOs (Data Transfer Objects) and domain models in the Request-Action-Response
pipeline.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel

# Type variables for generic transformations
T = TypeVar('T', bound=BaseModel)  # Source model type
U = TypeVar('U', bound=BaseModel)  # Target model type


class BaseMapper[T, U](ABC):
    """Base class for bidirectional model transformations.

    Provides the contract for transforming between different model layers:
    - DTOs (Data Transfer Objects) ↔ Domain Models
    - Request Payloads ↔ Response Payloads
    - External APIs ↔ Internal Models

    Example:
        class CasefileMapper(BaseMapper[CreateCasefilePayload, CasefileModel]):
            @classmethod
            def to_domain(cls, payload): ...
            @classmethod
            def to_dto(cls, domain): ...
    """

    @classmethod
    @abstractmethod
    def to_domain(cls, dto: T) -> U:
        """Transform DTO to domain model.

        Args:
            dto: The source DTO model

        Returns:
            Domain model instance
        """
        pass

    @classmethod
    @abstractmethod
    def to_dto(cls, domain: U) -> T:
        """Transform domain model to DTO.

        Args:
            domain: The source domain model

        Returns:
            DTO model instance
        """
        pass


class TransformationError(Exception):
    """Raised when model transformation fails."""
    pass


class FieldMappingError(TransformationError):
    """Raised when field mapping between models fails."""
    pass


class ValidationError(TransformationError):
    """Raised when transformed model fails validation."""
    pass


# Utility functions for common transformations

def generate_id() -> str:
    """Generate a unique identifier for new entities."""
    return str(uuid.uuid4())


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.utcnow()


def safe_getattr(obj: BaseModel, field: str, default=None):
    """Safely get attribute from Pydantic model with default fallback."""
    return getattr(obj, field, default)


def transform_list(
    items: list[T],
    mapper_class: type[BaseMapper[T, U]],
    direction: str = "to_domain"
) -> list[U]:
    """Transform a list of models using the specified mapper.

    Args:
        items: List of source models
        mapper_class: Mapper class to use
        direction: "to_domain" or "to_dto"

    Returns:
        List of transformed models
    """
    if direction == "to_domain":
        return [mapper_class.to_domain(item) for item in items]
    elif direction == "to_dto":
        return [mapper_class.to_dto(item) for item in items]
    else:
        raise ValueError(f"Invalid direction: {direction}")


def create_transformation_chain(*mappers: type[BaseMapper]) -> callable:
    """Create a chain of transformations.

    Args:
        *mappers: Sequence of mapper classes to apply in order

    Returns:
        Function that applies the transformation chain
    """
    def transform_chain(input_model: BaseModel) -> BaseModel:
        result = input_model
        for mapper in mappers:
            if hasattr(mapper, 'to_domain'):
                result = mapper.to_domain(result)
            else:
                raise ValueError(f"Mapper {mapper} missing to_domain method")
        return result

    return transform_chain


# Registry for tracking available mappers
_mapper_registry: dict[str, type[BaseMapper]] = {}


def register_mapper(operation: str, mapper_class: type[BaseMapper]) -> None:
    """Register a mapper for an operation.

    Args:
        operation: Operation name (e.g., 'create_casefile')
        mapper_class: Mapper class to register
    """
    _mapper_registry[operation] = mapper_class


def get_mapper(operation: str) -> type[BaseMapper] | None:
    """Get registered mapper for an operation.

    Args:
        operation: Operation name

    Returns:
        Mapper class or None if not found
    """
    return _mapper_registry.get(operation)


def list_registered_mappers() -> dict[str, type[BaseMapper]]:
    """List all registered mappers.

    Returns:
        Dictionary of operation -> mapper_class
    """
    return _mapper_registry.copy()
