# FastAPI Refactoring Plan - Phase 8-10 Completion Guide

**Date:** October 9, 2025
**Status:** Phases 1-7 Complete | Planning Phases 8-10
**Document Version:** 1.0
**Author:** Technical Architecture Review

---

## 🎯 Executive Assessment: What's Actually Needed

### Current State (Reality vs. Critique)

Your system critique was **significantly inaccurate** about missing FastAPI integration. The reality is:

✅ **FastAPI app exists**: `src/pydantic_api/app.py`
✅ **Routers implemented**: `casefile.py`, `tool_session.py`, `chat.py`, `auth`
✅ **R-A-R pattern complete**: 23/23 operations compliant
✅ **Dependency injection active**: `Depends()` throughout
✅ **Async operations**: All service methods are `async def`
✅ **Repository pattern**: Dual-mode (Firestore/memory)

**The Real Gap**: Not architecture, but **operational integration** between:
1. **Stateless HTTP** ↔ **Stateful tool/chat sessions**
2. **RequestHub orchestration** ↔ **Direct service calls** (mixed patterns)
3. **Business logic** ↔ **API contract enforcement**

---

## 📋 Refactoring Strategy: Phase 8-10 Completion

### Phase 8: Service Integration (Priority 1)
**Goal**: Eliminate mixed patterns, standardize through RequestHub

#### 8.1 Migrate CasefileService Operations
**Current**: Direct service calls in routes
**Target**: All operations through RequestHub with hooks

```python
# BEFORE (src/pydantic_api/routers/casefile.py)
@router.post("/", response_model=CreateCasefileResponse)
async def create_casefile(
    title: str,
    service: CasefileService = Depends(get_casefile_service),
    current_user: Dict = Depends(get_current_user)
):
    request = CreateCasefileRequest(...)
    return await service.create_casefile(request)  # Direct call

# AFTER
@router.post("/", response_model=CreateCasefileResponse)
async def create_casefile(
    title: str,
    hub: RequestHub = Depends(get_request_hub),
    current_user: Dict = Depends(get_current_user)
):
    request = CreateCasefileRequest(
        hooks=["metrics", "audit"],  # Always enabled
        context_requirements=["session"]  # Auto-load session
    )
    return await hub.dispatch(request)  # RequestHub orchestration
```

**Files to Update**:
- `src/pydantic_api/routers/casefile.py` (15+ endpoints)
- `src/pydantic_api/routers/tool_session.py` (5 endpoints)
- `src/pydantic_api/routers/chat.py` (6 endpoints)

#### 8.2 Extend RequestHub Dispatch
**Current**: Only handles 2 operations
**Target**: Handle all 26 methods

