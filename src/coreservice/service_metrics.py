"""
Advanced Service Metrics and Performance Optimization for MDS Architecture.

This module provides comprehensive metrics collection, monitoring dashboards,
and performance optimization techniques for the MDS microservices.
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

import psutil

logger = logging.getLogger(__name__)


@dataclass
class MetricValue:
    """Represents a single metric measurement."""
    name: str
    value: float
    timestamp: float
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSeries:
    """Time series data for a metric."""
    name: str
    values: deque = field(default_factory=lambda: deque(maxlen=1000))
    tags: dict[str, str] = field(default_factory=dict)

    def add_value(self, value: float, timestamp: float = None, **metadata):
        """Add a value to the series."""
        if timestamp is None:
            timestamp = time.time()
        self.values.append(MetricValue(self.name, value, timestamp, self.tags.copy(), metadata))

    def get_recent_values(self, seconds: int = 60) -> list[MetricValue]:
        """Get values from the last N seconds."""
        cutoff = time.time() - seconds
        return [v for v in self.values if v.timestamp >= cutoff]

    def get_stats(self, seconds: int = 60) -> dict[str, float]:
        """Get statistics for recent values."""
        values = self.get_recent_values(seconds)
        if not values:
            return {}

        vals = [v.value for v in values]
        return {
            'count': len(vals),
            'min': min(vals),
            'max': max(vals),
            'avg': sum(vals) / len(vals),
            'latest': vals[-1]
        }


class MetricsCollector:
    """Central metrics collection system."""

    def __init__(self):
        self._series: dict[str, MetricSeries] = {}
        self._gauges: dict[str, float] = {}
        self._counters: dict[str, int] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def record_counter(self, name: str, value: float = 1.0, **tags):
        """Record a counter metric."""
        async with self._lock:
            key = f"{name}:{json.dumps(tags, sort_keys=True)}"
            if key not in self._counters:
                self._counters[key] = 0
            self._counters[key] += value

            series_key = f"counter:{name}"
            if series_key not in self._series:
                self._series[series_key] = MetricSeries(series_key, tags=tags)
            self._series[series_key].add_value(self._counters[key])

    async def record_gauge(self, name: str, value: float, **tags):
        """Record a gauge metric."""
        async with self._lock:
            self._gauges[f"{name}:{json.dumps(tags, sort_keys=True)}"] = value

            series_key = f"gauge:{name}"
            if series_key not in self._series:
                self._series[series_key] = MetricSeries(series_key, tags=tags)
            self._series[series_key].add_value(value)

    async def record_histogram(self, name: str, value: float, **tags):
        """Record a histogram value."""
        async with self._lock:
            key = f"{name}:{json.dumps(tags, sort_keys=True)}"
            self._histograms[key].append(value)

            series_key = f"histogram:{name}"
            if series_key not in self._series:
                self._series[series_key] = MetricSeries(series_key, tags=tags)
            self._series[series_key].add_value(value)

    async def record_timer(self, name: str, duration: float, **tags):
        """Record a timer/duration metric."""
        async with self._lock:
            series_key = f"timer:{name}"
            if series_key not in self._series:
                self._series[series_key] = MetricSeries(series_key, tags=tags)
            self._series[series_key].add_value(duration)

    async def get_series(self, name: str) -> MetricSeries | None:
        """Get a metric series."""
        return self._series.get(name)

    async def get_all_series(self) -> dict[str, MetricSeries]:
        """Get all metric series."""
        return self._series.copy()

    async def get_stats(self, name: str, seconds: int = 60) -> dict[str, float]:
        """Get statistics for a metric."""
        series = self._series.get(name)
        if series:
            return series.get_stats(seconds)
        return {}


# Global metrics collector
metrics_collector = MetricsCollector()


class ServiceMetrics:
    """Service-specific metrics collection."""

    def __init__(self, service_name: str, metrics_collector: MetricsCollector = None):
        self.service_name = service_name
        self._start_time = time.time()
        self._metrics_collector = metrics_collector or metrics_collector

    @asynccontextmanager
    async def measure_execution_time(self, operation: str, **tags):
        """Context manager to measure execution time."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            await self._metrics_collector.record_timer(
                f"{self.service_name}.execution_time",
                duration,
                operation=operation,
                **tags
            )

    async def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record an HTTP request."""
        await self._metrics_collector.record_counter(
            f"{self.service_name}.requests_total",
            tags={
                'method': method,
                'endpoint': endpoint,
                'status': str(status_code),
                'status_class': str(status_code // 100) + 'xx'
            }
        )

        await self._metrics_collector.record_timer(
            f"{self.service_name}.request_duration",
            duration,
            method=method,
            endpoint=endpoint,
            status=str(status_code)
        )

    async def record_error(self, error_type: str, operation: str = None):
        """Record an error."""
        await self._metrics_collector.record_counter(
            f"{self.service_name}.errors_total",
            tags={
                'error_type': error_type,
                'operation': operation or 'unknown'
            }
        )

    async def record_cache_hit(self, cache_name: str):
        """Record a cache hit."""
        await self._metrics_collector.record_counter(
            f"{self.service_name}.cache_hits",
            tags={'cache': cache_name}
        )

    async def record_cache_miss(self, cache_name: str):
        """Record a cache miss."""
        await self._metrics_collector.record_counter(
            f"{self.service_name}.cache_misses",
            tags={'cache': cache_name}
        )

    async def record_database_query(self, operation: str, table: str, duration: float):
        """Record a database query."""
        await self._metrics_collector.record_timer(
            f"{self.service_name}.db_query_duration",
            duration,
            operation=operation,
            table=table
        )

    async def record_external_call(self, service: str, operation: str, duration: float, success: bool):
        """Record an external service call."""
        await self._metrics_collector.record_counter(
            f"{self.service_name}.external_calls_total",
            tags={
                'external_service': service,
                'operation': operation,
                'success': str(success)
            }
        )

        if success:
            await self._metrics_collector.record_timer(
                f"{self.service_name}.external_call_duration",
                duration,
                external_service=service,
                operation=operation
            )

    async def update_health_metrics(self):
        """Update system health metrics."""
        # Memory usage
        memory = psutil.virtual_memory()
        await self._metrics_collector.record_gauge(
            f"{self.service_name}.memory_usage_percent",
            memory.percent
        )
        await self._metrics_collector.record_gauge(
            f"{self.service_name}.memory_usage_mb",
            memory.used / 1024 / 1024
        )

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        await self._metrics_collector.record_gauge(
            f"{self.service_name}.cpu_usage_percent",
            cpu_percent
        )

        # Service uptime
        uptime = time.time() - self._start_time
        await self._metrics_collector.record_gauge(
            f"{self.service_name}.uptime_seconds",
            uptime
        )


class MetricsDashboard:
    """Web dashboard for metrics visualization."""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self._running = False
        self._server = None

    async def start_dashboard(self, host: str = "localhost", port: int = 8080):
        """Start the metrics dashboard server."""
        # This would implement a simple web server to serve metrics
        # For now, just log that it would start
        logger.info(f"Metrics dashboard would start on http://{host}:{port}")
        self._running = True

    async def stop_dashboard(self):
        """Stop the metrics dashboard server."""
        self._running = False
        logger.info("Metrics dashboard stopped")

    async def get_metrics_json(self) -> str:
        """Get all metrics as JSON."""
        all_series = await self.metrics_collector.get_all_series()
        result = {}

        for name, series in all_series.items():
            stats = series.get_stats(300)  # Last 5 minutes
            if stats:
                result[name] = {
                    'stats': stats,
                    'tags': series.tags,
                    'recent_count': len(series.get_recent_values(300))
                }

        return json.dumps(result, indent=2, default=str)


# Performance Optimization Components

@dataclass
class PerformanceBenchmark:
    """Performance benchmark result."""
    name: str
    operation: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    p95_time: float
    p99_time: float
    timestamp: float = field(default_factory=time.time)

    @property
    def operations_per_second(self) -> float:
        """Calculate operations per second."""
        return self.iterations / self.total_time if self.total_time > 0 else 0


class PerformanceProfiler:
    """Performance profiling and benchmarking tool."""

    def __init__(self):
        self._benchmarks: list[PerformanceBenchmark] = []

    async def benchmark_async(
        self,
        name: str,
        operation: str,
        func: Callable,
        iterations: int = 100,
        warmup_iterations: int = 10,
        *args,
        **kwargs
    ) -> PerformanceBenchmark:
        """Benchmark an async function."""
        # Warmup
        for _ in range(warmup_iterations):
            await func(*args, **kwargs)

        # Benchmark
        times = []
        start_time = time.time()

        for _ in range(iterations):
            iter_start = time.time()
            await func(*args, **kwargs)
            iter_end = time.time()
            times.append(iter_end - iter_start)

        total_time = time.time() - start_time

        # Calculate percentiles
        sorted_times = sorted(times)
        p95_index = int(0.95 * len(sorted_times))
        p99_index = int(0.99 * len(sorted_times))

        benchmark = PerformanceBenchmark(
            name=name,
            operation=operation,
            iterations=iterations,
            total_time=total_time,
            avg_time=sum(times) / len(times),
            min_time=min(sorted_times),
            max_time=max(sorted_times),
            p95_time=sorted_times[p95_index],
            p99_time=sorted_times[p99_index]
        )

        self._benchmarks.append(benchmark)
        return benchmark

    def benchmark_sync(
        self,
        name: str,
        operation: str,
        func: Callable,
        iterations: int = 100,
        warmup_iterations: int = 10,
        *args,
        **kwargs
    ) -> PerformanceBenchmark:
        """Benchmark a sync function."""
        # Warmup
        for _ in range(warmup_iterations):
            func(*args, **kwargs)

        # Benchmark
        times = []
        start_time = time.time()

        for _ in range(iterations):
            iter_start = time.time()
            func(*args, **kwargs)
            iter_end = time.time()
            times.append(iter_end - iter_start)

        total_time = time.time() - start_time

        # Calculate percentiles
        sorted_times = sorted(times)
        p95_index = int(0.95 * len(sorted_times))
        p99_index = int(0.99 * len(sorted_times))

        benchmark = PerformanceBenchmark(
            name=name,
            operation=operation,
            iterations=iterations,
            total_time=total_time,
            avg_time=sum(times) / len(times),
            min_time=min(sorted_times),
            max_time=max(sorted_times),
            p95_time=sorted_times[p95_index],
            p99_time=sorted_times[p99_index]
        )

        self._benchmarks.append(benchmark)
        return benchmark

    def get_benchmarks(self) -> list[PerformanceBenchmark]:
        """Get all benchmarks."""
        return self._benchmarks.copy()

    def get_benchmark_summary(self) -> str:
        """Get a summary of all benchmarks."""
        if not self._benchmarks:
            return "No benchmarks available"

        lines = ["Performance Benchmark Summary", "=" * 40]

        for benchmark in self._benchmarks:
            lines.extend([
                f"Benchmark: {benchmark.name}",
                f"Operation: {benchmark.operation}",
                f"Iterations: {benchmark.iterations}",
                f"Avg Time: {benchmark.avg_time:.4f}s",
                f"Min Time: {benchmark.min_time:.4f}s",
                f"Max Time: {benchmark.max_time:.4f}s",
                f"P95 Time: {benchmark.p95_time:.4f}s",
                f"P99 Time: {benchmark.p99_time:.4f}s",
                f"Ops/sec: {benchmark.operations_per_second:.2f}",
                ""
            ])

        return "\n".join(lines)


class OptimizedServiceMixin:
    """Mixin to add performance optimizations to services."""

    def __init__(self, metrics_collector: MetricsCollector = None):
        self._profiler = PerformanceProfiler()
        self._metrics = ServiceMetrics(self.__class__.__name__, metrics_collector)

    async def benchmark_operation(
        self,
        operation_name: str,
        operation_func: Callable,
        iterations: int = 50,
        *args,
        **kwargs
    ) -> PerformanceBenchmark:
        """Benchmark a service operation."""
        return await self._profiler.benchmark_async(
            f"{self.__class__.__name__}.{operation_name}",
            operation_name,
            operation_func,
            iterations,
            *args,
            **kwargs
        )

    async def optimize_with_metrics(self, operation_name: str, operation_func: Callable, *args, **kwargs):
        """Execute operation with metrics collection."""
        async with self._metrics.measure_execution_time(operation_name):
            try:
                result = await operation_func(*args, **kwargs)
                return result
            except Exception as e:
                await self._metrics.record_error(type(e).__name__, operation_name)
                raise

    def get_performance_report(self) -> str:
        """Get performance report for this service."""
        return self._profiler.get_benchmark_summary()


# Global instances
performance_profiler = PerformanceProfiler()
metrics_dashboard = MetricsDashboard(metrics_collector)


async def collect_system_metrics():
    """Background task to collect system metrics."""
    while True:
        try:
            # This would be called by services to update their metrics
            await asyncio.sleep(30)  # Collect every 30 seconds
        except asyncio.CancelledError:
            break


# Utility functions for performance monitoring
async def profile_async_function(func: Callable, iterations: int = 100, *args, **kwargs) -> PerformanceBenchmark:
    """Profile an async function."""
    profiler = PerformanceProfiler()
    return await profiler.benchmark_async(
        func.__name__,
        f"call_{func.__name__}",
        func,
        iterations,
        *args,
        **kwargs
    )


def profile_sync_function(func: Callable, iterations: int = 100, *args, **kwargs) -> PerformanceBenchmark:
    """Profile a sync function."""
    profiler = PerformanceProfiler()
    return profiler.benchmark_sync(
        func.__name__,
        f"call_{func.__name__}",
        func,
        iterations,
        *args,
        **kwargs
    )


@asynccontextmanager
async def measure_time(metrics_collector: MetricsCollector, metric_name: str, **tags):
    """Context manager to measure execution time and record as metric."""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        await metrics_collector.record_timer(metric_name, duration, **tags)
