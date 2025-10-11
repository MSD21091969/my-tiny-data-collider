# MVP Specification: Tiny Data Collider

**Version:** 1.0.0  
**Status:** DRAFT  
**Date:** October 11, 2025  
**Branch:** feature/develop

## Overview

This document defines the Minimum Viable Product (MVP) for the Tiny Data Collider platform - the essential subset of functionality required to validate the core value proposition with real users.

## MVP Value Proposition

**Core Promise:** Enable users to organize work into casefiles, execute AI-powered tools within session contexts, and maintain full audit trails across all operations.

## Essential User Journeys

### Journey 1: Workspace Setup
**Actor:** Authenticated User  
**Goal:** Create workspace for organizing work

**Flow:**
1. User authenticates → receives JWT token with user_id/username
2. User creates casefile with title, description → receives casefile_id
3. Token extended with casefile_id for subsequent operations
4. User confirms casefile visible in workspace

**Success Criteria:**
- Casefile created and persisted to Firestore
- Token carries routing metadata (session_request_id, casefile_id)
- User can retrieve casefile by ID

---

### Journey 2: Tool Execution in Context
**Actor:** Authenticated User (with casefile)  
**Goal:** Execute tool within session context

**Flow:**
1. User creates tool session → receives session_id
2. Session linked to casefile → audit trail established
3. User submits tool request with parameters
4. Tool executes, results returned, audit logged
5. User confirms session_request persisted under correct casefile → session → request hierarchy

**Success Criteria:**
- Session created with casefile linkage
- Tool execution completes successfully
- Audit trail visible: casefile → session → session_request
- Token carries session_id for routing

---

### Journey 3: Permission Management
**Actor:** Casefile Owner  
**Goal:** Grant collaborator access to casefile

**Flow:**
1. Owner grants "read" permission to collaborator user_id
2. Collaborator authenticates, requests casefile
3. Permission check passes → casefile data returned
4. Owner confirms permission visible in ACL list
5. Owner revokes permission
6. Collaborator access denied on next request

**Success Criteria:**
- ACL stored and enforced
- Permission levels (read/write/admin/owner) honored
- Revocation takes immediate effect

---

### Journey 4: Service Automation
**Actor:** Service (automated process)  
**Goal:** Execute tool operations without user session

**Flow:**
1. Service requests service token with client_id
2. Token issued without session_request_id (service context)
3. Service creates tool session, executes tool
4. Audit records show service_token as actor
5. Results returned, no user session created

**Success Criteria:**
- Service tokens distinguishable from user tokens
- Tool execution works without session_request_id
- Audit trail shows "system" or service identifier

---

### Journey 5: Session Lifecycle
**Actor:** Authenticated User  
**Goal:** Manage tool session from creation to closure

**Flow:**
1. User creates session → status "active"
2. User executes multiple tools in same session
3. All requests logged under session_id
4. User closes session → status "closed"
5. User confirms closed sessions cannot accept new requests

**Success Criteria:**
- Session state transitions (active → closed)
- Session request history preserved
- Closed sessions reject new tool executions

---

## Minimal Toolset (Essential 10)

### **TIER 1: Workspace Foundation (5 tools)**

1. **create_casefile** - CasefileService.create_casefile
   - **Why:** Workspace setup entry point
   - **Models:** CreateCasefileRequest → CreateCasefileResponse
   - **Auth:** Requires user token, casefiles:write permission

2. **get_casefile** - CasefileService.get_casefile
   - **Why:** Workspace retrieval and validation
   - **Models:** GetCasefileRequest → GetCasefileResponse
   - **Auth:** Requires user token, casefiles:read permission, casefile-level read access

3. **list_casefiles** - CasefileService.list_casefiles
   - **Why:** Workspace discovery
   - **Models:** ListCasefilesRequest → ListCasefilesResponse
   - **Auth:** Requires user token, casefiles:read permission

4. **update_casefile** - CasefileService.update_casefile
   - **Why:** Workspace metadata management
   - **Models:** UpdateCasefileRequest → UpdateCasefileResponse
   - **Auth:** Requires user token, casefiles:write permission, casefile-level write access

5. **delete_casefile** - CasefileService.delete_casefile
   - **Why:** Workspace cleanup
   - **Models:** DeleteCasefileRequest → DeleteCasefileResponse
   - **Auth:** Requires user token, casefiles:delete permission, casefile-level owner access

