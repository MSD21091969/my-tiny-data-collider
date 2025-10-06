# GmailClient

**Module:** `src.pydantic_ai_integration.integrations.google_workspace.clients`  
**Methods:** 4

## Methods

### Create Operations

#### [`send_message`](../communication/send_message.md)

Send Gmail message

**Request:** `GmailSendMessageRequest`  
**Response:** `GmailSendMessageResponse`  
**Permissions:** `workspace:gmail:write`  

### Read Operations

#### [`get_message`](../communication/get_message.md)

Get single Gmail message by ID

**Request:** `GmailGetMessageRequest`  
**Response:** `GmailGetMessageResponse`  
**Permissions:** `workspace:gmail:read`  

#### [`list_messages`](../communication/list_messages.md)

List Gmail messages

**Request:** `GmailListMessagesRequest`  
**Response:** `GmailListMessagesResponse`  
**Permissions:** `workspace:gmail:read`  

### Search Operations

#### [`search_messages`](../communication/search_messages.md)

Search Gmail messages by query

**Request:** `GmailSearchMessagesRequest`  
**Response:** `GmailSearchMessagesResponse`  
**Permissions:** `workspace:gmail:read`  

