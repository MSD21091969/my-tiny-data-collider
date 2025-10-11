import asyncio
import os
import sys
import time

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from coreservice.service_metrics import (
    MetricsCollector,
    MetricsDashboard,
    OptimizedServiceMixin,
    PerformanceBenchmark,
    PerformanceProfiler,
    ServiceMetrics,
    measure_time,
    profile_async_function,
    profile_sync_function,
)


class TestMetricsCollector:
    """Test the MetricsCollector class."""

    @pytest.fixture
    def collector(self):
        """Create a fresh MetricsCollector for each test."""
        return MetricsCollector()

    @pytest.mark.asyncio
    async def test_record_counter(self, collector):
        """Test recording counter metrics."""
        await collector.record_counter("test_counter", 1.0, service="test")
        await collector.record_counter("test_counter", 2.0, service="test")

        series = await collector.get_series("counter:test_counter")
        assert series is not None
        assert len(series.values) == 2
        assert series.values[0].value == 1.0
        assert series.values[1].value == 3.0  # Cumulative

    @pytest.mark.asyncio
    async def test_record_gauge(self, collector):
        """Test recording gauge metrics."""
        await collector.record_gauge("test_gauge", 42.0, service="test")
        await collector.record_gauge("test_gauge", 43.0, service="test")

        series = await collector.get_series("gauge:test_gauge")
        assert series is not None
        assert len(series.values) == 2
        assert series.values[0].value == 42.0
        assert series.values[1].value == 43.0

    @pytest.mark.asyncio
    async def test_record_histogram(self, collector):
        """Test recording histogram metrics."""
        await collector.record_histogram("test_histogram", 1.0, service="test")
        await collector.record_histogram("test_histogram", 2.0, service="test")

        series = await collector.get_series("histogram:test_histogram")
        assert series is not None
        assert len(series.values) == 2

    @pytest.mark.asyncio
    async def test_record_timer(self, collector):
        """Test recording timer metrics."""
        await collector.record_timer("test_timer", 0.5, service="test")

        series = await collector.get_series("timer:test_timer")
        assert series is not None
        assert len(series.values) == 1
        assert series.values[0].value == 0.5

    @pytest.mark.asyncio
    async def test_get_stats(self, collector):
        """Test getting statistics for metrics."""
        # Add some test data
        await collector.record_gauge("test_metric", 10.0)
        await collector.record_gauge("test_metric", 20.0)
        await collector.record_gauge("test_metric", 30.0)

        stats = await collector.get_stats("gauge:test_metric")
        assert "count" in stats
        assert "min" in stats
        assert "max" in stats
        assert "avg" in stats
        assert stats["count"] == 3
        assert stats["min"] == 10.0
        assert stats["max"] == 30.0
        assert stats["avg"] == 20.0


