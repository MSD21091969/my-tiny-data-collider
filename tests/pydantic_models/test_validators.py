"""
Tests for reusable validation functions.

Tests all validators in pydantic_models.base.validators to ensure:
- Correct validation logic
- Proper error messages
- Edge case handling
- Type flexibility
"""

import sys
from pathlib import Path

# Ensure src is in path for imports
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import pytest
from datetime import datetime

from pydantic_models.base.validators import (
    validate_timestamp_order,
    validate_at_least_one,
    validate_mutually_exclusive,
    validate_conditional_required,
    validate_list_not_empty,
    validate_list_unique,
    validate_range,
    validate_string_length,
    validate_depends_on,
)


class TestTimestampOrderValidation:
    """Test timestamp ordering validation."""
    
    def test_valid_iso_timestamps(self):
        """Test valid ISO timestamp ordering."""
        validate_timestamp_order(
            "2025-01-01T00:00:00Z",
            "2025-01-02T00:00:00Z"
        )
        # Should not raise
    
    def test_valid_unix_timestamps(self):
        """Test valid Unix timestamp ordering."""
        validate_timestamp_order(
            1609459200,  # 2021-01-01
            1609545600   # 2021-01-02
        )
        # Should not raise
    
    def test_equal_timestamps_allowed(self):
        """Test equal timestamps are allowed by default."""
        validate_timestamp_order(
            "2025-01-01T00:00:00Z",
            "2025-01-01T00:00:00Z"
        )
        # Should not raise
    
    def test_equal_timestamps_disallowed(self):
        """Test equal timestamps can be disallowed."""
        with pytest.raises(ValueError, match="must be greater than"):
            validate_timestamp_order(
                "2025-01-01T00:00:00Z",
                "2025-01-01T00:00:00Z",
                allow_equal=False
            )
    
    def test_invalid_order(self):
        """Test invalid timestamp order raises error."""
        with pytest.raises(ValueError, match="must be greater than or equal to"):
            validate_timestamp_order(
                "2025-01-02T00:00:00Z",
                "2025-01-01T00:00:00Z"
            )
    
    def test_custom_field_names_in_error(self):
        """Test custom field names appear in error message."""
        with pytest.raises(ValueError, match="updated_at.*created_at"):
            validate_timestamp_order(
                "2025-01-02T00:00:00Z",
                "2025-01-01T00:00:00Z",
                earlier_field="created_at",
                later_field="updated_at"
            )
    
    def test_invalid_timestamp_format(self):
        """Test invalid timestamp format raises error."""
        with pytest.raises(ValueError, match="Invalid.*timestamp"):
            validate_timestamp_order("invalid", "2025-01-01T00:00:00Z")


class TestAtLeastOneValidation:
    """Test at-least-one validation."""
    
    def test_one_field_present(self):
        """Test validation passes when one field is present."""
        validate_at_least_one(None, "value", None)
        # Should not raise
    
    def test_multiple_fields_present(self):
        """Test validation passes when multiple fields are present."""
        validate_at_least_one("value1", "value2", None)
        # Should not raise
    
    def test_no_fields_present(self):
        """Test validation fails when no fields are present."""
        with pytest.raises(ValueError, match="At least one"):
            validate_at_least_one(None, None, None)
    
    def test_custom_field_names_in_error(self):
        """Test custom field names appear in error message."""
        with pytest.raises(ValueError, match="gmail.*drive.*sheets"):
            validate_at_least_one(
                None, None, None,
                field_names=["gmail", "drive", "sheets"]
            )
    
    def test_custom_error_message(self):
        """Test custom error message is used."""
        with pytest.raises(ValueError, match="Need at least one data source"):
            validate_at_least_one(
                None, None,
                error_message="Need at least one data source"
            )


