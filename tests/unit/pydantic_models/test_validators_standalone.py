"""
Standalone validator testing script.

This script tests all validators without pytest to avoid import path issues.
Run directly: python tests/pydantic_models/test_validators_standalone.py
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.pydantic_models.base.validators import *


def test_timestamp_validation():
    """Test timestamp ordering validation."""
    print("Testing timestamp validation...")
    
    # Valid ordering
    validate_timestamp_order("2025-01-01T00:00:00Z", "2025-01-02T00:00:00Z")
    print("  ✓ Valid ISO timestamps")
    
    # Unix timestamps
    validate_timestamp_order(1609459200, 1609545600)
    print("  ✓ Valid Unix timestamps")
    
    # Invalid ordering
    try:
        validate_timestamp_order("2025-01-02T00:00:00Z", "2025-01-01T00:00:00Z")
        assert False, "Should have raised ValueError for invalid order"
    except ValueError:
        print(f"  ✓ Correctly rejected invalid order")


def test_at_least_one_validation():
    """Test at-least-one validation."""
    print("\nTesting at-least-one validation...")
    
    # Valid: one field present
    validate_at_least_one(None, "value", None)
    print("  ✓ Accepts when one field is present")
    
    # Invalid: all None
    try:
        validate_at_least_one(None, None, None)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✓ Correctly rejected all-None")


def test_mutually_exclusive_validation():
    """Test mutually exclusive validation."""
    print("\nTesting mutually exclusive validation...")
    
    # Valid: only one field
    validate_mutually_exclusive(None, "value", None)
    print("  ✓ Accepts one field")
    
    # Invalid: multiple fields
    try:
        validate_mutually_exclusive("value1", "value2", None)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✓ Correctly rejected multiple fields")


def test_range_validation():
    """Test range validation."""
    print("\nTesting range validation...")
    
    # Valid value
    validate_range(5, "count", min_value=1, max_value=10)
    print("  ✓ Accepts value in range")
    
    # Invalid: too high
    try:
        validate_range(11, "count", min_value=1, max_value=10)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✓ Correctly rejected value above max")
    
    # Invalid: too low
    try:
        validate_range(0, "count", min_value=1, max_value=10)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✓ Correctly rejected value below min")


def test_list_validation():
    """Test list validation."""
    print("\nTesting list validation...")
    
    # Not empty
    validate_list_not_empty([1, 2, 3], "items")
    print("  ✓ Accepts non-empty list")
    
    # Empty list
    try:
        validate_list_not_empty([], "items")
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✓ Correctly rejected empty list")
    
    # Unique values
    validate_list_unique([1, 2, 3], "numbers")
    print("  ✓ Accepts unique values")
    
    # Duplicate values
    try:
        validate_list_unique([1, 2, 2, 3], "numbers")
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✓ Correctly rejected duplicates")


def test_string_length_validation():
    """Test string length validation."""
    print("\nTesting string length validation...")
    
    # Valid length
    validate_string_length("hello", "name", min_length=1, max_length=10)
    print("  ✓ Accepts valid length")
    
    # Too short
    try:
        validate_string_length("", "name", min_length=1)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✓ Correctly rejected too-short string")
    
    # Too long
    try:
        validate_string_length("toolongstring", "name", max_length=5)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✓ Correctly rejected too-long string")


def test_conditional_required_validation():
    """Test conditional required validation."""
    print("\nTesting conditional required validation...")
    
    # Condition met, field present
    validate_conditional_required(True, "value", "is_active", "email")
    print("  ✓ Accepts when both present")
    
    # Condition not met
    validate_conditional_required(False, None, "is_active", "email")
    print("  ✓ Accepts when condition not met")
    
    # Condition met, field missing
    try:
        validate_conditional_required(True, None, "is_active", "email")
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✓ Correctly rejected missing required field")


def test_depends_on_validation():
    """Test dependency validation."""
    print("\nTesting depends-on validation...")
    
    # Both present
    validate_depends_on("value1", "value2", "field_a", "field_b")
    print("  ✓ Accepts when both present")
    
    # Both absent
    validate_depends_on(None, None, "field_a", "field_b")
    print("  ✓ Accepts when both absent")
    
    # Dependent without dependency
    try:
        validate_depends_on("value", None, "field_a", "field_b")
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✓ Correctly rejected missing dependency")


def main():
    """Run all validator tests."""
    print("=" * 60)
    print("VALIDATOR TESTING SUITE")
    print("=" * 60)
    
    tests = [
        test_timestamp_validation,
        test_at_least_one_validation,
        test_mutually_exclusive_validation,
        test_range_validation,
        test_list_validation,
        test_string_length_validation,
        test_conditional_required_validation,
        test_depends_on_validation,
    ]
    
    results = []
    for test_func in tests:
        result = test_func()
        results.append((test_func.__name__, result))
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓✓✓ ALL VALIDATORS WORKING CORRECTLY! ✓✓✓")
        return 0
    else:
        print("✗✗✗ SOME TESTS FAILED ✗✗✗")
        return 1


if __name__ == "__main__":
    exit(main())
