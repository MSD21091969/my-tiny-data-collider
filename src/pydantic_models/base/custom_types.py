"""
Custom reusable types for Pydantic models.

This module provides Annotated types with built-in validation constraints
to ensure consistency across all models and reduce code duplication.

Usage:
    from src.pydantic_models.base.custom_types import CasefileId, PositiveInt
    
    class MyModel(BaseModel):
        casefile_id: CasefileId  # Automatically validated with regex pattern
        count: PositiveInt       # Automatically validated >= 1
"""

from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, Field, EmailStr, HttpUrl


# ============================================================================
# ID Types with Validation Patterns
# ============================================================================

def normalize_and_validate_casefile_id(v: str) -> str:
    """Normalize and validate casefile ID format: cf_YYMMDD_code."""
    v = v.lower() if isinstance(v, str) else v
    if not v.startswith("cf_"):
        raise ValueError("Casefile ID must start with 'cf_'")
    parts = v.split("_")
    if len(parts) < 3:
        raise ValueError("Casefile ID format: cf_YYMMDD_code")
    # Validate date part is numeric
    if not parts[1].isdigit() or len(parts[1]) != 6:
        raise ValueError("Casefile ID date part must be 6 digits (YYMMDD)")
    return v


def normalize_and_validate_tool_session_id(v: str) -> str:
    """Normalize and validate tool session ID format: ts_XXX."""
    v = v.lower() if isinstance(v, str) else v
    if not v.startswith("ts_"):
        raise ValueError("Tool session ID must start with 'ts_'")
    return v


def normalize_and_validate_chat_session_id(v: str) -> str:
    """Normalize and validate chat session ID format: cs_XXX."""
    v = v.lower() if isinstance(v, str) else v
    if not v.startswith("cs_"):
        raise ValueError("Chat session ID must start with 'cs_'")
    return v


def normalize_and_validate_session_id(v: str) -> str:
    """Normalize and validate session ID (tool or chat)."""
    v = v.lower() if isinstance(v, str) else v
    if not (v.startswith("ts_") or v.startswith("cs_")):
        raise ValueError("Session ID must start with 'ts_' or 'cs_'")
    return v


CasefileId = Annotated[
    str,
    Field(description="Casefile ID in format cf_YYMMDD_code"),
    BeforeValidator(normalize_and_validate_casefile_id)
]

ToolSessionId = Annotated[
    str,
    Field(description="Tool session ID in format ts_XXX"),
    BeforeValidator(normalize_and_validate_tool_session_id)
]

ChatSessionId = Annotated[
    str,
    Field(description="Chat session ID in format cs_XXX"),
    BeforeValidator(normalize_and_validate_chat_session_id)
]

SessionId = Annotated[
    str,
    Field(description="Session ID (tool or chat) in format ts_XXX or cs_XXX"),
    BeforeValidator(normalize_and_validate_session_id)
]


# ============================================================================
# Constrained Numeric Types
# ============================================================================

PositiveInt = Annotated[
    int,
    Field(gt=0, description="Positive integer (greater than 0)")
]

NonNegativeInt = Annotated[
    int,
    Field(ge=0, description="Non-negative integer (greater than or equal to 0)")
]

PositiveFloat = Annotated[
    float,
    Field(gt=0.0, description="Positive float (greater than 0.0)")
]

NonNegativeFloat = Annotated[
    float,
    Field(ge=0.0, description="Non-negative float (greater than or equal to 0.0)")
]

Percentage = Annotated[
    float,
    Field(ge=0.0, le=100.0, description="Percentage value between 0.0 and 100.0")
]

FileSizeBytes = Annotated[
    int,
    Field(ge=0, description="File size in bytes")
]


# ============================================================================
# Constrained String Types
# ============================================================================

NonEmptyString = Annotated[
    str,
    Field(min_length=1, description="Non-empty string")
]

ShortString = Annotated[
    str,
    Field(min_length=1, max_length=200, description="Short string (1-200 characters)")
]

MediumString = Annotated[
    str,
    Field(min_length=1, max_length=2000, description="Medium string (1-2000 characters)")
]

LongString = Annotated[
    str,
    Field(min_length=1, max_length=5000, description="Long string (1-5000 characters)")
]

EmailAddress = EmailStr

UrlString = HttpUrl


# ============================================================================
# Timestamp Types
# ============================================================================

def validate_iso_timestamp(v: str) -> str:
    """Validate and normalize ISO 8601 timestamp."""
    if not v:
        raise ValueError("Timestamp cannot be empty")
    try:
        # Parse and re-format to ensure valid ISO 8601
        dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
        return dt.isoformat()
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Invalid ISO 8601 timestamp: {v}") from e


IsoTimestamp = Annotated[
    str,
    Field(description="ISO 8601 timestamp (e.g., 2025-10-13T12:00:00)"),
    AfterValidator(validate_iso_timestamp)
]


# ============================================================================
# Collection Types
# ============================================================================

TagList = Annotated[
    list[str],
    Field(description="List of tags for categorization")
]

EmailList = Annotated[
    list[EmailStr],
    Field(description="List of email addresses")
]


# ============================================================================
# Export all custom types
# ============================================================================

__all__ = [
    # ID Types
    "CasefileId",
    "ToolSessionId",
    "ChatSessionId",
    "SessionId",
    # Numeric Types
    "PositiveInt",
    "NonNegativeInt",
    "PositiveFloat",
    "NonNegativeFloat",
    "Percentage",
    "FileSizeBytes",
    # String Types
    "NonEmptyString",
    "ShortString",
    "MediumString",
    "LongString",
    "EmailAddress",
    "UrlString",
    # Timestamp Types
    "IsoTimestamp",
    # Collection Types
    "TagList",
    "EmailList",
    # Validators (for custom use)
    "normalize_and_validate_casefile_id",
    "normalize_and_validate_tool_session_id",
    "normalize_and_validate_chat_session_id",
    "validate_iso_timestamp",
]
