"""
Communication model package initialization.
"""

from .models import (
    MessageType,
    ChatMessagePayload,
    ChatResponsePayload,
    ChatRequest,
    ChatResponse,
    ChatSession,
)

from .session_models import (
    # Create Chat Session
    CreateChatSessionPayload,
    CreateChatSessionRequest,
    ChatSessionCreatedPayload,
    CreateChatSessionResponse,
    # Get Chat Session
    GetChatSessionPayload,
    GetChatSessionRequest,
    ChatSessionDataPayload,
    GetChatSessionResponse,
    # List Chat Sessions
    ListChatSessionsPayload,
    ListChatSessionsRequest,
    ChatSessionSummary,
    ChatSessionListPayload,
    ListChatSessionsResponse,
    # Close Chat Session
    CloseChatSessionPayload,
    CloseChatSessionRequest,
    ChatSessionClosedPayload,
    CloseChatSessionResponse,
)

__all__ = [
    # Original models
    "MessageType",
    "ChatMessagePayload",
    "ChatResponsePayload",
    "ChatRequest",
    "ChatResponse",
    "ChatSession",
    # Session management models
    "CreateChatSessionPayload",
    "CreateChatSessionRequest",
    "ChatSessionCreatedPayload",
    "CreateChatSessionResponse",
    "GetChatSessionPayload",
    "GetChatSessionRequest",
    "ChatSessionDataPayload",
    "GetChatSessionResponse",
    "ListChatSessionsPayload",
    "ListChatSessionsRequest",
    "ChatSessionSummary",
    "ChatSessionListPayload",
    "ListChatSessionsResponse",
    "CloseChatSessionPayload",
    "CloseChatSessionRequest",
    "ChatSessionClosedPayload",
    "CloseChatSessionResponse",
]