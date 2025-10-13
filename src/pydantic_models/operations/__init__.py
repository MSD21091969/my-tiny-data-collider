"""
Operation models for domain entities.

This package contains request/response models for all domain operations:
- casefile_ops.py: Casefile CRUD and ACL operations
- tool_session_ops.py: Tool session lifecycle operations
- chat_session_ops.py: Chat session lifecycle operations
- tool_execution_ops.py: Tool and chat message execution operations

These are operation models that work with canonical entities.
For canonical entities, see pydantic_models.canonical
"""

from .casefile_ops import (
    CreateCasefileRequest,
    CreateCasefileResponse,
    CreateCasefilePayload,
    UpdateCasefileRequest,
    UpdateCasefileResponse,
    UpdateCasefilePayload,
    GetCasefileRequest,
    GetCasefileResponse,
    DeleteCasefileRequest,
    DeleteCasefileResponse,
    ListCasefilesRequest,
    ListCasefilesResponse,
)

__all__ = [
    "CreateCasefileRequest",
    "CreateCasefileResponse",
    "CreateCasefilePayload",
    "UpdateCasefileRequest",
    "UpdateCasefileResponse",
    "UpdateCasefilePayload",
    "GetCasefileRequest",
    "GetCasefileResponse",
    "DeleteCasefileRequest",
    "DeleteCasefileResponse",
    "ListCasefilesRequest",
    "ListCasefilesResponse",
]
