# CommunicationService

**Module:** `src.communicationservice.service`  
**Methods:** 6

## Methods

### Create Operations

#### [`create_session`](../communication/create_session.md)

Create chat session with linked tool session

**Request:** `CreateChatSessionRequest`  
**Response:** `CreateChatSessionResponse`  
**Permissions:** `chat:create`  

### Process Operations

#### [`_ensure_tool_session`](../communication/_ensure_tool_session.md)

Internal: ensure tool session exists for chat

**Request:** `Unknown`  
**Response:** `Unknown`  

#### [`process_chat_request`](../communication/process_chat_request.md)

Parse message, call LLM, handle tool calls

**Request:** `ChatRequest`  
**Response:** `ChatResponse`  
**Permissions:** `chat:write`  

### Read Operations

#### [`get_session`](../communication/get_session.md)

Retrieve chat session by ID

**Request:** `GetChatSessionRequest`  
**Response:** `GetChatSessionResponse`  
**Permissions:** `chat:read`  

### Search Operations

#### [`list_sessions`](../communication/list_sessions.md)

List chat sessions with filters

**Request:** `ListChatSessionsRequest`  
**Response:** `ListChatSessionsResponse`  
**Permissions:** `chat:read`  

### Update Operations

#### [`close_session`](../communication/close_session.md)

Close chat session

**Request:** `CloseChatSessionRequest`  
**Response:** `CloseChatSessionResponse`  
**Permissions:** `chat:write`  

