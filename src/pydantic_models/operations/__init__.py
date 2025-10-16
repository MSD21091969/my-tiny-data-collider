
"""
Operation models for domain entities.

This package contains request/response models for all domain operations:
- casefile_ops.py: Casefile CRUD and ACL operations
- tool_session_ops.py: Tool session lifecycle operations
- chat_session_ops.py: Chat session lifecycle operations
- tool_execution_ops.py: Tool and chat message execution operations

Discriminated unions for tool operation requests and responses are provided as:
- OperationRequestUnion: all request models (discriminator: 'operation')
- OperationResponseUnion: all response models (discriminator: 'operation')

For canonical entities, see pydantic_models.canonical
"""


from .casefile_ops import *
from .tool_session_ops import *
from .chat_session_ops import *
from .tool_execution_ops import *

# Discriminated unions for all operation requests and responses
from typing import Annotated, Union
from pydantic import Field

# Request union (discriminator: 'operation')
OperationRequestUnion = Annotated[
    Union[
        CreateCasefileRequest,
        UpdateCasefileRequest,
        GetCasefileRequest,
        DeleteCasefileRequest,
        ListCasefilesRequest,
        AddSessionToCasefileRequest,
        GrantPermissionRequest,
        RevokePermissionRequest,
        ListPermissionsRequest,
        CheckPermissionRequest,
        StoreGmailMessagesRequest,
        StoreDriveFilesRequest,
        StoreSheetDataRequest,
        CreateSessionRequest,
        GetSessionRequest,
        ListSessionsRequest,
        CloseSessionRequest,
        CreateChatSessionRequest,
        GetChatSessionRequest,
        ListChatSessionsRequest,
        CloseChatSessionRequest,
        ToolRequest,
        ChatRequest,
    ],
    Field(discriminator="operation")
]

# Response union (discriminator: 'operation')
OperationResponseUnion = Annotated[
    Union[
        CreateCasefileResponse,
        UpdateCasefileResponse,
        GetCasefileResponse,
        DeleteCasefileResponse,
        ListCasefilesResponse,
        AddSessionToCasefileResponse,
        GrantPermissionResponse,
        RevokePermissionResponse,
        ListPermissionsResponse,
        CheckPermissionResponse,
        StoreGmailMessagesResponse,
        StoreDriveFilesResponse,
        StoreSheetDataResponse,
        CreateSessionResponse,
        GetSessionResponse,
        ListSessionsResponse,
        CloseSessionResponse,
        CreateChatSessionResponse,
        GetChatSessionResponse,
        ListChatSessionsResponse,
        CloseChatSessionResponse,
        ToolResponse,
        ChatResponse,
    ],
    Field(discriminator="operation")
]

__all__ = [
    # Casefile ops
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
    "AddSessionToCasefileRequest",
    "AddSessionToCasefileResponse",
    "GrantPermissionRequest",
    "GrantPermissionResponse",
    "RevokePermissionRequest",
    "RevokePermissionResponse",
    "ListPermissionsRequest",
    "ListPermissionsResponse",
    "CheckPermissionRequest",
    "CheckPermissionResponse",
    "StoreGmailMessagesRequest",
    "StoreGmailMessagesResponse",
    "StoreDriveFilesRequest",
    "StoreDriveFilesResponse",
    "StoreSheetDataRequest",
    "StoreSheetDataResponse",
    # Tool session ops
    "CreateSessionRequest",
    "CreateSessionResponse",
    "GetSessionRequest",
    "GetSessionResponse",
    "ListSessionsRequest",
    "ListSessionsResponse",
    "CloseSessionRequest",
    "CloseSessionResponse",
    # Chat session ops
    "CreateChatSessionRequest",
    "CreateChatSessionResponse",
    "GetChatSessionRequest",
    "GetChatSessionResponse",
    "ListChatSessionsRequest",
    "ListChatSessionsResponse",
    "CloseChatSessionRequest",
    "CloseChatSessionResponse",
    # Tool execution ops
    "ToolRequest",
    "ToolResponse",
    "ChatRequest",
    "ChatResponse",
    # Discriminated unions
    "OperationRequestUnion",
    "OperationResponseUnion",
]
