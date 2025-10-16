"""
Reusable validation functions for Pydantic models.

This module contains common validation patterns that can be reused across multiple models:
- Timestamp ordering validation
- Data source validation
- Permission validation
- Cross-field consistency checks
- Business rule enforcement

Usage:
    from src.pydantic_models.base.validators import validate_timestamp_order
    
    class MyModel(BaseModel):
        created_at: str
        updated_at: str
        
        @model_validator(mode='after')
        def check_timestamps(self) -> 'MyModel':
            validate_timestamp_order(
                self.created_at,
                self.updated_at,
                'created_at',
                'updated_at'
            )
            return self
"""

from datetime import datetime
from typing import Any, List, Optional, Union

from pydantic import ValidationError


def validate_timestamp_order(
    earlier: Union[str, int, float],
    later: Union[str, int, float],
    earlier_field: str = "created_at",
    later_field: str = "updated_at",
    allow_equal: bool = True,
) -> None:
    """
    Validate that one timestamp comes before (or equal to) another.
    
    Args:
        earlier: The earlier timestamp (ISO string or Unix timestamp)
        later: The later timestamp (ISO string or Unix timestamp)
        earlier_field: Name of the earlier field (for error messages)
        later_field: Name of the later field (for error messages)
        allow_equal: Whether to allow equal timestamps (default: True)
        
    Raises:
        ValueError: If later timestamp is before earlier timestamp
        
    Examples:
        >>> validate_timestamp_order("2025-01-01T00:00:00Z", "2025-01-02T00:00:00Z")
        >>> validate_timestamp_order(1609459200, 1609545600)  # Unix timestamps
    """
    # Convert to datetime objects for comparison
    earlier_dt = _parse_timestamp(earlier, earlier_field)
    later_dt = _parse_timestamp(later, later_field)
    
    if allow_equal:
        if later_dt < earlier_dt:
            raise ValueError(
                f"{earlier_field} must be <= {later_field} "
                f"({earlier_field}={earlier}, {later_field}={later})"
            )
    else:
        if later_dt <= earlier_dt:
            raise ValueError(
                f"{earlier_field} must be < {later_field} "
                f"({earlier_field}={earlier}, {later_field}={later})"
            )


def validate_at_least_one(
    *fields: Optional[Any],
    field_names: Optional[List[str]] = None,
    error_message: Optional[str] = None,
) -> None:
    """
    Validate that at least one of the provided fields has a non-None value.
    
    Args:
        *fields: Field values to check
        field_names: Names of fields (for error message)
        error_message: Custom error message (overrides default)
        
    Raises:
        ValueError: If all fields are None
        
    Examples:
        >>> validate_at_least_one(None, "value", None, field_names=["a", "b", "c"])
        >>> validate_at_least_one(None, None, error_message="Need at least one data source")
    """
    if not any(field is not None for field in fields):
        if error_message:
            raise ValueError(error_message)
        elif field_names:
            raise ValueError(f"At least one of {field_names} must be provided")
        else:
            raise ValueError("At least one field must be provided")


def validate_mutually_exclusive(
    *fields: Optional[Any],
    field_names: Optional[List[str]] = None,
    error_message: Optional[str] = None,
) -> None:
    """
    Validate that at most one of the provided fields has a non-None value.
    
    Args:
        *fields: Field values to check
        field_names: Names of fields (for error message)
        error_message: Custom error message (overrides default)
        
    Raises:
        ValueError: If more than one field is non-None
        
    Examples:
        >>> validate_mutually_exclusive(None, "value", None, field_names=["a", "b", "c"])
        >>> validate_mutually_exclusive("a", "b", error_message="Choose only one")
    """
    non_none_count = sum(1 for field in fields if field is not None)
    
    if non_none_count > 1:
        if error_message:
            raise ValueError(error_message)
        elif field_names:
            raise ValueError(f"Only one of {field_names} can be provided")
        else:
            raise ValueError("Only one field can be provided")


def validate_conditional_required(
    condition_field: Any,
    required_field: Any,
    condition_field_name: str,
    required_field_name: str,
    condition_value: Any = True,
) -> None:
    """
    Validate that a field is required when a condition field has a specific value.
    
    Args:
        condition_field: The field that determines if validation applies
        required_field: The field that must be non-None when condition is met
        condition_field_name: Name of condition field (for error message)
        required_field_name: Name of required field (for error message)
        condition_value: Value that triggers the requirement (default: True)
        
    Raises:
        ValueError: If condition is met but required field is None
        
    Examples:
        >>> validate_conditional_required(True, "value", "is_active", "email", True)
        >>> validate_conditional_required("premium", None, "tier", "payment_method", "premium")
    """
    if condition_field == condition_value and required_field is None:
        raise ValueError(
            f"{required_field_name} is required when {condition_field_name} is {condition_value}"
        )


