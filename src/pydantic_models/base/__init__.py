"""
Base infrastructure models for the pydantic_models layer.

This package contains the fundamental building blocks used across all domain models:
- envelopes.py: Request/response wrapper models (BaseRequest, BaseResponse, RequestEnvelope)
- types.py: Common enums and types (RequestStatus, etc.)
- custom_types.py: Reusable Annotated types with validation (CasefileId, PositiveInt, etc.)
- validators.py: Reusable validation functions (validate_timestamp_order, etc.)

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
from .validators import (
    validate_timestamp_order,
    validate_at_least_one,
    validate_mutually_exclusive,
    validate_conditional_required,
    validate_list_not_empty,
    validate_list_unique,
    validate_range,
    validate_string_length,
    validate_depends_on,
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
    # Validators
    "validate_timestamp_order",
    "validate_at_least_one",
    "validate_mutually_exclusive",
    "validate_conditional_required",
    "validate_list_not_empty",
    "validate_list_unique",
    "validate_range",
    "validate_string_length",
    "validate_depends_on",
]
