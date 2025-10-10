"""
Canonical domain entity models.

This package contains the "source of truth" entities for the business domain:
- casefile.py: CasefileModel, CasefileMetadata, ResourceReference
- acl.py: CasefileACL, PermissionEntry, PermissionLevel
- tool_session.py: ToolSession, ToolEvent, AuthToken
- chat_session.py: ChatSession, MessageType

These are the core domain entities. For operations on these entities,
see pydantic_models.operations.
"""

# Casefile entities
# ACL entities
from .acl import CasefileACL, PermissionEntry, PermissionLevel
from .casefile import CasefileMetadata, CasefileModel, ResourceReference

# Chat session entities
from .chat_session import ChatSession, MessageType

# Tool session entities
from .tool_session import AuthToken, ToolEvent, ToolSession

__all__ = [
    # Casefile
    "CasefileModel",
    "CasefileMetadata",
    "ResourceReference",
    # ACL
    "CasefileACL",
    "PermissionEntry",
    "PermissionLevel",
    # Tool session
    "AuthToken",
    "ToolEvent",
    "ToolSession",
    # Chat session
    "MessageType",
    "ChatSession",
]
