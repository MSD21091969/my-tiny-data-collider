"""
Base infrastructure models for the pydantic_models layer.

This package contains the fundamental building blocks used across all domain models:
- envelopes.py: Request/response wrapper models (BaseRequest, BaseResponse, RequestEnvelope)
- types.py: Common enums and types (RequestStatus, etc.)
- custom_types.py: Reusable Annotated types with validation (CasefileId, PositiveInt, etc.)

These models provide the infrastructure for type-safe operations throughout the system.
"""

from .envelopes import BaseRequest, BaseResponse, RequestEnvelope
from .types import RequestStatus
from .custom_types import (
    CasefileId,
    ToolSessionId,
    ChatSessionId,
    SessionId,
    PositiveInt,
    NonNegativeInt,
    PositiveFloat,
    NonNegativeFloat,
    Percentage,
    FileSizeBytes,
    NonEmptyString,
    ShortString,
    MediumString,
    LongString,
    EmailAddress,
    UrlString,
    IsoTimestamp,
    TagList,
    EmailList,
)

__all__ = [
    "BaseRequest",
    "BaseResponse",
    "RequestEnvelope",
    "RequestStatus",
    # Custom types
    "CasefileId",
    "ToolSessionId",
    "ChatSessionId",
    "SessionId",
    "PositiveInt",
    "NonNegativeInt",
    "PositiveFloat",
    "NonNegativeFloat",
    "Percentage",
    "FileSizeBytes",
    "NonEmptyString",
    "ShortString",
    "MediumString",
    "LongString",
    "EmailAddress",
    "UrlString",
    "IsoTimestamp",
    "TagList",
    "EmailList",
]
