"""
Prometheus metrics middleware for request monitoring.
"""

import time
from collections.abc import Callable

from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

# Prometheus metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

operation_requests_total = Counter(
    "operation_requests_total",
    "Total operation requests via RequestHub",
    ["operation", "status"],
)

operation_duration_seconds = Histogram(
    "operation_duration_seconds",
    "Operation execution duration in seconds",
    ["operation"],
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware for Prometheus metrics collection."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        """Track request metrics."""
        method = request.method
        path = request.url.path

        # Skip metrics endpoint itself
        if path == "/metrics":
            return await call_next(request)

        # Track request duration
        start_time = time.time()

        try:
            response = await call_next(request)
            status_code = response.status_code

            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status=status_code,
            ).inc()

            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method,
                endpoint=path,
            ).observe(duration)

            return response

        except Exception as e:
            # Record error
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status=500,
            ).inc()

            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method,
                endpoint=path,
            ).observe(duration)

            raise e


def track_operation(operation: str, status: str, duration_seconds: float) -> None:
    """Track RequestHub operation metrics.

    Args:
        operation: Operation name
        status: Operation status (COMPLETED, FAILED, etc.)
        duration_seconds: Execution duration in seconds
    """
    operation_requests_total.labels(
        operation=operation,
        status=status,
    ).inc()

    operation_duration_seconds.labels(
        operation=operation,
    ).observe(duration_seconds)


def get_metrics() -> bytes:
    """Get Prometheus metrics in text format.

    Returns:
        Metrics in Prometheus exposition format
    """
    return generate_latest()