def validate_list_not_empty(
    value: Optional[List[Any]],
    field_name: str = "list",
) -> None:
    """
    Validate that a list is not None and not empty.
    
    Args:
        value: The list to validate
        field_name: Name of field (for error message)
        
    Raises:
        ValueError: If list is None or empty
        
    Examples:
        >>> validate_list_not_empty([1, 2, 3], "items")
        >>> validate_list_not_empty([], "items")  # Raises ValueError
    """
    if value is None or len(value) == 0:
        raise ValueError(f"{field_name} must not be empty")


def validate_list_unique(
    value: List[Any],
    field_name: str = "list",
    key: Optional[str] = None,
) -> None:
    """
    Validate that all items in a list are unique.
    
    Args:
        value: The list to validate
        field_name: Name of field (for error message)
        key: If items are dicts, the key to check for uniqueness
        
    Raises:
        ValueError: If list contains duplicate items
        
    Examples:
        >>> validate_list_unique([1, 2, 3], "numbers")
        >>> validate_list_unique([{"id": 1}, {"id": 2}], "items", key="id")
        >>> validate_list_unique([1, 2, 2], "numbers")  # Raises ValueError
    """
    if key:
        # For list of dicts, check uniqueness of specific key
        keys = [item.get(key) if isinstance(item, dict) else getattr(item, key, None) 
                for item in value]
        if len(keys) != len(set(keys)):
            raise ValueError(f"{field_name} must have unique values for '{key}'")
    else:
        # For simple lists, check direct uniqueness
        if len(value) != len(set(value)):
            raise ValueError(f"{field_name} must have unique values")


def validate_range(
    value: Union[int, float],
    field_name: str,
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    inclusive: bool = True,
) -> None:
    """
    Validate that a numeric value is within a specified range.
    
    Args:
        value: The value to validate
        field_name: Name of field (for error message)
        min_value: Minimum allowed value (optional)
        max_value: Maximum allowed value (optional)
        inclusive: Whether bounds are inclusive (default: True)
        
    Raises:
        ValueError: If value is outside the specified range
        
    Examples:
        >>> validate_range(5, "count", min_value=1, max_value=10)
        >>> validate_range(11, "count", min_value=1, max_value=10)  # Raises ValueError
    """
    if min_value is not None:
        if inclusive and value < min_value:
            raise ValueError(f"{field_name} must be >= {min_value}, got {value}")
        elif not inclusive and value <= min_value:
            raise ValueError(f"{field_name} must be > {min_value}, got {value}")
    
    if max_value is not None:
        if inclusive and value > max_value:
            raise ValueError(f"{field_name} must be <= {max_value}, got {value}")
        elif not inclusive and value >= max_value:
            raise ValueError(f"{field_name} must be < {max_value}, got {value}")


def validate_string_length(
    value: str,
    field_name: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
) -> None:
    """
    Validate that a string length is within specified bounds.
    
    Args:
        value: The string to validate
        field_name: Name of field (for error message)
        min_length: Minimum allowed length (optional)
        max_length: Maximum allowed length (optional)
        
    Raises:
        ValueError: If string length is outside bounds
        
    Examples:
        >>> validate_string_length("hello", "name", min_length=1, max_length=10)
        >>> validate_string_length("", "name", min_length=1)  # Raises ValueError
    """
    length = len(value)
    
    if min_length is not None and length < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters, got {length}")
    
    if max_length is not None and length > max_length:
        raise ValueError(f"{field_name} must be at most {max_length} characters, got {length}")


def validate_depends_on(
    dependent_field: Any,
    dependency_field: Any,
    dependent_field_name: str,
    dependency_field_name: str,
) -> None:
    """
    Validate that if a dependent field is set, its dependency is also set.
    
    Args:
        dependent_field: The field that depends on another
        dependency_field: The field that must be set first
        dependent_field_name: Name of dependent field (for error message)
        dependency_field_name: Name of dependency field (for error message)
        
    Raises:
        ValueError: If dependent field is set but dependency is not
        
    Examples:
        >>> validate_depends_on("value", "other", "field_a", "field_b")
        >>> validate_depends_on("value", None, "field_a", "field_b")  # Raises ValueError
    """
    if dependent_field is not None and dependency_field is None:
        raise ValueError(
            f"{dependent_field_name} requires {dependency_field_name} to be set"
        )