```python
# src/coreservice/request_hub.py
class RequestHub:
    async def dispatch(self, request: BaseRequest[Any]) -> BaseResponse[Any]:
        """Dispatch request to the appropriate workflow based on operation name."""

        # Map operation to handler
        handlers = {
            # Casefile operations
            "create_casefile": self._execute_casefile_create,
            "get_casefile": self._execute_casefile_get,
            "update_casefile": self._execute_casefile_update,
            "delete_casefile": self._execute_casefile_delete,
            "list_casefiles": self._execute_casefile_list,

            # Session operations
            "add_session_to_casefile": self._execute_casefile_add_session,

            # ACL operations
            "grant_permission": self._execute_casefile_grant_permission,
            "revoke_permission": self._execute_casefile_revoke_permission,
            "list_permissions": self._execute_casefile_list_permissions,
            "check_permission": self._execute_casefile_check_permission,

            # Workspace sync operations
            "store_gmail_messages": self._execute_casefile_store_gmail,
            "store_drive_files": self._execute_casefile_store_drive,
            "store_sheet_data": self._execute_casefile_store_sheet,

            # Tool session operations
            "create_session": self._execute_session_create,
            "get_session": self._execute_session_get,
            "list_sessions": self._execute_session_list,
            "close_session": self._execute_session_close,
            "process_tool_request": self._execute_tool_request,

            # Chat session operations
            "create_chat_session": self._execute_chat_create,
            "get_chat_session": self._execute_chat_get,
            "list_chat_sessions": self._execute_chat_list,
            "close_chat_session": self._execute_chat_close,
            "process_chat_request": self._execute_chat_process,

            # Composite workflows
            "workspace.casefile.create_casefile_with_session": self._execute_casefile_with_session,
        }

        handler = handlers.get(request.operation)
        if not handler:
            raise ValueError(f"Unknown operation: {request.operation}")

        return await handler(request)

    # ========================================
    # Casefile Operation Handlers
    # ========================================

    async def _execute_casefile_create(
        self, request: CreateCasefileRequest
    ) -> CreateCasefileResponse:
        """Handler for create_casefile operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.create_casefile(request)

        context["casefile_id"] = response.payload.casefile_id
        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_get(
        self, request: GetCasefileRequest
    ) -> GetCasefileResponse:
        """Handler for get_casefile operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.get_casefile(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_update(
        self, request: UpdateCasefileRequest
    ) -> UpdateCasefileResponse:
        """Handler for update_casefile operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.update_casefile(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_delete(
        self, request: DeleteCasefileRequest
    ) -> DeleteCasefileResponse:
        """Handler for delete_casefile operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.delete_casefile(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_casefile_list(
        self, request: ListCasefilesRequest
    ) -> ListCasefilesResponse:
        """Handler for list_casefiles operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.casefile_service.list_casefiles(request)

        context["status"] = response.status.value
        context["count"] = len(response.payload.casefiles)

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    # ========================================
    # Tool Session Operation Handlers
    # ========================================

    async def _execute_session_create(
        self, request: CreateSessionRequest
    ) -> CreateSessionResponse:
        """Handler for create_session operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.tool_session_service.create_session(request)

        context["session_id"] = response.payload.session_id
        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_session_get(
        self, request: GetSessionRequest
    ) -> GetSessionResponse:
        """Handler for get_session operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.tool_session_service.get_session(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_session_list(
        self, request: ListSessionsRequest
    ) -> ListSessionsResponse:
        """Handler for list_sessions operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.tool_session_service.list_sessions(request)

        context["status"] = response.status.value
        context["count"] = len(response.payload.sessions)

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_session_close(
        self, request: CloseSessionRequest
    ) -> CloseSessionResponse:
        """Handler for close_session operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.tool_session_service.close_session(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response

    async def _execute_tool_request(
        self, request: ProcessToolRequestRequest
    ) -> ProcessToolRequestResponse:
        """Handler for process_tool_request operation."""
        context = await self._prepare_context(request)
        await self._run_hooks("pre", request, context)

        response = await self.tool_session_service.process_tool_request(request)

        context["status"] = response.status.value

        await self._run_hooks("post", request, context, response)
        self._attach_hook_metadata(response, context)
        return response
```

#### 8.3 Stateless Session Management Pattern
**Challenge**: HTTP is stateless, but tool/chat sessions are stateful
**Solution**: Session ID in JWT + Context enrichment

```python
# Pattern 1: Session ID in JWT claims
# src/authservice/token.py
def create_access_token(
    user_id: str,
    session_id: Optional[str] = None,  # Add session binding
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token with optional session binding."""
    to_encode = {
        "sub": user_id,
        "session_id": session_id,  # Bind session to token
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + (expires_delta or timedelta(hours=24))
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Pattern 2: Session context in RequestHub
# src/coreservice/request_hub.py
async def _prepare_context(self, request: BaseRequest[Any]) -> Dict[str, Any]:
    """Prepare execution context with automatic session resumption."""
    context = {
        "request_id": str(request.request_id),
        "user_id": request.user_id,
        "operation": request.operation,
        "timestamp": datetime.utcnow().isoformat(),
        "hook_events": [],
    }

    # Auto-resume session from JWT
    if not request.session_id and "session_id" in request.metadata.get("jwt_claims", {}):
        request.session_id = request.metadata["jwt_claims"]["session_id"]

    # Load active session
    if request.session_id:
        session = await self.tool_session_service.repository.get_session(
            request.session_id
        )
        if session and not session.active:
            # Session expired - create new one automatically
            logger.info(f"Session {request.session_id} expired, creating new session")
            new_session_req = CreateSessionRequest(
                user_id=request.user_id,
                operation="create_session",
                payload=CreateSessionPayload(
                    casefile_id=context.get("casefile_id")
                )
            )
            new_session_resp = await self.tool_session_service.create_session(
                new_session_req
            )
            context["session"] = new_session_resp.payload.model_dump()
            context["session_recreated"] = True
        else:
            context["session"] = session.model_dump() if session else None

    # Load casefile if referenced in payload
    if hasattr(request.payload, "casefile_id") and request.payload.casefile_id:
        casefile = await self.casefile_service.repository.get_casefile(
            request.payload.casefile_id
        )
        context["casefile"] = casefile.model_dump() if casefile else None

    # Load policy patterns
    if request.policy_hints:
        context["policy"] = self.policy_loader.load_policy(request.policy_hints)
    else:
        context["policy"] = self.policy_loader.get_defaults()

    return context
```

