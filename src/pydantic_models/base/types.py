"""
Common types and enums used across all models.

This module contains shared type definitions that are used throughout the domain models:
- RequestStatus: Status enum for request/response lifecycle
- Additional common types as needed
"""

from enum import Enum


class RequestStatus(str, Enum):
    """Status of a request."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