---

### **TIER 2: Session Management (3 tools)**

6. **create_session** - ToolSessionService.create_session
   - **Why:** Tool execution context establishment
   - **Models:** CreateSessionRequest → CreateSessionResponse
   - **Auth:** Requires user/service token, tools:execute permission

7. **get_session** - ToolSessionService.get_session
   - **Why:** Session state inspection
   - **Models:** GetSessionRequest → GetSessionResponse
   - **Auth:** Requires user/service token, tools:read permission

8. **close_session** - ToolSessionService.close_session
   - **Why:** Session lifecycle completion
   - **Models:** CloseSessionRequest → CloseSessionResponse
   - **Auth:** Requires user/service token, tools:execute permission

---

### **TIER 3: Tool Execution (1 tool)**

9. **process_tool_request** - ToolSessionService.process_tool_request
   - **Why:** Core tool execution engine
   - **Models:** ToolRequest → ToolResponse
   - **Auth:** Requires user/service token, tools:execute permission, validates session alignment

---

### **TIER 4: Access Control (1 tool)**

10. **grant_permission** - CasefileService.grant_permission
    - **Why:** Collaboration enablement
    - **Models:** GrantPermissionRequest → GrantPermissionResponse
    - **Auth:** Requires user token, casefiles:share permission, casefile-level admin access

---

## Out of Scope for MVP

### Excluded Tools (24 remaining)
- **add_session_to_casefile** - Auto-handled in create_session
- **list_sessions** - Nice-to-have, not critical path
- **revoke_permission** - Grant covers 80% of use case
- **list_permissions** - Admin feature, defer
- **check_permission** - Internal, not user-facing
- **store_gmail_messages** - Integration feature, post-MVP
- **store_drive_files** - Integration feature, post-MVP
- **store_sheet_data** - Integration feature, post-MVP
- **GmailClient methods (4)** - Mock mode, post-MVP
- **DriveClient methods (1)** - Mock mode, post-MVP
- **SheetsClient methods (1)** - Mock mode, post-MVP
- **RequestHub composite methods (3)** - Advanced orchestration, post-MVP
- **CommunicationService methods (6)** - Chat interface, separate track
- **process_tool_request_with_session_management** - Convenience wrapper, defer

### Excluded Features
- Chat interface and LLM integration
- Google Workspace integrations (Gmail, Drive, Sheets)
- Composite tool orchestration
- RequestHub advanced workflows
- Real-time collaboration features
- Advanced analytics and reporting
- Multi-tenant isolation
- Rate limiting per user/session
- Quota management

---

## Acceptance Criteria

### Functional Requirements

#### FR-1: Authentication & Authorization
- ✅ JWT tokens contain user_id, username, session_request_id, casefile_id, session_id
- ✅ Service tokens omit session_request_id (service context)
- ✅ Token validation enforces permission requirements
- ✅ Casefile-level ACL enforced (read/write/admin/owner)

#### FR-2: Workspace Management
- ✅ Users can create/read/update/delete casefiles
- ✅ Casefiles persist to Firestore with user_id ownership
- ✅ List operation filters by user ownership
- ✅ Delete cascades to sessions and session_requests

#### FR-3: Session Management
- ✅ Tool sessions created with casefile linkage
- ✅ Sessions have lifecycle states (active → closed)
- ✅ Session requests logged under correct hierarchy
- ✅ Closed sessions reject new tool executions

#### FR-4: Tool Execution
- ✅ Tool requests validated against session ownership
- ✅ Tool execution logs to session_request subcollection
- ✅ Results returned in ToolResponse envelope
- ✅ Errors handled gracefully with structured error responses

#### FR-5: Access Control
- ✅ Permission grants stored in casefile ACL
- ✅ Permission checks enforce access levels
- ✅ Owner can grant permissions to other users
- ✅ Permission validation integrated into all casefile operations

---

### Non-Functional Requirements

#### NFR-1: Performance
- **Target:** 95th percentile < 500ms for all operations (excluding external integrations)
- **Measured:** Via MetricsCollector in service layer
- **Tools:** PerformanceProfiler for benchmarking

#### NFR-2: Reliability
- **Target:** 99.5% uptime for core services
- **Measured:** Via health check endpoints (/health, /health/services)
- **Resilience:** Circuit breakers on external dependencies