#### 8.4 Tool/Chat Session Lifecycle Management
**Current**: Manual session creation/cleanup
**Target**: Automatic lifecycle with hooks

```python
# src/coreservice/request_hub.py
class RequestHub:
    def __init__(
        self,
        casefile_service: Optional[CasefileService] = None,
        tool_session_service: Optional[ToolSessionService] = None,
        policy_loader: Optional[PolicyPatternLoader] = None,
        hook_handlers: Optional[Dict[str, HookHandler]] = None,
    ) -> None:
        self.casefile_service = casefile_service or CasefileService()
        self.tool_session_service = tool_session_service or ToolSessionService()
        self.policy_loader = policy_loader or PolicyPatternLoader()
        self.hook_handlers = hook_handlers or {
            "metrics": self._metrics_hook,
            "audit": self._audit_hook,
            "session_lifecycle": self._session_lifecycle_hook,  # NEW
        }

    async def _session_lifecycle_hook(
        self,
        stage: str,
        request: BaseRequest[Any],
        context: Dict[str, Any],
        response: Optional[BaseResponse[Any]],
    ) -> None:
        """Manage session lifecycle automatically."""
        if stage == "pre":
            # Check if session is expired
            session = context.get("session")
            if session and not session.get("active"):
                logger.info(f"Closing expired session: {session['session_id']}")
                # Auto-close expired session
                close_req = CloseSessionRequest(
                    user_id=request.user_id,
                    operation="close_session",
                    payload=CloseSessionPayload(
                        session_id=session["session_id"]
                    )
                )
                await self.tool_session_service.close_session(close_req)
                context["session_closed"] = True

                # Record hook event
                context["hook_events"].append({
                    "hook": "session_lifecycle",
                    "stage": stage,
                    "action": "session_closed",
                    "session_id": session["session_id"],
                    "timestamp": datetime.utcnow().isoformat(),
                })

        elif stage == "post":
            # Update session activity timestamp
            session = context.get("session")
            if session and session.get("active"):
                # Update last_activity timestamp
                await self.tool_session_service.repository.update_activity(
                    session["session_id"]
                )

                # Record hook event
                context["hook_events"].append({
                    "hook": "session_lifecycle",
                    "stage": stage,
                    "action": "activity_updated",
                    "session_id": session["session_id"],
                    "timestamp": datetime.utcnow().isoformat(),
                })
```

---

### Phase 9: Route Cleanup & Middleware (Priority 2)

#### 9.1 API Versioning
**Pattern**: `/v1/` prefix for all routes

```python
# src/pydantic_api/app.py
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="MDS Objects API",
        description="Data-centric AI Tooling Framework with Pydantic Integration",
        version="1.0.0",
        openapi_url="/v1/openapi.json",  # Versioned OpenAPI
        docs_url="/v1/docs",
        redoc_url="/v1/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Version 1 routers
    v1_router = APIRouter(prefix="/v1")
    v1_router.include_router(casefile.router, prefix="/casefiles", tags=["Casefiles"])
    v1_router.include_router(tool_session.router, prefix="/tool-sessions", tags=["Tool Sessions"])
    v1_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
    v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

    app.include_router(v1_router)

    # Health check endpoint (no version prefix)
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": "1.0.0",
            "api_version": "v1"
        }

    return app

app = create_app()
```

#### 9.2 Authentication Middleware
**Pattern**: Validate JWT on every request

