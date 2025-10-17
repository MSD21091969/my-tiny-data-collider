"""
Main FastAPI application.
"""

import logging
import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from authservice.routes import router as auth_router
from coreservice.config import get_environment
from persistence.firestore_pool import FirestoreConnectionPool
from persistence.mock_firestore_pool import MockFirestoreConnectionPool
from persistence.redis_cache import RedisCacheService

from .middleware import (
    ErrorHandlingMiddleware,
    JWTAuthMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    TraceIDMiddleware,
)
from .prometheus_metrics import PrometheusMiddleware, get_metrics
from .routers import casefile, tool_session

logger = logging.getLogger(__name__)

# Import the chat router conditionally to handle potential missing module
try:
    from .routers import chat

    has_chat_router = True
except ImportError:
    has_chat_router = False


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="MDS Objects API",
        description="Data-centric AI Tooling Framework with Pydantic Integration",
        version="0.1.0",
    )

    # Initialize connection pool on startup
    @app.on_event("startup")
    async def startup_event() -> None:
        """Initialize resources on application startup."""
        use_mocks = os.getenv("USE_MOCKS", "false").lower() == "true"
        logger.info(f"Startup event: USE_MOCKS={use_mocks}")
        
        if not use_mocks:
            # Initialize Firestore connection pool
            logger.info("Initializing Firestore connection pool...")
            pool = FirestoreConnectionPool(database="mds-objects", pool_size=10)
            await pool.initialize()
            app.state.firestore_pool = pool
            logger.info("Firestore connection pool initialized")
        else:
            # Initialize mock Firestore pool for development
            logger.info("Mock mode enabled, initializing mock Firestore pool...")
            pool = MockFirestoreConnectionPool()
            await pool.initialize()
            app.state.firestore_pool = pool
            logger.info("Mock Firestore pool initialized")

        # Initialize Redis cache
        if not use_mocks:
            logger.info("Initializing Redis cache...")
            cache = RedisCacheService(redis_url="redis://localhost:6379/0", ttl=3600)
            try:
                await cache.initialize()
                app.state.redis_cache = cache
                logger.info("Redis cache initialized")
            except Exception as e:
                logger.warning(f"Redis cache initialization failed: {e}, continuing without cache")
                app.state.redis_cache = None
        else:
            logger.info("Mock mode enabled, skipping Redis cache initialization")
            app.state.redis_cache = None

    # Cleanup connection pool on shutdown
    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        """Cleanup resources on application shutdown."""
        if hasattr(app.state, "firestore_pool") and app.state.firestore_pool:
            await app.state.firestore_pool.close_all()
        if hasattr(app.state, "redis_cache") and app.state.redis_cache:
            await app.state.redis_cache.close()

    # Add middleware stack (order matters: first added = outermost)
    app.add_middleware(PrometheusMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(JWTAuthMiddleware)
    app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
    app.add_middleware(TraceIDMiddleware)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add routers with v1 prefix
    app.include_router(tool_session.router, prefix="/v1")
    app.include_router(casefile.router, prefix="/v1")
    app.include_router(auth_router, prefix="/v1")

    # Add chat router if available
    if has_chat_router:
        app.include_router(chat.router, prefix="/v1")

    # Add health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, Any]:
        pool_health = {}
        if hasattr(app.state, "firestore_pool") and app.state.firestore_pool:
            pool_health = await app.state.firestore_pool.health_check()
        elif hasattr(app.state, "firestore_pool") and app.state.firestore_pool is None:
            pool_health = {"status": "mock"}

        redis_health = {}
        if hasattr(app.state, "redis_cache") and app.state.redis_cache:
            redis_health = await app.state.redis_cache.health_check()

        return {
            "status": "ok",
            "version": "0.1.0",
            "environment": get_environment(),
            "firestore_pool": pool_health,
            "redis_cache": redis_health,
        }

    # Add metrics endpoint
    @app.get("/metrics", tags=["monitoring"])
    async def metrics() -> Response:
        """Expose Prometheus metrics."""

        metrics_data = get_metrics()
        return Response(content=metrics_data, media_type="text/plain")

    return app


# Main application instance
app = create_app()
