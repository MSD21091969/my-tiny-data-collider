"""
FastAPI middleware for authentication, logging, rate limiting, and error handling.

Phase 9 middleware stack implementation.
"""

import logging
import os
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


def is_dev_mode() -> bool:
    """Check if we're in development mode."""
    return os.environ.get("ENVIRONMENT", "development").lower() == "development"


class TraceIDMiddleware(BaseHTTPMiddleware):
    """Add trace ID to all requests for distributed tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get or generate trace ID
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())

        # Store in request state for access by other components
        request.state.trace_id = trace_id

        # Process request
        response = await call_next(request)

        # Add trace ID to response headers
        response.headers["X-Trace-ID"] = trace_id

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests and responses with timing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timing
        start_time = time.time()

        # Get trace ID from request state
        trace_id = getattr(request.state, "trace_id", "no-trace-id")

        # Log incoming request
        logger.info(
            f"Incoming {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None,
                "trace_id": trace_id,
            },
        )

        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Add timing header
            response.headers["X-Process-Time"] = str(process_time)

            # Log response
            logger.info(
                f"Completed {request.method} {request.url.path} - "
                f"{response.status_code} in {process_time:.3f}s",
                extra={"trace_id": trace_id},
            )

            return response
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"Failed {request.method} {request.url.path} after {process_time:.3f}s: {exc}",
                exc_info=True,
                extra={"trace_id": trace_id},
            )
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handler for uncaught exceptions."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            trace_id = getattr(request.state, "trace_id", "no-trace-id")
            logger.error(
                f"Unhandled exception on {request.method} {request.url.path}",
                exc_info=True,
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(exc),
                    "trace_id": trace_id,
                },
            )

            # Return structured error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "internal_server_error",
                    "message": "An internal error occurred",
                    "path": request.url.path,
                    "trace_id": trace_id,
                },
            )


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """JWT authentication middleware (optional in dev mode)."""

    # Public paths that don't require authentication
    PUBLIC_PATHS = {"/health", "/v1/auth/login", "/v1/auth/register", "/docs", "/openapi.json"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip auth for public paths
        if any(request.url.path.startswith(path) for path in self.PUBLIC_PATHS):
            return await call_next(request)

        # In dev mode, allow requests without auth
        if is_dev_mode():
            auth_header = request.headers.get("authorization")
            if not auth_header:
                # Set default dev user in request state
                request.state.user = {
                    "user_id": "sam123",
                    "username": "Sam",
                    "email": "sam@example.com",
                    "roles": ["user", "admin"],
                }
                return await call_next(request)

        # Check for Authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            trace_id = getattr(request.state, "trace_id", "no-trace-id")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "unauthorized",
                    "message": "Missing or invalid authorization header",
                    "trace_id": trace_id,
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Note: Actual JWT validation happens in the dependency injection layer
        # This middleware just ensures the header exists for protected routes
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter (per-IP)."""

    def __init__(self, app: ASGIApp, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts: dict[str, list] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # Clean old requests
        if client_ip in self.request_counts:
            self.request_counts[client_ip] = [
                req_time
                for req_time in self.request_counts[client_ip]
                if current_time - req_time < self.window_seconds
            ]
        else:
            self.request_counts[client_ip] = []

        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {client_ip} on {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded. Max {self.max_requests} "
                    f"requests per {self.window_seconds}s.",
                },
            )

        # Record this request
        self.request_counts[client_ip].append(current_time)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = self.max_requests - len(self.request_counts[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