class TestMutuallyExclusiveValidation:
    """Test mutually exclusive validation."""
    
    def test_no_fields_present(self):
        """Test validation passes when no fields are present."""
        validate_mutually_exclusive(None, None, None)
        # Should not raise
    
    def test_one_field_present(self):
        """Test validation passes when one field is present."""
        validate_mutually_exclusive(None, "value", None)
        # Should not raise
    
    def test_multiple_fields_present(self):
        """Test validation fails when multiple fields are present."""
        with pytest.raises(ValueError, match="Only one"):
            validate_mutually_exclusive("value1", "value2", None)
    
    def test_custom_field_names_in_error(self):
        """Test custom field names appear in error message."""
        with pytest.raises(ValueError, match="tool_id.*method_id"):
            validate_mutually_exclusive(
                "value1", "value2",
                field_names=["tool_id", "method_id"]
            )
    
    def test_custom_error_message(self):
        """Test custom error message is used."""
        with pytest.raises(ValueError, match="Choose only one"):
            validate_mutually_exclusive(
                "a", "b",
                error_message="Choose only one"
            )


class TestConditionalRequiredValidation:
    """Test conditional required validation."""
    
    def test_condition_met_field_present(self):
        """Test validation passes when condition is met and field is present."""
        validate_conditional_required(
            True, "value",
            "is_active", "email"
        )
        # Should not raise
    
    def test_condition_not_met(self):
        """Test validation passes when condition is not met."""
        validate_conditional_required(
            False, None,
            "is_active", "email"
        )
        # Should not raise
    
    def test_condition_met_field_missing(self):
        """Test validation fails when condition is met but field is missing."""
        with pytest.raises(ValueError, match="email is required when is_active is True"):
            validate_conditional_required(
                True, None,
                "is_active", "email"
            )
    
    def test_custom_condition_value(self):
        """Test custom condition value."""
        validate_conditional_required(
            "premium", "payment_method",
            "tier", "payment_info",
            condition_value="premium"
        )
        # Should not raise
        
        with pytest.raises(ValueError, match="payment_info is required"):
            validate_conditional_required(
                "premium", None,
                "tier", "payment_info",
                condition_value="premium"
            )


class TestListNotEmptyValidation:
    """Test list not empty validation."""
    
    def test_valid_list(self):
        """Test validation passes for non-empty list."""
        validate_list_not_empty([1, 2, 3], "items")
        # Should not raise
    
    def test_empty_list(self):
        """Test validation fails for empty list."""
        with pytest.raises(ValueError, match="items must not be empty"):
            validate_list_not_empty([], "items")
    
    def test_none_list(self):
        """Test validation fails for None."""
        with pytest.raises(ValueError, match="items must not be empty"):
            validate_list_not_empty(None, "items")


class TestListUniqueValidation:
    """Test list uniqueness validation."""
    
    def test_unique_simple_list(self):
        """Test validation passes for unique simple list."""
        validate_list_unique([1, 2, 3], "numbers")
        # Should not raise
    
    def test_duplicate_simple_list(self):
        """Test validation fails for duplicate simple list."""
        with pytest.raises(ValueError, match="numbers must have unique values"):
            validate_list_unique([1, 2, 2, 3], "numbers")
    
    def test_unique_dict_list_with_key(self):
        """Test validation passes for unique dict list."""
        validate_list_unique(
            [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}],
            "items",
            key="id"
        )
        # Should not raise
    
    def test_duplicate_dict_list_with_key(self):
        """Test validation fails for duplicate dict list."""
        with pytest.raises(ValueError, match="items must have unique values for 'id'"):
            validate_list_unique(
                [{"id": 1, "name": "a"}, {"id": 1, "name": "b"}],
                "items",
                key="id"
            )


class TestRangeValidation:
    """Test numeric range validation."""
    
    def test_value_in_range(self):
        """Test validation passes for value in range."""
        validate_range(5, "count", min_value=1, max_value=10)
        # Should not raise
    
    def test_value_at_min_inclusive(self):
        """Test validation passes for value at min (inclusive)."""
        validate_range(1, "count", min_value=1, max_value=10)
        # Should not raise
    
    def test_value_at_max_inclusive(self):
        """Test validation passes for value at max (inclusive)."""
        validate_range(10, "count", min_value=1, max_value=10)
        # Should not raise
    
    def test_value_below_min(self):
        """Test validation fails for value below min."""
        with pytest.raises(ValueError, match="count must be >= 1"):
            validate_range(0, "count", min_value=1, max_value=10)
    
    def test_value_above_max(self):
        """Test validation fails for value above max."""
        with pytest.raises(ValueError, match="count must be <= 10"):
            validate_range(11, "count", min_value=1, max_value=10)
    
    def test_exclusive_bounds(self):
        """Test exclusive bounds."""
        with pytest.raises(ValueError, match="count must be > 1"):
            validate_range(1, "count", min_value=1, max_value=10, inclusive=False)
        
        with pytest.raises(ValueError, match="count must be < 10"):
            validate_range(10, "count", min_value=1, max_value=10, inclusive=False)