```python
# src/pydantic_api/middleware/auth.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from authservice.token import decode_access_token
import logging

logger = logging.getLogger(__name__)

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate JWT tokens on all requests."""

    def __init__(self, app, public_paths: list[str] = None):
        super().__init__(app)
        self.public_paths = public_paths or [
            "/health",
            "/v1/auth/login",
            "/v1/docs",
            "/v1/redoc",
            "/v1/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        if request.url.path in self.public_paths:
            return await call_next(request)

        # Extract JWT from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Missing or invalid authorization header"
                }
            )

        token = auth_header.split(" ")[1]
        try:
            payload = decode_access_token(token)
            # Attach user context to request state
            request.state.user_id = payload["sub"]
            request.state.session_id = payload.get("session_id")
            request.state.jwt_claims = payload
            logger.debug(f"Authenticated user: {payload['sub']}")
        except Exception as e:
            logger.warning(f"Token validation failed: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": f"Invalid token: {str(e)}"
                }
            )

        return await call_next(request)

# Add to app.py
from pydantic_api.middleware.auth import AuthenticationMiddleware
app.add_middleware(AuthenticationMiddleware)
```

#### 9.3 Request Logging Middleware
**Pattern**: Log all requests with trace_id

```python
# src/pydantic_api/middleware/logging.py
import logging
from uuid import uuid4
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from datetime import datetime

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests with trace IDs."""

    async def dispatch(self, request: Request, call_next):
        # Generate trace ID for request tracking
        trace_id = str(uuid4())
        request.state.trace_id = trace_id

        start_time = datetime.utcnow()

        logger.info(
            f"[{trace_id}] {request.method} {request.url.path}",
            extra={
                "trace_id": trace_id,
                "method": request.method,
                "path": request.url.path,
                "user_id": getattr(request.state, "user_id", None),
                "timestamp": start_time.isoformat(),
            }
        )

        try:
            response = await call_next(request)

            duration = (datetime.utcnow() - start_time).total_seconds()

            logger.info(
                f"[{trace_id}] Response status: {response.status_code} ({duration:.3f}s)",
                extra={
                    "trace_id": trace_id,
                    "status_code": response.status_code,
                    "duration_seconds": duration,
                }
            )

            # Add trace ID to response headers
            response.headers["X-Trace-ID"] = trace_id

            return response
        except Exception as e:
            logger.exception(
                f"[{trace_id}] Request failed: {str(e)}",
                extra={"trace_id": trace_id}
            )
            raise

# Add to app.py
from pydantic_api.middleware.logging import RequestLoggingMiddleware
app.add_middleware(RequestLoggingMiddleware)
```

#### 9.4 Rate Limiting Middleware
**Pattern**: Per-user rate limiting with in-memory store

```python
# src/pydantic_api/middleware/rate_limit.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for per-user rate limiting."""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self._requests: Dict[str, List[datetime]] = {}  # user_id -> [timestamps]
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next):
        user_id = getattr(request.state, "user_id", "anonymous")

        async with self._lock:
            now = datetime.now()
            cutoff = now - timedelta(minutes=1)

            # Clean old entries
            if user_id in self._requests:
                self._requests[user_id] = [
                    ts for ts in self._requests[user_id] if ts > cutoff
                ]
            else:
                self._requests[user_id] = []

            # Check rate limit
            if len(self._requests[user_id]) >= self.requests_per_minute:
                logger.warning(
                    f"Rate limit exceeded for user: {user_id}",
                    extra={
                        "user_id": user_id,
                        "requests_count": len(self._requests[user_id])
                    }
                )
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too Many Requests",
                        "message": "Rate limit exceeded",
                        "retry_after": 60
                    },
                    headers={"Retry-After": "60"}
                )

            # Record request
            self._requests[user_id].append(now)

        return await call_next(request)

# Add to app.py
from pydantic_api.middleware.rate_limit import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
```

#### 9.5 Error Handling Middleware
**Pattern**: Standardized error responses

```python
# src/pydantic_api/middleware/error_handler.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

def setup_exception_handlers(app):
    """Setup global exception handlers for the FastAPI app."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):
        """Handle Pydantic validation errors."""
        logger.warning(
            f"Validation error: {exc.errors()}",
            extra={
                "trace_id": getattr(request.state, "trace_id", None),
                "path": request.url.path,
            }
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "message": "Request validation failed",
                "details": exc.errors(),
                "trace_id": getattr(request.state, "trace_id", None)
            }
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError exceptions."""
        logger.warning(
            f"ValueError: {str(exc)}",
            extra={
                "trace_id": getattr(request.state, "trace_id", None),
                "path": request.url.path,
            }
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Bad Request",
                "message": str(exc),
                "trace_id": getattr(request.state, "trace_id", None)
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions."""
        logger.exception(
            f"Unhandled exception: {exc}",
            extra={
                "trace_id": getattr(request.state, "trace_id", None),
                "path": request.url.path,
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "trace_id": getattr(request.state, "trace_id", None)
            }
        )

# Add to app.py
from pydantic_api.middleware.error_handler import setup_exception_handlers
setup_exception_handlers(app)
```

