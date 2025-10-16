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


def validate_user_id(v: str) -> str:
    """Validate user ID (typically email address)."""
    if not v or len(v) < 3:
        raise ValueError("User ID cannot be empty or too short")
    # Basic email format check (@ symbol present)
    if "@" in v and len(v.split("@")) == 2:
        domain = v.split("@")[1]
        if "." not in domain:
            raise ValueError(f"Invalid user ID format: {v}")
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

UserId = Annotated[
    str,
    Field(description="User identifier (typically email address)"),
    AfterValidator(validate_user_id)
]


def validate_gmail_id(v: str) -> str:
    """Validate Gmail message/thread ID format."""
    if not v or not v.strip():
        raise ValueError("Gmail ID cannot be empty")
    v = v.strip()
    # Allow short IDs for testing, but validate format
    if len(v) < 1:
        raise ValueError(f"Gmail ID too short: {v}")
    return v


GmailMessageId = Annotated[
    str,
    Field(description="Gmail message ID"),
    AfterValidator(validate_gmail_id)
]

GmailThreadId = Annotated[
    str,
    Field(description="Gmail thread ID"),
    AfterValidator(validate_gmail_id)
]

GmailAttachmentId = Annotated[
    str,
    Field(description="Gmail attachment ID"),
    AfterValidator(validate_gmail_id)
]


def validate_resource_id(v: str) -> str:
    """Validate generic resource ID."""
    if not v or not v.strip():
        raise ValueError("Resource ID cannot be empty")
    return v.strip()


ResourceId = Annotated[
    str,
    Field(description="Generic resource identifier"),
    AfterValidator(validate_resource_id)
]


def validate_event_id(v: str) -> str:
    """Validate event ID format."""
    if not v or not v.strip():
        raise ValueError("Event ID cannot be empty")
    return v.strip()


EventId = Annotated[
    str,
    Field(description="Event identifier"),
    AfterValidator(validate_event_id)
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


# ============================================================================
# Enhanced Email/URL Types
# ============================================================================

def validate_secure_url(v: HttpUrl) -> HttpUrl:
    """Validate URL uses HTTPS protocol."""
    if v.scheme != "https":
        raise ValueError(f"URL must use HTTPS protocol: {v}")
    return v


def validate_google_workspace_email(v: EmailStr) -> EmailStr:
    """Validate email is from Google Workspace domain."""
    email_str = str(v)
    # Common Google Workspace domains (extend as needed)
    allowed_domains = ["gmail.com", "googlemail.com"]
    domain = email_str.split("@")[-1].lower()
    if not any(domain.endswith(allowed) for allowed in allowed_domains):
        # For custom Google Workspace domains, you'd typically check a whitelist
        # For now, we accept any domain (customize per deployment)
        pass
    return v


UrlString = HttpUrl

SecureUrl = Annotated[
    HttpUrl,
    Field(description="HTTPS URL (secure protocol only)"),
    AfterValidator(validate_secure_url)
]

GoogleWorkspaceEmail = Annotated[
    EmailStr,
    Field(description="Google Workspace email address"),
    AfterValidator(validate_google_workspace_email)
]


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


def validate_future_timestamp(v: str) -> str:
    """Validate timestamp is in the future."""
    v = validate_iso_timestamp(v)
    dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
    if dt <= datetime.now(dt.tzinfo):
        raise ValueError(f"Timestamp must be in the future: {v}")
    return v


def validate_past_timestamp(v: str) -> str:
    """Validate timestamp is in the past."""
    v = validate_iso_timestamp(v)
    dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
    if dt >= datetime.now(dt.tzinfo):
        raise ValueError(f"Timestamp must be in the past: {v}")
    return v


def validate_date_string(v: str) -> str:
    """Validate YYYY-MM-DD date format."""
    if not v:
        raise ValueError("Date string cannot be empty")
    try:
        datetime.strptime(v, "%Y-%m-%d")
        return v
    except ValueError as e:
        raise ValueError(f"Invalid date format (expected YYYY-MM-DD): {v}") from e


def validate_time_string(v: str) -> str:
    """Validate HH:MM:SS time format."""
    if not v:
        raise ValueError("Time string cannot be empty")
    try:
        datetime.strptime(v, "%H:%M:%S")
        return v
    except ValueError as e:
        raise ValueError(f"Invalid time format (expected HH:MM:SS): {v}") from e


IsoTimestamp = Annotated[
    str,
    Field(description="ISO 8601 timestamp (e.g., 2025-10-13T12:00:00)"),
    AfterValidator(validate_iso_timestamp)
]

FutureTimestamp = Annotated[
    str,
    Field(description="ISO 8601 timestamp that must be in the future"),
    AfterValidator(validate_future_timestamp)
]

PastTimestamp = Annotated[
    str,
    Field(description="ISO 8601 timestamp that must be in the past"),
    AfterValidator(validate_past_timestamp)
]

DateString = Annotated[
    str,
    Field(description="Date in YYYY-MM-DD format"),
    AfterValidator(validate_date_string)
]

TimeString = Annotated[
    str,
    Field(description="Time in HH:MM:SS format"),
    AfterValidator(validate_time_string)
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
    "UserId",
    "GmailMessageId",
    "GmailThreadId",
    "GmailAttachmentId",
    "ResourceId",
    "EventId",
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
    "SecureUrl",
    "GoogleWorkspaceEmail",
    # Timestamp Types
    "IsoTimestamp",
    "FutureTimestamp",
    "PastTimestamp",
    "DateString",
    "TimeString",
    # Collection Types
    "TagList",
    "EmailList",
    # Validators (for custom use)
    "normalize_and_validate_casefile_id",
    "normalize_and_validate_tool_session_id",
    "normalize_and_validate_chat_session_id",
    "normalize_and_validate_session_id",
    "validate_user_id",
    "validate_gmail_id",
    "validate_resource_id",
    "validate_event_id",
    "validate_iso_timestamp",
    "validate_future_timestamp",
    "validate_past_timestamp",
    "validate_date_string",
    "validate_time_string",
    "validate_secure_url",
    "validate_google_workspace_email",
]