#### NFR-3: Security
- **Target:** All endpoints require valid JWT tokens
- **Enforcement:** AuthMiddleware rejects unauthenticated requests
- **Audit:** All operations logged with user_id/service_id

#### NFR-4: Observability
- **Logging:** Structured logs with correlation IDs
- **Metrics:** Request count, latency, error rate per operation
- **Tracing:** RequestHub context propagation across services

#### NFR-5: Data Integrity
- **Persistence:** Firestore transactions for multi-document updates
- **Validation:** Pydantic models enforce schema correctness
- **Audit Trail:** Complete hierarchy: casefile → session → session_request

---

## Technical Validation

### Integration Test Coverage

**Required Tests (7 minimum):**
1. ✅ `test_auth_token_structure` - Token payload validation (PASSING)
2. ⏳ `test_create_casefile_journey` - Workspace setup flow
3. ⏳ `test_tool_execution_with_session` - Tool execution in context
4. ⏳ `test_permission_grant_and_check` - ACL enforcement
5. ⏳ `test_service_token_execution` - Automation flow
6. ⏳ `test_session_lifecycle` - State transitions
7. ⏳ `test_audit_trail_persistence` - Firestore hierarchy validation

**Current Status:** 1/7 passing (structural validation working, need service mocks)

**Location:** `tests/integration/test_mvp_user_journeys.py`

---

### API Endpoint Coverage

**Required Endpoints (10 minimum):**

| Endpoint | Method | Handler | Status |
|----------|--------|---------|--------|
| `/casefiles` | POST | create_casefile | ✅ Implemented |
| `/casefiles/{id}` | GET | get_casefile | ✅ Implemented |
| `/casefiles` | GET | list_casefiles | ✅ Implemented |
| `/casefiles/{id}` | PUT | update_casefile | ✅ Implemented |
| `/casefiles/{id}` | DELETE | delete_casefile | ✅ Implemented |
| `/sessions` | POST | create_session | ✅ Implemented |
| `/sessions/{id}` | GET | get_session | ✅ Implemented |
| `/sessions/{id}/close` | POST | close_session | ✅ Implemented |
| `/tools/execute` | POST | process_tool_request | ✅ Implemented |
| `/casefiles/{id}/permissions` | POST | grant_permission | ✅ Implemented |

**Location:** `src/pydantic_api/routers/`

---

### YAML Tool Definitions

**Required Coverage (10 tools):**

| Tool | YAML File | Validation Status |
|------|-----------|-------------------|
| create_casefile | `CasefileService_create_casefile_tool.yaml` | ✅ Validated |
| get_casefile | `CasefileService_get_casefile_tool.yaml` | ✅ Validated |
| list_casefiles | `CasefileService_list_casefiles_tool.yaml` | ✅ Validated |
| update_casefile | `CasefileService_update_casefile_tool.yaml` | ✅ Validated |
| delete_casefile | `CasefileService_delete_casefile_tool.yaml` | ✅ Validated |
| create_session | `ToolSessionService_create_session_tool.yaml` | ⏳ Pending validation |
| get_session | `ToolSessionService_get_session_tool.yaml` | ⏳ Pending validation |
| close_session | `ToolSessionService_close_session_tool.yaml` | ⏳ Pending validation |
| process_tool_request | `ToolSessionService_process_tool_request_tool.yaml` | ⏳ Pending validation |
| grant_permission | `CasefileService_grant_permission_tool.yaml` | ⏳ Pending validation |

**Location:** `config/methodtools_v1/`

**Validation Tool:** `scripts/validate_tool_definitions.py`

---

## Release Criteria

### Go/No-Go Checklist

**Code Quality:**
- [ ] All 10 MVP tools pass YAML validation
- [ ] Integration tests: 7/7 passing
- [ ] Unit tests: >90% coverage for MVP services
- [ ] Type checking: mypy passes with no errors
- [ ] Linting: ruff check passes

**Documentation:**
- [x] MVP_SPECIFICATION.md (this document)
- [ ] USER_FLOWS.md with examples
- [ ] API_REFERENCE.md for 10 MVP endpoints
- [ ] DEPLOYMENT_GUIDE.md for production setup
- [ ] TROUBLESHOOTING_GUIDE.md for common issues

**Performance:**
- [ ] Load testing: 100 concurrent users, <500ms p95 latency
- [ ] Stress testing: Graceful degradation under 2x expected load
- [ ] Benchmarking: Baseline established for all 10 tools