---

### Phase 10: Production Readiness (Priority 3)

#### 10.1 Database Connection Pooling
**Current**: New connection per request
**Target**: Connection pool with health checks

```python
# src/persistence/firestore_adapter.py
from google.cloud import firestore
from google.cloud.firestore import AsyncClient
import asyncio
import logging

logger = logging.getLogger(__name__)

class FirestoreConnectionPool:
    """Connection pool for Firestore async clients."""

    def __init__(self, database: str = "mds-objects", pool_size: int = 10):
        self.database = database
        self.pool_size = pool_size
        self._pool: list[AsyncClient] = []
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self):
        """Create connection pool on startup."""
        if self._initialized:
            return

        logger.info(f"Initializing Firestore connection pool (size={self.pool_size})")
        for i in range(self.pool_size):
            client = firestore.AsyncClient(database=self.database)
            self._pool.append(client)
            logger.debug(f"Created connection {i+1}/{self.pool_size}")

        self._initialized = True
        logger.info("Firestore connection pool initialized")

    async def acquire(self) -> AsyncClient:
        """Get connection from pool."""
        async with self._lock:
            if not self._pool:
                # Pool exhausted - create temporary connection
                logger.warning("Connection pool exhausted, creating temporary connection")
                return firestore.AsyncClient(database=self.database)

            client = self._pool.pop()
            logger.debug(f"Acquired connection (pool size: {len(self._pool)})")
            return client

    async def release(self, client: AsyncClient):
        """Return connection to pool."""
        async with self._lock:
            if len(self._pool) < self.pool_size:
                self._pool.append(client)
                logger.debug(f"Released connection (pool size: {len(self._pool)})")
            else:
                # Pool full - close connection
                await client.close()
                logger.debug("Pool full, closed excess connection")

    async def close_all(self):
        """Close all connections in pool."""
        logger.info("Closing all Firestore connections")
        async with self._lock:
            for client in self._pool:
                await client.close()
            self._pool.clear()
        logger.info("All connections closed")

# src/pydantic_api/app.py
from persistence.firestore_adapter import FirestoreConnectionPool

@app.on_event("startup")
async def startup_event():
    """Initialize resources on application startup."""
    logger.info("Application starting up")
    app.state.db_pool = FirestoreConnectionPool(pool_size=10)
    await app.state.db_pool.initialize()
    logger.info("Startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on application shutdown."""
    logger.info("Application shutting down")
    await app.state.db_pool.close_all()
    logger.info("Shutdown complete")

# Usage in repositories
class CasefileRepository:
    async def get_casefile(
        self,
        casefile_id: str,
        db_pool: FirestoreConnectionPool
    ) -> Optional[CasefileModel]:
        """Get casefile using connection pool."""
        client = await db_pool.acquire()
        try:
            doc = await client.collection("casefiles").document(casefile_id).get()
            return CasefileModel(**doc.to_dict()) if doc.exists else None
        finally:
            await db_pool.release(client)
```

#### 10.2 Caching Layer
**Pattern**: Redis caching for frequently accessed data

