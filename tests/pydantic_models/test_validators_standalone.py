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

from pydantic_models.base.validators import *


def test_timestamp_validation():
    """Test timestamp ordering validation."""
    print("Testing timestamp validation...")
    
    # Valid ordering
    try:
        validate_timestamp_order("2025-01-01T00:00:00Z", "2025-01-02T00:00:00Z")
        print("  ✓ Valid ISO timestamps")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Unix timestamps
    try:
        validate_timestamp_order(1609459200, 1609545600)
        print("  ✓ Valid Unix timestamps")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Invalid ordering
    try:
        validate_timestamp_order("2025-01-02T00:00:00Z", "2025-01-01T00:00:00Z")
        print("  ✗ Should have raised ValueError for invalid order")
        return False
    except ValueError as e:
        print(f"  ✓ Correctly rejected invalid order")
    
    return True


def test_at_least_one_validation():
    """Test at-least-one validation."""
    print("\nTesting at-least-one validation...")
    
    # Valid: one field present
    try:
        validate_at_least_one(None, "value", None)
        print("  ✓ Accepts when one field is present")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Invalid: all None
    try:
        validate_at_least_one(None, None, None)
        print("  ✗ Should have raised ValueError")
        return False
    except ValueError:
        print("  ✓ Correctly rejected all-None")
    
    return True


def test_mutually_exclusive_validation():
    """Test mutually exclusive validation."""
    print("\nTesting mutually exclusive validation...")
    
    # Valid: only one field
    try:
        validate_mutually_exclusive(None, "value", None)
        print("  ✓ Accepts one field")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Invalid: multiple fields
    try:
        validate_mutually_exclusive("value1", "value2", None)
        print("  ✗ Should have raised ValueError")
        return False
    except ValueError:
        print("  ✓ Correctly rejected multiple fields")
    
    return True


def test_range_validation():
    """Test range validation."""
    print("\nTesting range validation...")
    
    # Valid value
    try:
        validate_range(5, "count", min_value=1, max_value=10)
        print("  ✓ Accepts value in range")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Invalid: too high
    try:
        validate_range(11, "count", min_value=1, max_value=10)
        print("  ✗ Should have raised ValueError")
        return False
    except ValueError:
        print("  ✓ Correctly rejected value above max")
    
    # Invalid: too low
    try:
        validate_range(0, "count", min_value=1, max_value=10)
        print("  ✗ Should have raised ValueError")
        return False
    except ValueError:
        print("  ✓ Correctly rejected value below min")
    
    return True


def test_list_validation():
    """Test list validation."""
    print("\nTesting list validation...")
    
    # Not empty
    try:
        validate_list_not_empty([1, 2, 3], "items")
        print("  ✓ Accepts non-empty list")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Empty list
    try:
        validate_list_not_empty([], "items")
        print("  ✗ Should have raised ValueError")
        return False
    except ValueError:
        print("  ✓ Correctly rejected empty list")
    
    # Unique values
    try:
        validate_list_unique([1, 2, 3], "numbers")
        print("  ✓ Accepts unique values")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Duplicate values
    try:
        validate_list_unique([1, 2, 2, 3], "numbers")
        print("  ✗ Should have raised ValueError")
        return False
    except ValueError:
        print("  ✓ Correctly rejected duplicates")
    
    return True


def test_string_length_validation():
    """Test string length validation."""
    print("\nTesting string length validation...")
    
    # Valid length
    try:
        validate_string_length("hello", "name", min_length=1, max_length=10)
        print("  ✓ Accepts valid length")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Too short
    try:
        validate_string_length("", "name", min_length=1)
        print("  ✗ Should have raised ValueError")
        return False
    except ValueError:
        print("  ✓ Correctly rejected too-short string")
    
    # Too long
    try:
        validate_string_length("toolongstring", "name", max_length=5)
        print("  ✗ Should have raised ValueError")
        return False
    except ValueError:
        print("  ✓ Correctly rejected too-long string")
    
    return True


def test_conditional_required_validation():
    """Test conditional required validation."""
    print("\nTesting conditional required validation...")
    
    # Condition met, field present
    try:
        validate_conditional_required(True, "value", "is_active", "email")
        print("  ✓ Accepts when both present")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Condition not met
    try:
        validate_conditional_required(False, None, "is_active", "email")
        print("  ✓ Accepts when condition not met")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Condition met, field missing
    try:
        validate_conditional_required(True, None, "is_active", "email")
        print("  ✗ Should have raised ValueError")
        return False
    except ValueError:
        print("  ✓ Correctly rejected missing required field")
    
    return True


def test_depends_on_validation():
    """Test dependency validation."""
    print("\nTesting depends-on validation...")
    
    # Both present
    try:
        validate_depends_on("value1", "value2", "field_a", "field_b")
        print("  ✓ Accepts when both present")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Both absent
    try:
        validate_depends_on(None, None, "field_a", "field_b")
        print("  ✓ Accepts when both absent")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Dependent without dependency
    try:
        validate_depends_on("value", None, "field_a", "field_b")
        print("  ✗ Should have raised ValueError")
        return False
    except ValueError:
        print("  ✓ Correctly rejected missing dependency")
    
    return True


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