**Security:**
- [x] Auth flow tested with user and service tokens
- [ ] Permission boundaries tested (unauthorized access blocked)
- [ ] Token expiration and refresh working
- [ ] Audit trail complete for all operations

**Operations:**
- [ ] Health checks operational (/health, /ready, /live)
- [ ] Metrics dashboard configured
- [ ] Log aggregation working
- [ ] Firestore backup strategy documented
- [ ] Redis failover tested

**User Acceptance:**
- [ ] All 5 user journeys validated end-to-end
- [ ] Error messages user-friendly and actionable
- [ ] API responses follow consistent envelope structure
- [ ] Authentication flow smooth (token creation/validation)

---

## Success Metrics (Post-Release)

### Technical Metrics
- **Uptime:** >99.5% over 30-day period
- **Latency:** p95 <500ms, p99 <1000ms
- **Error Rate:** <0.5% of all requests
- **Tool Execution Success Rate:** >99%

### User Metrics
- **Onboarding:** Users create first casefile within 5 minutes
- **Engagement:** Average 3+ tool executions per session
- **Retention:** 70% of users return within 7 days
- **Satisfaction:** NPS >50 from early adopters

---

## Next Steps

### TIER 2 #4 Completion Roadmap

1. **YAML Validation (5 tools)** - Complete validation for remaining MVP tools
   - Status: 5/10 validated
   - Timeline: 1 day
   - Owner: Tool Engineering

2. **Service Mocks** - Add mocks for integration test completion
   - Status: Not started
   - Timeline: 2 days
   - Owner: Testing Infrastructure

3. **User Flow Documentation** - Create USER_FLOWS.md with examples
   - Status: Not started
   - Timeline: 1 day
   - Owner: Documentation

4. **API Reference** - Generate API_REFERENCE.md from OpenAPI schema
   - Status: Not started
   - Timeline: 1 day
   - Owner: Documentation

5. **Load Testing** - Establish performance baselines
   - Status: Not started
   - Timeline: 2 days
   - Owner: Performance Engineering

6. **Deployment Guide** - Document production setup
   - Status: Not started
   - Timeline: 1 day
   - Owner: DevOps

**Total Estimated Effort:** 8 days for MVP validation completion

---

## Appendix A: Tool-to-Service Mapping

| Tool Name | Service Class | Method | Request DTO | Response DTO |
|-----------|---------------|--------|-------------|--------------|
| create_casefile | CasefileService | create_casefile | CreateCasefileRequest | CreateCasefileResponse |
| get_casefile | CasefileService | get_casefile | GetCasefileRequest | GetCasefileResponse |
| list_casefiles | CasefileService | list_casefiles | ListCasefilesRequest | ListCasefilesResponse |
| update_casefile | CasefileService | update_casefile | UpdateCasefileRequest | UpdateCasefileResponse |
| delete_casefile | CasefileService | delete_casefile | DeleteCasefileRequest | DeleteCasefileResponse |
| create_session | ToolSessionService | create_session | CreateSessionRequest | CreateSessionResponse |
| get_session | ToolSessionService | get_session | GetSessionRequest | GetSessionResponse |
| close_session | ToolSessionService | close_session | CloseSessionRequest | CloseSessionResponse |
| process_tool_request | ToolSessionService | process_tool_request | ToolRequest | ToolResponse |
| grant_permission | CasefileService | grant_permission | GrantPermissionRequest | GrantPermissionResponse |

---

## Appendix B: Dependencies

### External Services
- **Firestore:** Persistence layer for casefiles, sessions, session_requests
- **Redis:** Caching layer for session state and auth tokens
- **JWT:** Token generation and validation (PyJWT library)

### Internal Services
- **AuthService:** Token creation, validation, user context
- **CasefileService:** Workspace management and ACL
- **ToolSessionService:** Session lifecycle and tool execution
- **RequestHub:** R-A-R orchestration and context flow

### Libraries
- **FastAPI:** HTTP API framework
- **Pydantic:** Data validation and serialization
- **pytest:** Testing framework
- **uvicorn:** ASGI server

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-10-11 | System | Initial MVP specification created |

---

**Status:** DRAFT - Ready for review and refinement
**Next Review:** After YAML validation completion (5 remaining tools)