```python
# src/coreservice/cache.py
from typing import Optional, Any
import json
import logging
from redis.asyncio import Redis, from_url

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[Redis] = None

    async def connect(self):
        """Connect to Redis."""
        if not self.redis:
            self.redis = await from_url(self.redis_url, decode_responses=True)
            logger.info("Connected to Redis cache")

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self.redis = None
            logger.info("Disconnected from Redis cache")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis:
            await self.connect()

        try:
            value = await self.redis.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL (seconds)."""
        if not self.redis:
            await self.connect()

        try:
            await self.redis.setex(key, ttl, json.dumps(value))
            logger.debug(f"Cache set: {key} (ttl={ttl}s)")
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    async def delete(self, key: str):
        """Delete key from cache."""
        if not self.redis:
            await self.connect()

        try:
            await self.redis.delete(key)
            logger.debug(f"Cache deleted: {key}")
        except Exception as e:
            logger.error(f"Cache delete error: {e}")

    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern."""
        if not self.redis:
            await self.connect()

        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
                logger.info(f"Invalidated {len(keys)} keys matching: {pattern}")
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")

# Usage in RequestHub
class RequestHub:
    def __init__(
        self,
        ...,
        cache: Optional[CacheService] = None
    ):
        self.cache = cache or CacheService()

    async def _prepare_context(self, request: BaseRequest[Any]) -> Dict[str, Any]:
        """Prepare context with caching support."""
        context = {
            "request_id": str(request.request_id),
            "user_id": request.user_id,
            "operation": request.operation,
            "timestamp": datetime.utcnow().isoformat(),
            "hook_events": [],
        }

        # Try cache first for session
        if request.session_id:
            cache_key = f"session:{request.session_id}"
            cached_session = await self.cache.get(cache_key)
            if cached_session:
                context["session"] = cached_session
                context["session_from_cache"] = True
                return context

        # Cache miss - load from database
        if request.session_id:
            session = await self.tool_session_service.repository.get_session(
                request.session_id
            )
            if session:
                context["session"] = session.model_dump()
                # Update cache
                await self.cache.set(
                    f"session:{request.session_id}",
                    context["session"],
                    ttl=300  # 5 minutes
                )

        return context

# Add to app.py
@app.on_event("startup")
async def startup_event():
    app.state.cache = CacheService()
    await app.state.cache.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.cache.disconnect()
```

#### 10.3 Monitoring & Metrics
**Pattern**: Prometheus metrics export