class TestServiceMetrics:
    """Test the ServiceMetrics class."""

    @pytest.fixture
    def service_metrics(self):
        """Create ServiceMetrics instance for testing."""
        collector = MetricsCollector()
        return ServiceMetrics("TestService", collector)

    @pytest.mark.asyncio
    async def test_measure_execution_time(self, service_metrics):
        """Test execution time measurement."""
        async def dummy_operation():
            await asyncio.sleep(0.01)
            return "result"

        async with service_metrics.measure_execution_time("test_operation", user="test"):
            result = await dummy_operation()

        assert result == "result"

        # Check that timer was recorded
        series = await service_metrics._metrics_collector.get_series("timer:TestService.execution_time")
        assert series is not None
        assert len(series.values) >= 1

    @pytest.mark.asyncio
    async def test_record_request(self, service_metrics):
        """Test recording HTTP requests."""
        await service_metrics.record_request("GET", "/api/test", 200, 0.1)

        # Check request counter
        series = await service_metrics._metrics_collector.get_series("counter:TestService.requests_total")
        assert series is not None
        assert len(series.values) == 1

        # Check request duration
        duration_series = await service_metrics._metrics_collector.get_series("timer:TestService.request_duration")
        assert duration_series is not None
        assert len(duration_series.values) == 1

    @pytest.mark.asyncio
    async def test_record_error(self, service_metrics):
        """Test recording errors."""
        await service_metrics.record_error("ValueError", "test_operation")

        series = await service_metrics._metrics_collector.get_series("counter:TestService.errors_total")
        assert series is not None
        assert len(series.values) == 1

    @pytest.mark.asyncio
    async def test_record_cache_operations(self, service_metrics):
        """Test recording cache hits and misses."""
        await service_metrics.record_cache_hit("user_cache")
        await service_metrics.record_cache_miss("user_cache")

        hit_series = await service_metrics._metrics_collector.get_series("counter:TestService.cache_hits")
        miss_series = await service_metrics._metrics_collector.get_series("counter:TestService.cache_misses")

        assert hit_series is not None
        assert miss_series is not None
        assert len(hit_series.values) == 1
        assert len(miss_series.values) == 1

    @pytest.mark.asyncio
    async def test_record_database_query(self, service_metrics):
        """Test recording database queries."""
        await service_metrics.record_database_query("SELECT", "users", 0.05)

        series = await service_metrics._metrics_collector.get_series("timer:TestService.db_query_duration")
        assert series is not None
        assert len(series.values) == 1
        assert series.values[0].value == 0.05

    @pytest.mark.asyncio
    async def test_record_external_call(self, service_metrics):
        """Test recording external service calls."""
        await service_metrics.record_external_call("payment_service", "charge", 0.2, True)
        await service_metrics.record_external_call("email_service", "send", 0.1, False)

        success_series = await service_metrics._metrics_collector.get_series("counter:TestService.external_calls_total")
        duration_series = await service_metrics._metrics_collector.get_series("timer:TestService.external_call_duration")

        assert success_series is not None
        assert duration_series is not None
        assert len(success_series.values) == 2
        assert len(duration_series.values) == 1  # Only successful call recorded duration

    @pytest.mark.asyncio
    async def test_update_health_metrics(self, service_metrics):
        """Test updating system health metrics."""
        await service_metrics.update_health_metrics()

        # Check memory metrics
        mem_percent_series = await service_metrics._metrics_collector.get_series("gauge:TestService.memory_usage_percent")
        mem_mb_series = await service_metrics._metrics_collector.get_series("gauge:TestService.memory_usage_mb")

        assert mem_percent_series is not None
        assert mem_mb_series is not None

        # Check CPU metrics
        cpu_series = await service_metrics._metrics_collector.get_series("gauge:TestService.cpu_usage_percent")
        assert cpu_series is not None

        # Check uptime
        uptime_series = await service_metrics._metrics_collector.get_series("gauge:TestService.uptime_seconds")
        assert uptime_series is not None


class TestPerformanceProfiler:
    """Test the PerformanceProfiler class."""

    @pytest.fixture
    def profiler(self):
        """Create a PerformanceProfiler instance."""
        return PerformanceProfiler()

    @pytest.mark.asyncio
    async def test_benchmark_async(self, profiler):
        """Test benchmarking async functions."""
        async def test_func(delay=0.01):
            await asyncio.sleep(delay)
            return 42

        benchmark = await profiler.benchmark_async(
            "test_async", "sleep_operation", test_func, iterations=5, warmup_iterations=2
        )

        assert isinstance(benchmark, PerformanceBenchmark)
        assert benchmark.name == "test_async"
        assert benchmark.operation == "sleep_operation"
        assert benchmark.iterations == 5
        assert benchmark.total_time > 0
        assert benchmark.avg_time > 0
        assert benchmark.operations_per_second > 0

    def test_benchmark_sync(self, profiler):
        """Test benchmarking sync functions."""
        def test_func(delay=0.01):
            time.sleep(delay)
            return 42

        benchmark = profiler.benchmark_sync(
            "test_sync", "sleep_operation", test_func, iterations=3, warmup_iterations=1
        )

        assert isinstance(benchmark, PerformanceBenchmark)
        assert benchmark.name == "test_sync"
        assert benchmark.iterations == 3
        assert benchmark.total_time > 0

    def test_get_benchmarks(self, profiler):
        """Test getting benchmark results."""
        def dummy_func():
            return 1

        profiler.benchmark_sync("test1", "op1", dummy_func, iterations=1)
        profiler.benchmark_sync("test2", "op2", dummy_func, iterations=1)

        benchmarks = profiler.get_benchmarks()
        assert len(benchmarks) == 2
        assert benchmarks[0].name == "test1"
        assert benchmarks[1].name == "test2"

    def test_get_benchmark_summary(self, profiler):
        """Test getting benchmark summary."""
        def dummy_func():
            return 1

        profiler.benchmark_sync("test", "operation", dummy_func, iterations=1)

        summary = profiler.get_benchmark_summary()
        assert "Performance Benchmark Summary" in summary
        assert "test" in summary
        assert "operation" in summary


