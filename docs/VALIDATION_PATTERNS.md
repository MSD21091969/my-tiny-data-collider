# Validation Patterns and Migration Guide

**Last Updated:** January 2025  
**Branch:** feature/pydantic-enhancement

---

## Overview

This guide covers the new validation infrastructure added to the my-tiny-data-collider project, including custom types, reusable validators, and best practices for creating new models.

---

## Table of Contents

1. [Custom Types Library](#custom-types-library)
2. [Reusable Validators](#reusable-validators)
3. [Migration Guide](#migration-guide)
4. [Best Practices](#best-practices)
5. [Common Patterns](#common-patterns)
6. [Troubleshooting](#troubleshooting)

---

## Custom Types Library

### Location
`src/pydantic_models/base/custom_types.py`

### Philosophy
Custom types eliminate duplicate validation code and provide consistent, type-safe validation across all models.

### ID Types

```python
from src.pydantic_models.base.custom_types import (
    CasefileId, ToolSessionId, ChatSessionId, SessionId
)

class MyModel(BaseModel):
    casefile_id: CasefileId          # UUID validation + lowercase normalization
    tool_session_id: ToolSessionId   # UUID validation + lowercase normalization
    chat_session_id: ChatSessionId   # UUID validation + lowercase normalization
    session_id: SessionId            # UUID validation + lowercase normalization
```

**Features:**
- Validates UUID format
- Automatically converts to lowercase
- Clear error messages: "Invalid casefile_id format. Must be a valid UUID."

### String Types

```python
from src.pydantic_models.base.custom_types import (
    NonEmptyString, ShortString, MediumString, LongString
)

class MyModel(BaseModel):
    name: ShortString        # 1-200 characters
    description: MediumString # 1-1000 characters
    content: LongString      # 1-10000 characters
    required_field: NonEmptyString  # At least 1 character
```

**When to use:**
- `NonEmptyString` - Any field that cannot be empty
- `ShortString` - Titles, names, labels (≤200 chars)
- `MediumString` - Descriptions, summaries (≤1000 chars)
- `LongString` - Content, notes, detailed text (≤10000 chars)

### Numeric Types

```python
from src.pydantic_models.base.custom_types import (
    PositiveInt, NonNegativeInt, PositiveFloat, NonNegativeFloat,
    Percentage, FileSizeBytes
)

class MyModel(BaseModel):
    count: PositiveInt              # Must be > 0
    index: NonNegativeInt           # Must be >= 0
    rate: PositiveFloat             # Must be > 0.0
    offset: NonNegativeFloat        # Must be >= 0.0
    completion: Percentage          # 0-100
    file_size: FileSizeBytes        # Non-negative integer (bytes)
```

**When to use:**
- `PositiveInt` - Counts, quantities (must be > 0)
- `NonNegativeInt` - Indexes, offsets (can be 0)
- `PositiveFloat` - Rates, prices (must be > 0.0)
- `NonNegativeFloat` - Measurements (can be 0.0)
- `Percentage` - Percentages (0-100)
- `FileSizeBytes` - File sizes in bytes

### Timestamp Types

```python
from src.pydantic_models.base.custom_types import IsoTimestamp

class MyModel(BaseModel):
    created_at: IsoTimestamp   # ISO 8601 format (e.g., "2025-01-15T10:30:00Z")
    updated_at: IsoTimestamp
    deleted_at: IsoTimestamp | None = None
```

**Features:**
- Validates ISO 8601 format
- Supports timezone-aware and timezone-naive
- Example: "2025-01-15T10:30:00Z" or "2025-01-15T10:30:00"

### Email and URL Types

```python
from src.pydantic_models.base.custom_types import EmailAddress, UrlString

class MyModel(BaseModel):
    email: EmailAddress    # Valid email format
    website: UrlString     # Valid URL format
    contacts: EmailList    # List of valid emails
```

**Features:**
- `EmailAddress` - Validates email format (uses Pydantic's EmailStr)
- `UrlString` - Validates URL format (uses Pydantic's HttpUrl)
- `EmailList` - List of valid email addresses

### Collection Types

```python
from src.pydantic_models.base.custom_types import TagList, EmailList

class MyModel(BaseModel):
    tags: TagList       # List of non-empty strings
    recipients: EmailList  # List of valid emails
```

**Features:**
- `TagList` - List with at least one non-empty string
- `EmailList` - List with at least one valid email

---

## Reusable Validators

### Location
`src/pydantic_models/base/validators.py`

### Philosophy
Reusable validators extract common validation patterns into functions that can be used in any `@model_validator`.

### Timestamp Ordering

```python
from src.pydantic_models.base.validators import validate_timestamp_order

@model_validator(mode='after')
def validate_timestamps(self) -> 'MyModel':
    # Ensure created_at <= updated_at
    validate_timestamp_order(self, 'created_at', 'updated_at')
    return self
```

**Features:**
- Supports ISO 8601 strings and Unix timestamps
- Handles None values gracefully
- Clear error messages

**Advanced usage:**
```python
# Allow equal timestamps
validate_timestamp_order(self, 'start_time', 'end_time', allow_equal=True)

# Strict ordering (not equal)
validate_timestamp_order(self, 'start_time', 'end_time', allow_equal=False)
```

### At Least One Required

```python
from src.pydantic_models.base.validators import validate_at_least_one

@model_validator(mode='after')
def validate_contact_methods(self) -> 'MyModel':
    # At least one contact method required
    validate_at_least_one(
        self, 
        ['email', 'phone', 'address'],
        message="At least one contact method (email, phone, or address) is required"
    )
    return self
```

**Use cases:**
- Contact information (email OR phone OR address)
- Data sources (at least one data source must be provided)
- Search criteria (at least one filter required)

### Mutually Exclusive

```python
from src.pydantic_models.base.validators import validate_mutually_exclusive

@model_validator(mode='after')
def validate_payment_method(self) -> 'MyModel':
    # Only one payment method allowed
    validate_mutually_exclusive(
        self,
        ['credit_card', 'paypal', 'bank_transfer'],
        message="Only one payment method can be specified"
    )
    return self
```

**Use cases:**
- Payment methods (only one allowed)
- Authentication methods (password OR token OR certificate)
- Output formats (json OR xml OR csv)

### Conditional Required

```python
from src.pydantic_models.base.validators import validate_conditional_required

@model_validator(mode='after')
def validate_shipping(self) -> 'MyModel':
    # If requires_shipping is True, shipping_address is required
    validate_conditional_required(
        self,
        condition_field='requires_shipping',
        condition_value=True,
        required_field='shipping_address',
        message="Shipping address is required when requires_shipping is True"
    )
    return self
```

**Use cases:**
- Conditional requirements (if A then B required)
- Feature flags (if feature enabled, config required)
- Status-dependent fields (if status=approved, approval_date required)

### List Validation

```python
from src.pydantic_models.base.validators import (
    validate_list_not_empty,
    validate_list_unique
)

@model_validator(mode='after')
def validate_tags(self) -> 'MyModel':
    # Ensure tags list is not empty
    validate_list_not_empty(self, 'tags', "Tags list cannot be empty")
    
    # Ensure all tags are unique
    validate_list_unique(self, 'tags', "Tags must be unique")
    return self
```

**Advanced usage:**
```python
# Unique by dictionary key
validate_list_unique(self, 'permissions', key='user_id', 
                    message="Each user can only have one permission entry")
```

### Range Validation

```python
from src.pydantic_models.base.validators import validate_range

@model_validator(mode='after')
def validate_age(self) -> 'MyModel':
    # Age must be between 18 and 120 (inclusive)
    validate_range(self, 'age', min_value=18, max_value=120, inclusive=True)
    return self
```

**Advanced usage:**
```python
# Exclusive bounds (18 < age < 120)
validate_range(self, 'age', min_value=18, max_value=120, inclusive=False)

# Only minimum
validate_range(self, 'age', min_value=18)

# Only maximum
validate_range(self, 'age', max_value=120)
```

### String Length Validation

```python
from src.pydantic_models.base.validators import validate_string_length

@model_validator(mode='after')
def validate_password(self) -> 'MyModel':
    # Password must be 8-50 characters
    validate_string_length(self, 'password', min_length=8, max_length=50)
    return self
```

### Field Dependencies

```python
from src.pydantic_models.base.validators import validate_depends_on

@model_validator(mode='after')
def validate_dependencies(self) -> 'MyModel':
    # If discount_code is provided, discount_amount must also be provided
    validate_depends_on(
        self,
        dependent_field='discount_code',
        required_field='discount_amount',
        message="discount_amount is required when discount_code is provided"
    )
    return self
```

---

## Migration Guide

### Before: Duplicate Validation Code

```python
class CasefileMetadata(BaseModel):
    casefile_id: str
    title: str
    description: str | None = None
    tags: list[str] = []
    created_at: str
    updated_at: str
    
    @field_validator('casefile_id')
    @classmethod
    def validate_casefile_id(cls, v: str) -> str:
        try:
            UUID(v)
        except ValueError:
            raise ValueError("Invalid casefile_id format. Must be a valid UUID.")
        return v.lower()
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or len(v) > 200:
            raise ValueError("Title must be between 1 and 200 characters")
        return v
    
    @model_validator(mode='after')
    def validate_timestamps(self) -> 'CasefileMetadata':
        if self.created_at and self.updated_at:
            try:
                created = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
                updated = datetime.fromisoformat(self.updated_at.replace('Z', '+00:00'))
                if created > updated:
                    raise ValueError("created_at cannot be after updated_at")
            except ValueError as e:
                raise ValueError(f"Invalid timestamp format: {e}")
        return self
```

### After: Using Custom Types and Validators

```python
from src.pydantic_models.base.custom_types import (
    CasefileId, ShortString, MediumString, TagList, IsoTimestamp
)
from src.pydantic_models.base.validators import validate_timestamp_order

class CasefileMetadata(BaseModel):
    casefile_id: CasefileId
    title: ShortString
    description: MediumString | None = None
    tags: TagList = []
    created_at: IsoTimestamp
    updated_at: IsoTimestamp
    
    @model_validator(mode='after')
    def validate_timestamps(self) -> 'CasefileMetadata':
        validate_timestamp_order(self, 'created_at', 'updated_at')
        return self
```

**Lines of code:** 40 → 15 (62% reduction)  
**Validation features:** Same functionality, more maintainable

### Migration Checklist

When migrating existing models:

1. ✅ **Identify validation patterns**
   - Look for `@field_validator` decorators
   - Look for `@model_validator` decorators
   - Identify common validation logic

2. ✅ **Replace with custom types**
   - UUID validation → `CasefileId`, `ToolSessionId`, etc.
   - String length validation → `ShortString`, `MediumString`, `LongString`
   - Numeric validation → `PositiveInt`, `NonNegativeInt`
   - Timestamp validation → `IsoTimestamp`

3. ✅ **Extract reusable validators**
   - Timestamp ordering → `validate_timestamp_order`
   - At least one field → `validate_at_least_one`
   - Mutual exclusivity → `validate_mutually_exclusive`

4. ✅ **Test the migration**
   - Run existing tests
   - Verify error messages are clear
   - Check edge cases

---

## Best Practices

### 1. Prefer Custom Types Over Field Validators

**❌ Don't:**
```python
@field_validator('title')
@classmethod
def validate_title(cls, v: str) -> str:
    if not v or len(v) > 200:
        raise ValueError("Title must be between 1 and 200 characters")
    return v
```

**✅ Do:**
```python
from src.pydantic_models.base.custom_types import ShortString

title: ShortString
```

### 2. Use Reusable Validators for Model-Level Validation

**❌ Don't:**
```python
@model_validator(mode='after')
def validate_timestamps(self) -> 'MyModel':
    if self.created_at and self.updated_at:
        created = datetime.fromisoformat(self.created_at)
        updated = datetime.fromisoformat(self.updated_at)
        if created > updated:
            raise ValueError("created_at cannot be after updated_at")
    return self
```

**✅ Do:**
```python
from src.pydantic_models.base.validators import validate_timestamp_order

@model_validator(mode='after')
def validate_timestamps(self) -> 'MyModel':
    validate_timestamp_order(self, 'created_at', 'updated_at')
    return self
```

### 3. Combine Custom Types with Reusable Validators

```python
from src.pydantic_models.base.custom_types import (
    CasefileId, ShortString, IsoTimestamp, TagList
)
from src.pydantic_models.base.validators import (
    validate_timestamp_order, validate_at_least_one
)

class CasefileModel(BaseModel):
    casefile_id: CasefileId
    title: ShortString
    tags: TagList
    created_at: IsoTimestamp
    updated_at: IsoTimestamp
    
    # Data sources
    gmail_messages: list[str] = []
    drive_files: list[str] = []
    sheet_data: list[str] = []
    
    @model_validator(mode='after')
    def validate_model(self) -> 'CasefileModel':
        # Timestamp ordering
        validate_timestamp_order(self, 'created_at', 'updated_at')
        
        # At least one data source
        validate_at_least_one(
            self,
            ['gmail_messages', 'drive_files', 'sheet_data'],
            message="Casefile must have at least one data source"
        )
        
        return self
```

### 4. Add JSON Schema Examples

```python
class MyModel(BaseModel):
    casefile_id: CasefileId = Field(
        ...,
        description="Unique identifier for the casefile",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]
    )
    title: ShortString = Field(
        ...,
        description="Casefile title",
        examples=["Q4 2024 Financial Review"]
    )
```

### 5. Document Complex Validation Logic

```python
@model_validator(mode='after')
def validate_business_rules(self) -> 'MyModel':
    """
    Validates casefile business rules:
    1. created_at must be before updated_at
    2. At least one data source (gmail_messages, drive_files, or sheet_data)
    3. If archived=True, archived_at must be provided
    """
    validate_timestamp_order(self, 'created_at', 'updated_at')
    
    validate_at_least_one(
        self,
        ['gmail_messages', 'drive_files', 'sheet_data'],
        message="Casefile must have at least one data source"
    )
    
    validate_conditional_required(
        self,
        condition_field='archived',
        condition_value=True,
        required_field='archived_at',
        message="archived_at is required when archived=True"
    )
    
    return self
```

---

## Common Patterns

### Pattern 1: Entity Model with Timestamps

```python
from src.pydantic_models.base.custom_types import (
    CasefileId, ShortString, IsoTimestamp
)
from src.pydantic_models.base.validators import validate_timestamp_order

class EntityModel(BaseModel):
    id: CasefileId
    name: ShortString
    created_at: IsoTimestamp
    updated_at: IsoTimestamp
    
    @model_validator(mode='after')
    def validate_timestamps(self) -> 'EntityModel':
        validate_timestamp_order(self, 'created_at', 'updated_at')
        return self
```

### Pattern 2: Request Payload with Conditional Fields

```python
from src.pydantic_models.base.custom_types import ShortString, PositiveInt
from src.pydantic_models.base.validators import validate_conditional_required

class SearchRequest(BaseModel):
    query: ShortString | None = None
    advanced_mode: bool = False
    advanced_filters: dict | None = None
    
    limit: PositiveInt = 10
    offset: NonNegativeInt = 0
    
    @model_validator(mode='after')
    def validate_advanced_mode(self) -> 'SearchRequest':
        validate_conditional_required(
            self,
            condition_field='advanced_mode',
            condition_value=True,
            required_field='advanced_filters',
            message="advanced_filters required when advanced_mode=True"
        )
        return self
```

### Pattern 3: Configuration Model with Mutual Exclusivity

```python
from src.pydantic_models.base.custom_types import PositiveInt, UrlString
from src.pydantic_models.base.validators import (
    validate_mutually_exclusive, validate_at_least_one
)

class DataSourceConfig(BaseModel):
    # Data sources (mutually exclusive)
    file_path: str | None = None
    url: UrlString | None = None
    database_query: str | None = None
    
    # Common config
    max_records: PositiveInt = 1000
    
    @model_validator(mode='after')
    def validate_data_source(self) -> 'DataSourceConfig':
        # At least one data source
        validate_at_least_one(
            self,
            ['file_path', 'url', 'database_query'],
            message="At least one data source must be specified"
        )
        
        # Only one data source
        validate_mutually_exclusive(
            self,
            ['file_path', 'url', 'database_query'],
            message="Only one data source can be specified"
        )
        
        return self
```

### Pattern 4: List Model with Uniqueness

```python
from src.pydantic_models.base.custom_types import EmailAddress, ShortString
from src.pydantic_models.base.validators import (
    validate_list_not_empty, validate_list_unique
)

class Permission(BaseModel):
    user_email: EmailAddress
    role: ShortString
    granted_at: IsoTimestamp

class ACLModel(BaseModel):
    permissions: list[Permission] = []
    
    @model_validator(mode='after')
    def validate_permissions(self) -> 'ACLModel':
        validate_list_not_empty(self, 'permissions', 
                               "At least one permission required")
        
        validate_list_unique(self, 'permissions', key='user_email',
                           message="Each user can only have one permission")
        
        return self
```

---

## Troubleshooting

### Issue: Import Errors

**Problem:**
```python
ImportError: cannot import name 'CasefileId' from 'src.pydantic_models.base.custom_types'
```

**Solution:**
Ensure you're importing from the correct path:
```python
from src.pydantic_models.base.custom_types import CasefileId
```

### Issue: Validation Error Not Clear

**Problem:**
```
ValueError: Validation error
```

**Solution:**
Add custom error messages to validators:
```python
validate_timestamp_order(
    self, 
    'created_at', 
    'updated_at',
    message="Creation date cannot be after update date"
)
```

### Issue: Field Validator vs Model Validator

**Problem:**
Confusion about when to use `@field_validator` vs `@model_validator`.

**Solution:**
- Use **custom types** for single-field validation (replaces `@field_validator`)
- Use **reusable validators** with `@model_validator` for cross-field validation

### Issue: Custom Type Not Working

**Problem:**
Custom type validation not being triggered.

**Solution:**
Ensure you're using the type directly, not wrapping it:

**❌ Wrong:**
```python
casefile_id: Annotated[str, CasefileId]
```

**✅ Correct:**
```python
casefile_id: CasefileId
```

### Issue: Pydantic v2 Compatibility

**Problem:**
Code using Pydantic v1 syntax.

**Solution:**
Update to Pydantic v2 syntax:

**Pydantic v1:**
```python
@validator('field')
def validate_field(cls, v):
    ...
```

**Pydantic v2:**
```python
@field_validator('field')
@classmethod
def validate_field(cls, v):
    ...
```

---

## Additional Resources

- **Custom Types Source**: `src/pydantic_models/base/custom_types.py`
- **Validators Source**: `src/pydantic_models/base/validators.py`
- **Test Examples**: `tests/pydantic_models/test_custom_types.py`
- **Model Examples**: `src/pydantic_models/canonical/`, `src/pydantic_models/operations/`
- **Pydantic Docs**: https://docs.pydantic.dev/latest/

---

## Getting Help

For questions or issues with validation patterns:

1. Check this guide for common patterns
2. Review existing model implementations in `src/pydantic_models/`
3. Check test files for usage examples
4. Review `DEVELOPMENT_PROGRESS.md` for implementation details
5. Consult team members or create an issue

---

**Happy Validating!** 🚀
