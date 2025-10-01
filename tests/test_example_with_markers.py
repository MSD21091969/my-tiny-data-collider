"""
Example test file demonstrating pytest marker usage.

This file shows how to use the test markers defined in pytest.ini
for categorizing and selectively running tests.

Usage examples:
    pytest -m unit                    # Run only unit tests
    pytest -m "not slow"              # Skip slow tests
    pytest -m "firestore"             # Run only Firestore tests
    pytest -m "unit or integration"   # Run unit OR integration tests
    pytest -m "not (firestore or slow)"  # Skip Firestore and slow tests
"""

import pytest


@pytest.mark.unit
def test_fast_unit_test():
    """Example of a fast unit test with no dependencies."""
    assert 1 + 1 == 2


@pytest.mark.unit
def test_another_unit_test():
    """Another fast unit test."""
    result = "hello".upper()
    assert result == "HELLO"


@pytest.mark.integration
@pytest.mark.mock
def test_integration_with_mock():
    """Example of integration test using mock backend."""
    # This would test service integration with mock repository
    assert True


@pytest.mark.firestore
@pytest.mark.slow
def test_firestore_operation():
    """Example of test requiring Firestore connection (slow)."""
    # This would test actual Firestore operations
    pytest.skip("Requires Firestore connection")


@pytest.mark.integration
@pytest.mark.slow
def test_end_to_end_flow():
    """Example of slow end-to-end integration test."""
    # This would test complete workflow
    pytest.skip("E2E test - run manually")


class TestMarkerCombinations:
    """Example test class showing marker combinations."""

    @pytest.mark.unit
    def test_class_unit_test(self):
        """Unit test within a class."""
        assert len([1, 2, 3]) == 3

    @pytest.mark.integration
    @pytest.mark.mock
    def test_class_integration_test(self):
        """Integration test within a class."""
        data = {"key": "value"}
        assert "key" in data
