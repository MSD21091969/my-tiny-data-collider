#!/usr/bin/env python3
"""Test script for service caching and advanced features."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from coreservice.service_caching import (
    Cache, ConnectionPool, CircuitBreaker, CircuitBreakerConfig,
    ServiceCache, CachedServiceMixin, CircuitBreakerRegistry
)


async def test_cache():
    """Test cache functionality."""
    print("Testing Cache...")

    cache = Cache[str](max_size=10)
    await cache.put('key1', 'value1')
    await cache.put('key2', 'value2')

    result1 = await cache.get('key1')
    result2 = await cache.get('key2')
    result3 = await cache.get('key3')  # Should be None

    assert result1 == 'value1', f"Expected 'value1', got {result1}"
    assert result2 == 'value2', f"Expected 'value2', got {result2}"
    assert result3 is None, f"Expected None, got {result3}"

    size = await cache.size()
    assert size == 2, f"Expected size 2, got {size}"

    print("✓ Cache tests passed")


async def test_connection_pool():
    """Test connection pool functionality."""
    print("Testing Connection Pool...")

    async def create_conn():
        await asyncio.sleep(0.01)  # Simulate connection creation time
        return f"connection_{id(asyncio.current_task())}"

    pool = ConnectionPool[str](create_conn, max_size=3, min_size=1)
    await pool.initialize()

    # Test acquiring connections
    connections = []
    for i in range(3):
        async with pool.acquire() as conn:
            connections.append(conn)
            print(f"  Acquired connection: {conn}")

    assert len(connections) == 3, f"Expected 3 connections, got {len(connections)}"
    print("✓ Connection pool tests passed")


async def test_circuit_breaker():
    """Test circuit breaker functionality."""
    print("Testing Circuit Breaker...")

    success_count = 0
    failure_count = 0

    async def success_func():
        nonlocal success_count
        success_count += 1
        return f"success_{success_count}"

    async def failure_func():
        nonlocal failure_count
        failure_count += 1
        raise ValueError(f"failure_{failure_count}")

    config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=1.0, success_threshold=2)
    breaker = CircuitBreaker('test', config)

    # Test successful calls
    result1 = await breaker.call(success_func)
    result2 = await breaker.call(success_func)
    assert result1 == "success_1"
    assert result2 == "success_2"
    assert breaker.get_state().name == "CLOSED"

    # Test failures that open the circuit
    try:
        await breaker.call(failure_func)
    except ValueError:
        pass

    try:
        await breaker.call(failure_func)
    except ValueError:
        pass

    # Circuit should now be open
    assert breaker.get_state().name == "OPEN"

    # Try calling when circuit is open
    try:
        await breaker.call(success_func)
        raise AssertionError("Should have raised CircuitBreakerOpenException")
    except Exception as e:
        assert "Circuit breaker test is OPEN" in str(e)

    # Wait for recovery timeout
    await asyncio.sleep(1.1)

    # Circuit should be half-open now, try successes to close it
    result3 = await breaker.call(success_func)
    result4 = await breaker.call(success_func)
    assert result3 == "success_3"
    assert result4 == "success_4"
    assert breaker.get_state().name == "CLOSED"

    print("✓ Circuit breaker tests passed")


async def test_service_cache():
    """Test service cache manager."""
    print("Testing Service Cache Manager...")

    service_cache = ServiceCache()

    # Create caches
    cache1 = service_cache.create_cache("test_cache_1", max_size=5)
    cache2 = service_cache.create_cache("test_cache_2", max_size=10)

    # Test cache operations
    await cache1.put("key1", "value1")
    result = await cache1.get("key1")
    assert result == "value1"

    # Test pool creation
    async def create_conn():
        return "db_connection"

    pool = service_cache.create_pool("test_pool", ConnectionPool, factory=create_conn, max_size=5)
    await pool.initialize()

    async with pool.acquire() as conn:
        assert conn == "db_connection"

    print("✓ Service cache manager tests passed")


async def test_cached_service_mixin():
    """Test cached service mixin."""
    print("Testing Cached Service Mixin...")

    class TestService(CachedServiceMixin):
        def __init__(self):
            super().__init__("test_service")

        async def get_data(self, key: str) -> str:
            # Check cache first
            cached = await self.get_cached(key)
            if cached:
                return f"cached_{cached}"

            # Simulate expensive operation
            await asyncio.sleep(0.1)
            result = f"computed_{key}"

            # Cache result
            await self.set_cached(key, result, ttl=60.0)
            return result

    service = TestService()

    # First call should compute
    result1 = await service.get_data("test1")
    assert result1 == "computed_test1"

    # Second call should use cache
    result2 = await service.get_data("test1")
    assert result2 == "cached_computed_test1"

    print("✓ Cached service mixin tests passed")


async def test_circuit_breaker_registry():
    """Test circuit breaker registry."""
    print("Testing Circuit Breaker Registry...")

    registry = CircuitBreakerRegistry()

    # Get breakers
    breaker1 = registry.get_or_create("service1")
    breaker2 = registry.get_or_create("service1")  # Should return same instance
    breaker3 = registry.get_or_create("service2")

    assert breaker1 is breaker2
    assert breaker1 is not breaker3

    # Test state tracking
    states = registry.get_all_states()
    assert len(states) == 2
    assert all(state.name == "CLOSED" for state in states.values())

    print("✓ Circuit breaker registry tests passed")


async def main():
    """Run all tests."""
    print("🧪 Running Service Caching & Advanced Features Tests\n")

    try:
        await test_cache()
        await test_connection_pool()
        await test_circuit_breaker()
        await test_service_cache()
        await test_cached_service_mixin()
        await test_circuit_breaker_registry()

        print("\n🎉 All tests passed! Service caching implementation is working correctly.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)