```python
# src/pydantic_api/middleware/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time

# Define metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"]
)

session_operations_total = Counter(
    "session_operations_total",
    "Total session operations",
    ["operation", "status"]
)

casefile_operations_total = Counter(
    "casefile_operations_total",
    "Total casefile operations",
    ["operation", "status"]
)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics."""

    async def dispatch(self, request: Request, call_next):
        method = request.method
        endpoint = request.url.path

        # Track in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        start_time = time.time()

        try:
            response = await call_next(request)
            status = response.status_code
        except Exception as e:
            status = 500
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time

            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()

        return response

# Add to app.py
from pydantic_api.middleware.metrics import MetricsMiddleware
app.add_middleware(MetricsMiddleware)

# Metrics endpoint
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

@app.get("/metrics")
async def metrics_endpoint():
    """Expose Prometheus metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

---

## 🔧 Implementation Plan: Step-by-Step

### Week 1: Core Refactoring (Phase 8)

**Days 1-2: Extend RequestHub Dispatch (8.2)**
- [ ] Add all 26 operation handlers to `RequestHub`
- [ ] Update `src/coreservice/request_hub.py`
- [ ] Add unit tests for each handler
- [ ] Test all handlers with mock services

**Days 3-4: Migrate Casefile Routes (8.1)**
- [ ] Update `src/pydantic_api/routers/casefile.py`
- [ ] Replace all direct service calls with `hub.dispatch()`
- [ ] Add hooks configuration to all requests
- [ ] Test all endpoints end-to-end

**Day 5: Migrate Tool Session Routes**
- [ ] Update `src/pydantic_api/routers/tool_session.py`
- [ ] Replace all direct service calls with `hub.dispatch()`
- [ ] Test session lifecycle with hooks
- [ ] Validate session state management

### Week 2: Middleware & Infrastructure (Phase 9)

**Days 1-2: Add Middleware Stack (9.2-9.5)**
- [ ] Create `src/pydantic_api/middleware/` directory
- [ ] Implement `AuthenticationMiddleware`
- [ ] Implement `RequestLoggingMiddleware`
- [ ] Implement `RateLimitMiddleware`
- [ ] Implement error handlers
- [ ] Test middleware chain

**Days 3-4: API Versioning (9.1)**
- [ ] Add `/v1/` prefix to all routes
- [ ] Update OpenAPI configuration
- [ ] Update route imports in `app.py`
- [ ] Test backwards compatibility
- [ ] Update documentation

**Day 5: Testing & Validation**
- [ ] Run full test suite (`pytest tests/ -v`)
- [ ] Run integration tests
- [ ] Test all endpoints with Postman/curl
- [ ] Validate ARCHITECTURE.md compliance
- [ ] Update documentation

### Week 3: Production Readiness (Phase 10)

**Days 1-2: Connection Pooling (10.1)**
- [ ] Implement `FirestoreConnectionPool`
- [ ] Update `src/persistence/firestore_adapter.py`
- [ ] Update all repositories to use pool
- [ ] Add health check for database
- [ ] Load test with 100+ concurrent requests

**Days 3-4: Caching Layer (10.2)**
- [ ] Implement `CacheService` with Redis
- [ ] Add cache to `RequestHub._prepare_context()`
- [ ] Cache session and casefile lookups
- [ ] Add cache invalidation on updates
- [ ] Measure performance improvement

**Day 5: Monitoring & Documentation (10.3)**
- [ ] Add Prometheus metrics middleware
- [ ] Set up metrics endpoint `/metrics`
- [ ] Document all new middleware
- [ ] Update ARCHITECTURE.md with Phase 8-10 status
- [ ] Create deployment guide

---

## 📊 Validation Checklist

### Architecture Compliance
- [ ] All routes use RequestHub (no direct service calls)
- [ ] All operations have hooks enabled (`metrics`, `audit`, `session_lifecycle`)
- [ ] Context enrichment automatic (session/casefile loading with caching)
- [ ] Stateless HTTP with session resumption via JWT
- [ ] All 26 methods have dedicated handlers

### API Contract Enforcement
- [ ] All endpoints have `response_model=` parameter
- [ ] Pydantic validation on all request payloads
- [ ] Standardized error responses (422, 400, 401, 429, 500)
- [ ] OpenAPI schema complete and accessible at `/v1/docs`
- [ ] API versioning with `/v1/` prefix

### Middleware Stack
- [ ] Authentication middleware validates JWT on all routes
- [ ] Request logging middleware adds trace IDs
- [ ] Rate limiting middleware enforces 60 req/min per user
- [ ] Error handlers catch all exception types
- [ ] CORS middleware configured

### Performance
- [ ] Firestore connection pooling active (pool size: 10)
- [ ] Redis cache hit rate >70% (monitor with metrics)
- [ ] P95 latency <200ms (measure with load testing)
- [ ] No memory leaks (monitor with profiling)

### Session Management
- [ ] Session ID stored in JWT claims
- [ ] Session auto-resumed from JWT
- [ ] Expired sessions auto-closed by lifecycle hook
- [ ] Session activity timestamp updated on each request
- [ ] New sessions created automatically when needed

### Testing
- [ ] 100% of routes tested (unit + integration)
- [ ] Integration tests cover all workflows
- [ ] Load test passes (100 req/s for 5 minutes)
- [ ] All 8 existing tests still passing
- [ ] New tests added for Phase 8-10 features

### Monitoring
- [ ] Prometheus metrics exposed at `/metrics`
- [ ] Request count by method/endpoint/status
- [ ] Request duration histogram
- [ ] In-progress request gauge
- [ ] Session and casefile operation counters

### Documentation
- [ ] ARCHITECTURE.md updated with Phase 8-10 status
- [ ] Middleware documentation complete
- [ ] API documentation at `/v1/docs` accurate
- [ ] Deployment guide created
- [ ] Environment variable documentation complete

---

## 🎯 Key Recommendations

### 1. Prioritize Phase 8 (Service Integration)
**Why:** This is the core gap - mixed patterns violate single responsibility principle and make the system harder to maintain.

**Impact:**
- ✅ Consistent request flow through RequestHub
- ✅ Automatic hooks on all operations
- ✅ Centralized context enrichment
- ✅ Easier debugging with unified logging

### 2. Session Management is Critical
**Why:** HTTP is stateless but tool/chat sessions are stateful - this is a fundamental architectural challenge.

**Solution:**
- Session ID in JWT claims (bind session to auth token)
- Automatic session resumption in `_prepare_context()`
- Lifecycle hook for expired session cleanup
- Activity timestamp updates on every request

**Benefits:**
- ✅ No manual session management in routes
- ✅ Sessions persist across requests
- ✅ Automatic cleanup of stale sessions
- ✅ User experience improvement

### 3. Don't Rewrite What Works
**Why:** Your existing architecture is excellent - R-A-R pattern, parameter inheritance, tool generation are all solid.

**Keep:**
- ✅ 6-layer contract stack (L0-L5)
- ✅ Parameter inheritance flow (DTO → Method → Tool)
- ✅ BaseRequest/BaseResponse generics
- ✅ MANAGED_METHODS registry
- ✅ Tool generation scripts

**Integrate:**
- Make RequestHub the universal entry point
- Add middleware for cross-cutting concerns
- Enhance with caching and connection pooling

### 4. Add Observability First
**Why:** You can't optimize what you can't measure.

**Order:**
1. Request logging middleware (trace IDs)
2. Prometheus metrics
3. Performance profiling
4. Then optimize based on data

**Metrics to Track:**
- Request count by operation
- Request duration (P50, P95, P99)
- Cache hit rate
- Database connection pool utilization
- Session creation/closure rate

### 5. Test Continuously
**Why:** Each phase builds on the previous - catch issues early.

**After Each Phase:**
1. Run unit tests: `pytest tests/ -v`
2. Run integration tests: `pytest tests/integration/ -v`
3. Manual endpoint testing with curl/Postman
4. Load test with `locust` or `ab`
5. Check logs for errors/warnings

**Test Scenarios:**
- Create casefile → Add session → List casefiles
- Session expiration and auto-recreation
- Rate limit exceeded (429 response)
- Invalid JWT (401 response)
- Concurrent requests (connection pool)

---

## 💡 Next Immediate Action

Start with **Phase 8.2** (Extend RequestHub Dispatch):

```bash
# 1. Create feature branch
git checkout -b feature/request-hub-complete-dispatch