class TestMetricsDashboard:
    """Test the MetricsDashboard class."""

    @pytest.fixture
    def dashboard(self):
        """Create a MetricsDashboard instance."""
        collector = MetricsCollector()
        return MetricsDashboard(collector)

    @pytest.mark.asyncio
    async def test_get_metrics_json(self, dashboard):
        """Test getting metrics as JSON."""
        # Add some test data
        await dashboard.metrics_collector.record_gauge("test_metric", 42.0, service="test")

        json_data = await dashboard.get_metrics_json()
        assert isinstance(json_data, str)

        # Should be valid JSON
        import json
        data = json.loads(json_data)
        assert isinstance(data, dict)


class TestOptimizedServiceMixin:
    """Test the OptimizedServiceMixin class."""

    @pytest.fixture
    def service(self):
        """Create test service instance."""
        collector = MetricsCollector()
        class TestService(OptimizedServiceMixin):
            def __init__(self):
                super().__init__(collector)

            async def test_operation(self, delay=0.01):
                await asyncio.sleep(delay)
                return "success"

        return TestService()

    @pytest.mark.asyncio
    async def test_benchmark_operation(self, service):
        """Test benchmarking operations."""
        benchmark = await service.benchmark_operation(
            "test_op", service.test_operation, iterations=3
        )

        assert isinstance(benchmark, PerformanceBenchmark)
        assert benchmark.name == "TestService.test_op"
        assert benchmark.iterations == 3

    @pytest.mark.asyncio
    async def test_optimize_with_metrics(self, service):
        """Test executing operations with metrics."""
        result = await service.optimize_with_metrics(
            "test_operation", service.test_operation, 0.01
        )

        assert result == "success"

        # Check that execution time was recorded
        series = await service._metrics._metrics_collector.get_series("timer:TestService.execution_time")
        assert series is not None

    def test_get_performance_report(self, service):
        """Test getting performance report."""
        report = service.get_performance_report()
        assert isinstance(report, str)


class TestUtilityFunctions:
    """Test utility functions."""

    @pytest.mark.asyncio
    async def test_profile_async_function(self):
        """Test profiling async functions."""
        async def test_func():
            await asyncio.sleep(0.01)
            return 42

        benchmark = await profile_async_function(test_func, iterations=2)
        assert isinstance(benchmark, PerformanceBenchmark)
        assert benchmark.iterations == 2

    def test_profile_sync_function(self):
        """Test profiling sync functions."""
        def test_func():
            time.sleep(0.01)
            return 42

        benchmark = profile_sync_function(test_func, iterations=2)
        assert isinstance(benchmark, PerformanceBenchmark)
        assert benchmark.iterations == 2

    @pytest.mark.asyncio
    async def test_measure_time_context_manager(self):
        """Test measure_time context manager."""
        collector = MetricsCollector()

        async with measure_time(collector, "test_timer", operation="test"):
            await asyncio.sleep(0.01)

        series = await collector.get_series("timer:test_timer")
        assert series is not None
        assert len(series.values) == 1
        assert series.values[0].value > 0


if __name__ == "__main__":
    # Run basic smoke tests
    async def smoke_test():
        print("Running smoke tests...")

        # Test MetricsCollector
        collector = MetricsCollector()
        await collector.record_counter("smoke_test", 1.0)
        print("✓ MetricsCollector working")

        # Test ServiceMetrics
        service_metrics = ServiceMetrics("SmokeTest")
        await service_metrics.record_request("GET", "/health", 200, 0.001)
        print("✓ ServiceMetrics working")

        # Test PerformanceProfiler
        profiler = PerformanceProfiler()

        async def dummy_async():
            return 42

        benchmark = await profiler.benchmark_async(
            "smoke", "test", dummy_async, iterations=2
        )
        print(f"✓ PerformanceProfiler working (ops/sec: {benchmark.operations_per_second:.2f})")

        print("All smoke tests passed!")

    asyncio.run(smoke_test())