class TestStringLengthValidation:
    """Test string length validation."""
    
    def test_valid_length(self):
        """Test validation passes for valid length."""
        validate_string_length("hello", "name", min_length=1, max_length=10)
        # Should not raise
    
    def test_empty_string_with_min(self):
        """Test validation fails for empty string with min length."""
        with pytest.raises(ValueError, match="name must be at least 1 characters"):
            validate_string_length("", "name", min_length=1)
    
    def test_string_too_long(self):
        """Test validation fails for string too long."""
        with pytest.raises(ValueError, match="name must be at most 5 characters"):
            validate_string_length("toolong", "name", max_length=5)
    
    def test_exact_length_boundaries(self):
        """Test exact length boundaries."""
        validate_string_length("12345", "name", min_length=5, max_length=5)
        # Should not raise


class TestDependsOnValidation:
    """Test dependency validation."""
    
    def test_both_fields_present(self):
        """Test validation passes when both fields are present."""
        validate_depends_on("value1", "value2", "field_a", "field_b")
        # Should not raise
    
    def test_both_fields_absent(self):
        """Test validation passes when both fields are absent."""
        validate_depends_on(None, None, "field_a", "field_b")
        # Should not raise
    
    def test_only_dependency_present(self):
        """Test validation passes when only dependency is present."""
        validate_depends_on(None, "value", "field_a", "field_b")
        # Should not raise
    
    def test_dependent_without_dependency(self):
        """Test validation fails when dependent is present without dependency."""
        with pytest.raises(ValueError, match="field_a requires field_b to be set"):
            validate_depends_on("value", None, "field_a", "field_b")


class TestValidatorIntegration:
    """Test validators working together in realistic scenarios."""
    
    def test_casefile_validation_scenario(self):
        """Test validators in a casefile-like scenario."""
        # Simulate casefile with at least one data source
        gmail_data = {"messages": []}
        drive_data = None
        sheets_data = None
        
        validate_at_least_one(
            gmail_data, drive_data, sheets_data,
            field_names=["gmail_data", "drive_data", "sheets_data"]
        )
        # Should not raise
        
        # Validate timestamps
        validate_timestamp_order(
            "2025-01-01T00:00:00Z",
            "2025-01-02T00:00:00Z",
            "created_at",
            "updated_at"
        )
        # Should not raise
    
    def test_session_validation_scenario(self):
        """Test validators in a session-like scenario."""
        # Validate session has either tool_id or method_id (not both)
        validate_mutually_exclusive(
            "tool_123", None,
            field_names=["tool_id", "method_id"]
        )
        # Should not raise
        
        # Validate events list is not empty
        events = [{"event": "started"}, {"event": "completed"}]
        validate_list_not_empty(events, "events")
        # Should not raise
        
        # Validate unique event IDs
        event_ids = [1, 2, 3, 4]
        validate_list_unique(event_ids, "event_ids")
        # Should not raise
    
    def test_permission_validation_scenario(self):
        """Test validators in a permission-like scenario."""
        # If expiration is set, it must be in the future
        has_expiration = True
        expiration_time = "2026-01-01T00:00:00Z"
        
        validate_conditional_required(
            has_expiration,
            expiration_time,
            "has_expiration",
            "expiration_time"
        )
        # Should not raise
        
        # Validate permission level is in valid range
        permission_level = 2
        validate_range(permission_level, "permission_level", min_value=0, max_value=3)
        # Should not raise
