"""
Base infrastructure models for the pydantic_models layer.

This package contains the fundamental building blocks used across all domain models:
- envelopes.py: Request/response wrapper models (BaseRequest, BaseResponse, RequestEnvelope)
- types.py: Common enums and types (RequestStatus, etc.)

These models provide the infrastructure for type-safe operations throughout the system.
"""

from .envelopes import BaseRequest, BaseResponse, RequestEnvelope
from .types import RequestStatus

__all__ = [
    "BaseRequest",
    "BaseResponse",
    "RequestEnvelope",
    "RequestStatus",
]