def validate_timestamp_in_range(
    timestamp: Union[str, int, float],
    min_timestamp: Optional[Union[str, int, float]] = None,
    max_timestamp: Optional[Union[str, int, float]] = None,
    field_name: str = "timestamp",
) -> None:
    """
    Validate that a timestamp falls within a specified range.
    
    Args:
        timestamp: The timestamp to validate
        min_timestamp: Minimum allowed timestamp (inclusive)
        max_timestamp: Maximum allowed timestamp (inclusive)
        field_name: Name of field (for error messages)
        
    Raises:
        ValueError: If timestamp is outside the range
        
    Examples:
        >>> validate_timestamp_in_range("2025-06-01T00:00:00Z", "2025-01-01T00:00:00Z", "2025-12-31T23:59:59Z")
    """
    dt = _parse_timestamp(timestamp, field_name)
    
    if min_timestamp is not None:
        min_dt = _parse_timestamp(min_timestamp, "min_timestamp")
        if dt < min_dt:
            raise ValueError(f"{field_name} ({timestamp}) must be >= {min_timestamp}")
    
    if max_timestamp is not None:
        max_dt = _parse_timestamp(max_timestamp, "max_timestamp")
        if dt > max_dt:
            raise ValueError(f"{field_name} ({timestamp}) must be <= {max_timestamp}")


def validate_email_domain(
    email: str,
    allowed_domains: Optional[List[str]] = None,
    blocked_domains: Optional[List[str]] = None,
    field_name: str = "email",
) -> None:
    """
    Validate email domain against whitelist/blacklist.
    
    Args:
        email: Email address to validate
        allowed_domains: List of allowed domains (if None, all allowed)
        blocked_domains: List of blocked domains (checked after allowed_domains)
        field_name: Name of field (for error messages)
        
    Raises:
        ValueError: If domain is not allowed or is blocked
        
    Examples:
        >>> validate_email_domain("user@example.com", allowed_domains=["example.com"])
        >>> validate_email_domain("user@spam.com", blocked_domains=["spam.com"])  # Raises
    """
    if "@" not in email:
        raise ValueError(f"Invalid email format for {field_name}: {email}")
    
    domain = email.split("@")[-1].lower()
    
    # Check allowed domains (whitelist)
    if allowed_domains:
        if not any(domain == allowed.lower() for allowed in allowed_domains):
            raise ValueError(
                f"Email domain '{domain}' not in allowed domains: {allowed_domains}"
            )
    
    # Check blocked domains (blacklist)
    if blocked_domains:
        if any(domain == blocked.lower() for blocked in blocked_domains):
            raise ValueError(
                f"Email domain '{domain}' is blocked"
            )


def validate_url_domain(
    url: str,
    allowed_domains: Optional[List[str]] = None,
    blocked_domains: Optional[List[str]] = None,
    field_name: str = "url",
) -> None:
    """
    Validate URL domain against whitelist/blacklist.
    
    Args:
        url: URL to validate
        allowed_domains: List of allowed domains (if None, all allowed)
        blocked_domains: List of blocked domains (checked after allowed_domains)
        field_name: Name of field (for error messages)
        
    Raises:
        ValueError: If domain is not allowed or is blocked
        
    Examples:
        >>> validate_url_domain("https://example.com/path", allowed_domains=["example.com"])
        >>> validate_url_domain("https://malicious.com", blocked_domains=["malicious.com"])  # Raises
    """
    try:
        # Extract domain from URL
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if not domain:
            raise ValueError(f"Cannot extract domain from URL: {url}")
        
        # Check allowed domains (whitelist)
        if allowed_domains:
            if not any(domain == allowed.lower() or domain.endswith(f".{allowed.lower()}") for allowed in allowed_domains):
                raise ValueError(
                    f"URL domain '{domain}' not in allowed domains: {allowed_domains}"
                )
        
        # Check blocked domains (blacklist)
        if blocked_domains:
            if any(domain == blocked.lower() or domain.endswith(f".{blocked.lower()}") for blocked in blocked_domains):
                raise ValueError(
                    f"URL domain '{domain}' is blocked"
                )
    except Exception as e:
        raise ValueError(f"Invalid URL for {field_name}: {url}") from e


# Helper functions

def _parse_timestamp(
    timestamp: Union[str, int, float],
    field_name: str,
) -> datetime:
    """
    Parse a timestamp into a datetime object.
    
    Args:
        timestamp: ISO string or Unix timestamp
        field_name: Name of field (for error messages)
        
    Returns:
        datetime object
        
    Raises:
        ValueError: If timestamp cannot be parsed
    """
    if isinstance(timestamp, str):
        try:
            # Try parsing ISO format
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid ISO timestamp for {field_name}: {timestamp}") from e
    
    elif isinstance(timestamp, (int, float)):
        try:
            # Unix timestamp
            return datetime.fromtimestamp(timestamp)
        except (ValueError, OSError) as e:
            raise ValueError(f"Invalid Unix timestamp for {field_name}: {timestamp}") from e
    
    else:
        raise ValueError(f"Timestamp for {field_name} must be string or number, got {type(timestamp)}")


# Re-export for convenience
__all__ = [
    "validate_timestamp_order",
    "validate_at_least_one",
    "validate_mutually_exclusive",
    "validate_conditional_required",
    "validate_list_not_empty",
    "validate_list_unique",
    "validate_range",
    "validate_string_length",
    "validate_depends_on",
    "validate_timestamp_in_range",
    "validate_email_domain",
    "validate_url_domain",
]
