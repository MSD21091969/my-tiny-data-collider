# CasefileService

**Module:** `src.casefileservice.service`  
**Methods:** 13

## Methods

### Create Operations

#### [`create_casefile`](../workspace/create_casefile.md)

Create new casefile with metadata

**Request:** `CreateCasefileRequest`  
**Response:** `CreateCasefileResponse`  
**Permissions:** `casefiles:write`  

### Delete Operations

#### [`delete_casefile`](../workspace/delete_casefile.md)

Delete casefile permanently

**Request:** `DeleteCasefileRequest`  
**Response:** `DeleteCasefileResponse`  
**Requires Casefile:** ✓  
**Permissions:** `casefiles:delete`  

#### [`revoke_permission`](../workspace/revoke_permission.md)

Revoke user permission on casefile

**Request:** `RevokePermissionRequest`  
**Response:** `RevokePermissionResponse`  
**Requires Casefile:** ✓  
**Permissions:** `casefiles:share`  

### Read Operations

#### [`check_permission`](../workspace/check_permission.md)

Check if user has specific permission

**Request:** `CheckPermissionRequest`  
**Response:** `CheckPermissionResponse`  
**Requires Casefile:** ✓  
**Permissions:** `casefiles:read`  

#### [`get_casefile`](../workspace/get_casefile.md)

Retrieve casefile by ID

**Request:** `GetCasefileRequest`  
**Response:** `GetCasefileResponse`  
**Requires Casefile:** ✓  
**Permissions:** `casefiles:read`  

#### [`list_permissions`](../workspace/list_permissions.md)

List all permissions for casefile

**Request:** `ListPermissionsRequest`  
**Response:** `ListPermissionsResponse`  
**Requires Casefile:** ✓  
**Permissions:** `casefiles:read`  

### Search Operations

#### [`list_casefiles`](../workspace/list_casefiles.md)

List casefiles with optional filters

**Request:** `ListCasefilesRequest`  
**Response:** `ListCasefilesResponse`  
**Permissions:** `casefiles:read`  

### Update Operations

#### [`add_session_to_casefile`](../workspace/add_session_to_casefile.md)

Link tool/chat session to casefile

**Request:** `AddSessionToCasefileRequest`  
**Response:** `AddSessionToCasefileResponse`  
**Requires Casefile:** ✓  
**Permissions:** `casefiles:write`  

#### [`grant_permission`](../workspace/grant_permission.md)

Grant user permission on casefile

**Request:** `GrantPermissionRequest`  
**Response:** `GrantPermissionResponse`  
**Requires Casefile:** ✓  
**Permissions:** `casefiles:share`  

#### [`store_drive_files`](../workspace/store_drive_files.md)

Store Google Drive files in casefile

**Request:** `StoreDriveFilesRequest`  
**Response:** `StoreDriveFilesResponse`  
**Requires Casefile:** ✓  
**Permissions:** `casefiles:write`, `workspace:drive:read`  

#### [`store_gmail_messages`](../workspace/store_gmail_messages.md)

Store Gmail messages in casefile

**Request:** `StoreGmailMessagesRequest`  
**Response:** `StoreGmailMessagesResponse`  
**Requires Casefile:** ✓  
**Permissions:** `casefiles:write`, `workspace:gmail:read`  

#### [`store_sheet_data`](../workspace/store_sheet_data.md)

Store Google Sheets data in casefile

**Request:** `StoreSheetDataRequest`  
**Response:** `StoreSheetDataResponse`  
**Requires Casefile:** ✓  
**Permissions:** `casefiles:write`, `workspace:sheets:read`  

#### [`update_casefile`](../workspace/update_casefile.md)

Update casefile metadata

**Request:** `UpdateCasefileRequest`  
**Response:** `UpdateCasefileResponse`  
**Requires Casefile:** ✓  
**Permissions:** `casefiles:write`  