# 2. Update RequestHub with all 26 handlers
# Edit: src/coreservice/request_hub.py

# 3. Add missing imports for all operation types
# Edit: src/coreservice/request_hub.py (top of file)

# 4. Test RequestHub handlers
pytest tests/coreservice/test_request_hub.py -v

# 5. Update one router as proof-of-concept
# Edit: src/pydantic_api/routers/casefile.py (just create_casefile endpoint)

# 6. Test end-to-end
pytest tests/integration/test_request_hub_fastapi.py -v

# 7. If successful, migrate remaining endpoints
# Edit: src/pydantic_api/routers/casefile.py (all endpoints)
# Edit: src/pydantic_api/routers/tool_session.py
# Edit: src/pydantic_api/routers/chat.py

# 8. Commit and test
git add .
git commit -m "feat: Complete RequestHub dispatch for all 26 operations"
pytest tests/ -v --cov=src
```

---

## 📚 Additional Resources

### FastAPI Best Practices
- [FastAPI Official Docs - Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)

### Session Management in Stateless APIs
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Stateless Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

### Performance & Scaling
- [Async Database Connection Pooling](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Redis Caching Patterns](https://redis.io/docs/manual/patterns/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)

### Testing
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Load Testing with Locust](https://locust.io/)

---

## 🔄 Continuous Improvement

After completing Phases 8-10, consider:

### Phase 11: Advanced Features
- [ ] WebSocket support for real-time chat
- [ ] Background task queue (Celery/RQ)
- [ ] Distributed tracing (OpenTelemetry)
- [ ] API gateway integration

### Phase 12: Security Hardening
- [ ] Rate limiting per endpoint (not just global)
- [ ] API key management
- [ ] OAuth2 integration (Google, GitHub)
- [ ] Input sanitization & validation

### Phase 13: Developer Experience
- [ ] GraphQL endpoint (optional)
- [ ] SDK generation (Python, TypeScript)
- [ ] Interactive API playground
- [ ] Webhook support

---

## ✅ Success Criteria

Your refactoring is complete when:

1. **All routes use RequestHub** - No direct service calls
2. **All operations have hooks** - Metrics, audit, session lifecycle
3. **Session management is automatic** - JWT binding, auto-resumption, lifecycle
4. **Middleware stack is complete** - Auth, logging, rate limit, errors
5. **API is versioned** - `/v1/` prefix, OpenAPI schema
6. **Performance is optimized** - Connection pooling, caching, <200ms P95
7. **Monitoring is active** - Prometheus metrics, Grafana dashboards
8. **All tests pass** - 100% existing + new integration tests
9. **Documentation is updated** - ARCHITECTURE.md, deployment guide

---

## 📞 Support & Questions

If you encounter issues during implementation:

1. **Check logs** - All middleware adds detailed logging
2. **Review metrics** - `/metrics` endpoint shows system health
3. **Test incrementally** - Don't migrate all routes at once
4. **Validate assumptions** - Use integration tests to verify behavior
5. **Consult ARCHITECTURE.md** - Architecture decisions documented there

---

**Document Status:** Ready for Implementation
**Next Review:** After Phase 8 completion
**Owner:** Development Team
