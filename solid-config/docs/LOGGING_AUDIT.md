# Logging Consistency Audit

**Audit Date:** October 1, 2025  
**Auditor:** GitHub Copilot  
**Scope:** All service and API files in `src/`

---

## Executive Summary

**Total Files Audited:** 15 Python modules  
**Logging Issues Found:** 7 categories  
**Severity:** Medium (inconsistencies affect observability, not functionality)  
**Recommendation:** Standardize logging patterns across all services

### Key Findings

✅ **Strengths:**
- All services use `logging.getLogger(__name__)` pattern
- Consistent logger naming convention
- Good use of log levels (debug, info, warning, error)
- Exception logging uses `logger.exception()` properly

⚠️ **Issues:**
- Inconsistent context inclusion (some logs have user_id/session_id, others don't)
- Potential sensitive data exposure in logs (tokens, credentials)
- Mix of f-strings and %-formatting
- Missing structured logging (no log fields for parsing)
- No correlation IDs for tracing requests
- Inconsistent error context (some have stack traces, others don't)
- No log level configuration guidance

---

## Logging Patterns by Module

### 1. Tool Session Service

**Files:** `src/tool_sessionservice/service.py`, `src/tool_sessionservice/repository.py`

#### Current Patterns

```python
# service.py
logger.info(f"Successfully linked session {session_id} to casefile {casefile_id}")
logger.warning(f"Failed to link session {session_id} to casefile {casefile_id}: {e}")
logger.info(f"Executing tool {tool_name} with validated parameters: {validated_params}")
logger.exception(f"Error executing tool {tool_name}: {e}")

# repository.py
logger.info("Initializing Firestore for ToolSessionRepository (mock removed)")
logger.info("Using existing Firebase app")
logger.info(f"Initializing Firebase app with credentials from {cred_path}")
```

#### Issues Identified

1. **Inconsistent context**: Some logs include session_id, others don't
2. **Sensitive data exposure**: Logs validated_params which may contain sensitive data
3. **Missing user context**: No user_id in operational logs
4. **No structured fields**: All messages are strings, can't parse for metrics

#### Recommended Improvements

```python
# Add consistent context
logger.info(
    "Linked session to casefile",
    extra={
        "session_id": session_id,
        "casefile_id": casefile_id,
        "user_id": user_id
    }
)

# Sanitize sensitive data
sanitized_params = {k: "***" if k in SENSITIVE_FIELDS else v for k, v in validated_params.items()}
logger.info(
    "Executing tool",
    extra={
        "tool_name": tool_name,
        "param_count": len(validated_params),
        "session_id": session_id,
        "sanitized_params": sanitized_params
    }
)

# Use exception with context
logger.exception(
    "Tool execution failed",
    extra={
        "tool_name": tool_name,
        "session_id": session_id,
        "error_type": type(e).__name__
    }
)
```

---

### 2. Casefile Service

**Files:** `src/casefileservice/service.py`, `src/casefileservice/repository.py`

#### Current Patterns

```python
# repository.py
logger.info("Initializing Firestore for CasefileRepository")
logger.info("Using existing Firebase app")
logger.info(f"Initializing Firebase app with credentials from {cred_path}")
logger.warning("No GOOGLE_APPLICATION_CREDENTIALS found, using default credentials")
logger.info(f"Using Firestore database: {database_id}")
logger.info(f"Connected to Firestore database: {database_id}")
logger.error(f"Error deleting casefile {casefile_id}: {e}")
```

#### Issues Identified

1. **Missing operation context**: No user_id when deleting casefile
2. **Credential path logging**: Logs credentials path (minor security concern)
3. **No service.py logging**: Service layer has no logging at all! ⚠️
4. **Inconsistent initialization logs**: Too many "initialized" messages

#### Recommended Improvements

```python
# Service layer needs logging
class CasefileService:
    def __init__(self, ...):
        self.logger = logging.getLogger(__name__)
    
    def create_casefile(self, user_id, metadata):
        self.logger.info(
            "Creating casefile",
            extra={"user_id": user_id, "metadata_keys": list(metadata.keys())}
        )
        # ... operation ...
        self.logger.info(
            "Casefile created",
            extra={"user_id": user_id, "casefile_id": casefile.id}
        )
    
    def delete_casefile(self, casefile_id, user_id):
        self.logger.warning(
            "Deleting casefile",
            extra={"casefile_id": casefile_id, "user_id": user_id}
        )

# Repository: reduce initialization noise
logger.info("Firestore initialized", extra={"database_id": database_id or "default"})
# Instead of 5 separate messages
```

---

### 3. Communication Service

**Files:** `src/communicationservice/service.py`, `src/communicationservice/repository.py`

#### Current Patterns

```python
# service.py
logger.info("Created chat session %s with tool session %s", session_id, tool_session["session_id"])
logger.exception("Error processing chat message: %s", exc)
logger.info("Closing tool session %s", tool_session_id)
logger.warning("Failed to close tool session %s: %s", tool_session_id, exc)
```

#### Issues Identified

1. **Mix of formatting styles**: Uses %-formatting instead of f-strings
2. **Missing user context**: No user_id in chat session logs
3. **Incomplete error context**: Exception log doesn't include session_id
4. **No message metadata**: Chat logs don't include message type, length

#### Recommended Improvements

```python
# Use consistent f-strings with structured data
logger.info(
    f"Created chat session {session_id}",
    extra={
        "session_id": session_id,
        "tool_session_id": tool_session["session_id"],
        "user_id": user_id
    }
)

logger.exception(
    f"Error processing chat message",
    extra={
        "session_id": session_id,
        "user_id": user_id,
        "message_type": message.get("type"),
        "error_type": type(exc).__name__
    }
)

logger.info(
    f"Closing tool session {tool_session_id}",
    extra={
        "tool_session_id": tool_session_id,
        "chat_session_id": session_id,
        "reason": "chat_ended"
    }
)
```

---

### 4. Auth Service

**Files:** `src/authservice/token.py`

#### Current Patterns

```python
logger.info(f"Creating token for user: {username} ({user_id})")
logger.info(f"Using JWT version: {jwt.__version__}")
logger.info(f"Token payload: {payload}")
logger.info(f"Token type: {type(encoded_jwt)}")
logger.error(f"Error encoding token: {str(e)}")
logger.info(f"Decoding token (first 10 chars): {token[:10] if token else 'None'}...")
logger.error("Token is empty")
logger.info(f"Token decoded successfully: {payload}")
logger.error(f"JWT decode error: {str(e)}")
logger.info("Development mode: No credentials provided, returning default Sam user")
logger.info(f"Received token: {token[:20] if token and len(token) > 20 else token}...")
```

#### Issues Identified

1. **🚨 SECURITY RISK: Token logging**: Logs token fragments (even 10-20 chars can be risky)
2. **Excessive debug info**: JWT version, token type not needed in production
3. **Missing correlation**: No request_id to correlate token creation/validation
4. **Payload logging**: Logs full JWT payload (may contain sensitive claims)
5. **No rate limit warnings**: No logs for suspicious auth patterns

#### Recommended Improvements

```python
# NEVER log token content
logger.info(
    "Creating token",
    extra={
        "user_id": user_id,
        "username": username,  # OK if username is not sensitive
        "token_length": len(encoded_jwt) if encoded_jwt else 0,
        # DO NOT LOG: token content, payload claims
    }
)

# Minimal decoding logs
logger.info(
    "Decoding token",
    extra={
        "token_length": len(token),
        "has_bearer_prefix": token.startswith("Bearer "),
        # DO NOT LOG: token content
    }
)

# Log decode success without payload
logger.info(
    "Token validated",
    extra={
        "user_id": payload.get("user_id"),
        "exp_timestamp": payload.get("exp"),
        # DO NOT LOG: full payload
    }
)

# Security events should be WARNING level
logger.warning(
    "Token validation failed",
    extra={
        "error_type": type(e).__name__,
        "token_length": len(token),
        "ip_address": request_ip,  # If available
        # DO NOT LOG: token content, error details (info disclosure)
    }
)
```

---

### 5. Solid Service

**Files:** `src/solidservice/client.py`

#### Current Patterns

```python
logger.info("Successfully obtained access token")
logger.error(f"Failed to obtain access token: {e}")
logger.info(f"Created container: {url}")
logger.warning(f"Failed to create container {url}: {response.status_code}")
logger.debug(f"Response: {response.text}")
logger.error(f"Error creating container {url}: {e}")
logger.info(f"Wrote resource: {url}")
logger.info(f"Read resource: {url}")
logger.info(f"Deleted resource: {url}")
logger.info(f"Listed container: {url}")
```

#### Issues Identified

1. **Missing user context**: No user_id in Solid operations
2. **Response body logging**: `response.text` may contain sensitive data
3. **URL logging**: Full URLs may contain auth tokens in query params
4. **No operation timing**: No performance metrics
5. **Missing correlation**: Can't trace operation chains

#### Recommended Improvements

```python
import time

# Add timing context
start_time = time.time()
try:
    # ... operation ...
    logger.info(
        f"Created container",
        extra={
            "url_path": urlparse(url).path,  # Don't log full URL with tokens
            "user_id": user_id,
            "duration_ms": int((time.time() - start_time) * 1000),
            "status_code": response.status_code
        }
    )
except Exception as e:
    logger.error(
        f"Container creation failed",
        extra={
            "url_path": urlparse(url).path,
            "user_id": user_id,
            "duration_ms": int((time.time() - start_time) * 1000),
            "error_type": type(e).__name__,
            # DO NOT LOG: response.text (may contain sensitive data)
        }
    )

# Sanitize responses before logging
if response.status_code >= 400:
    # Only log status, not body
    logger.debug(
        f"HTTP error response",
        extra={
            "status_code": response.status_code,
            "content_length": len(response.text),
            # DO NOT LOG: response.text
        }
    )
```

---

### 6. Pydantic AI Integration

**Files:** `src/pydantic_ai_integration/tool_decorator.py`, `src/pydantic_ai_integration/dependencies.py`, `src/pydantic_ai_integration/agents/base.py`

#### Current Patterns

```python
# tool_decorator.py
logger.info(f"Tool '{name}' registered with agent runtime")
logger.error(f"Validation failed for tool '{name}': {e}")

# dependencies.py
logger.warning(f"Auto-persistence failed after {method.__name__}: {e}")
logger.info(f"Persistence handler set with auto_persist={auto_persist}")
logger.warning("No persistence handler set, cannot persist context")
logger.debug(f"Context persisted for session {self.session_id}")
logger.error(f"Failed to persist context: {e}")
logger.info(f"Context restored for session {self.session_id} with {len(self.tool_events)} events")

# agents/base.py
logging.info(f"Extracted parameters from prompt: {params}")  # Note: logging, not logger!
logging.warning(f"Failed to parse JSON parameters: {e}")
logging.info(f"Executing tool {tool_name} with params: {params}")
logging.exception(f"Error executing tool {tool_name}")
```

#### Issues Identified

1. **⚠️ CRITICAL: Mixed logger usage**: Some use `logging.info()` directly (module-level) instead of `logger.info()`
2. **Parameter logging**: May expose sensitive data in tool parameters
3. **Missing user context**: No user_id in tool execution logs
4. **No session correlation**: Can't trace tool chains
5. **Import logs cluttering**: Tool import successes logged at INFO level

#### Recommended Improvements

```python
# ALWAYS use logger instance, not logging module
logger = logging.getLogger(__name__)  # At module top
# Then use: logger.info(), NOT logging.info()

# Sanitize tool parameters
def sanitize_params(params: dict) -> dict:
    """Remove sensitive fields before logging."""
    SENSITIVE_KEYS = {"password", "token", "secret", "key", "credential"}
    return {
        k: "***REDACTED***" if any(sens in k.lower() for sens in SENSITIVE_KEYS) else v
        for k, v in params.items()
    }

logger.info(
    f"Executing tool {tool_name}",
    extra={
        "tool_name": tool_name,
        "session_id": context.session_id,
        "user_id": context.user_id,
        "param_keys": list(params.keys()),
        "sanitized_params": sanitize_params(params)
    }
)

# Reduce import noise
logger.debug(f"Imported {module_name} tools")  # DEBUG, not INFO

# Add correlation for context operations
logger.info(
    "Context persisted",
    extra={
        "session_id": self.session_id,
        "user_id": self.user_id,
        "event_count": len(self.tool_events),
        "operation_id": self.current_operation_id
    }
)
```

---

### 7. Firestore Persistence

**Files:** `src/persistence/firestore/__init__.py`, `src/persistence/firestore/context_persistence.py`

#### Current Patterns

```python
# __init__.py
logger.info(f"Using Firestore database: {database_id}")
logger.info(f"Initialized Firestore client for project {project_id}")
logger.error(f"Failed to initialize Firestore client: {e}")

# context_persistence.py
logger.info(f"Firestore persistence provider initialized with database: {database_id}")
logger.error(f"Failed to initialize Firestore persistence provider: {e}")
logger.debug(traceback.format_exc())
logger.debug(f"Stored {len(batch_chunks)} chunks for {session_id}/{field_name}")
logger.debug(f"Retrieved {len(chunks)} chunks for {session_id}/{field_name}")
logger.error("Cannot save: Firestore client not initialized")
logger.debug(f"Saved context for session {session_id} to Firestore")
logger.warning(f"No saved context found for session {session_id}")
```

#### Issues Identified

1. **Redundant initialization logs**: Multiple services log similar init messages
2. **Traceback logging**: Uses `traceback.format_exc()` instead of `logger.exception()`
3. **Missing user context**: Persistence logs don't include user_id
4. **No performance metrics**: Chunking operations have no timing data
5. **Inconsistent error levels**: Some errors are DEBUG level

#### Recommended Improvements

```python
# Single initialization log
logger.info(
    "Firestore initialized",
    extra={
        "database_id": database_id or "default",
        "project_id": project_id,
        "service": "context_persistence"
    }
)

# Use logger.exception() instead of traceback
try:
    # ... operation ...
except Exception as e:
    logger.exception(  # Automatically includes traceback
        "Firestore initialization failed",
        extra={
            "error_type": type(e).__name__,
            "database_id": database_id
        }
    )

# Add timing and user context
import time
start = time.time()
try:
    # ... save operation ...
    logger.debug(
        "Context saved",
        extra={
            "session_id": session_id,
            "user_id": user_id,  # ADD THIS
            "chunk_count": len(batch_chunks),
            "duration_ms": int((time.time() - start) * 1000)
        }
    )
except Exception as e:
    logger.error(  # ERROR level, not DEBUG
        "Context save failed",
        extra={
            "session_id": session_id,
            "user_id": user_id,
            "error_type": type(e).__name__,
            "duration_ms": int((time.time() - start) * 1000)
        }
    )
```

---

## Security Concerns Summary

### 🚨 HIGH PRIORITY

1. **Token Logging in authservice/token.py**
   - **Risk:** Logs token fragments, full payloads
   - **Exposure:** `logger.info(f"Token payload: {payload}")`
   - **Fix:** Remove all token content from logs
   - **Impact:** Potential credential disclosure

2. **Parameter Logging in tool_sessionservice**
   - **Risk:** Logs validated_params which may contain passwords, API keys
   - **Exposure:** `logger.info(f"Executing tool {tool_name} with validated parameters: {validated_params}")`
   - **Fix:** Implement parameter sanitization
   - **Impact:** Sensitive data in logs

3. **Response Body Logging in solidservice**
   - **Risk:** Logs `response.text` which may contain auth tokens, personal data
   - **Exposure:** `logger.debug(f"Response: {response.text}")`
   - **Fix:** Only log status codes, content length
   - **Impact:** Data leakage

### ⚠️ MEDIUM PRIORITY

4. **Credential Path Logging**
   - **Risk:** Logs filesystem paths to credentials
   - **Exposure:** `logger.info(f"Initializing Firebase app with credentials from {cred_path}")`
   - **Fix:** Log presence boolean, not path
   - **Impact:** Information disclosure

5. **URL Logging with Query Params**
   - **Risk:** Full URLs may contain tokens in query strings
   - **Exposure:** `logger.info(f"Created container: {url}")`
   - **Fix:** Parse and log path only
   - **Impact:** Token exposure

---

## Consistency Recommendations

### 1. Adopt Structured Logging

**Current:** Unstructured string messages  
**Recommended:** Use `extra={}` for structured fields

```python
# ❌ Current (unstructured)
logger.info(f"Session {session_id} created for user {user_id} with casefile {casefile_id}")

# ✅ Recommended (structured)
logger.info(
    "Session created",
    extra={
        "session_id": session_id,
        "user_id": user_id,
        "casefile_id": casefile_id,
        "timestamp": datetime.now().isoformat()
    }
)
```

**Benefits:**
- Parseable by log aggregators (ELK, Splunk, CloudWatch)
- Can query by specific fields
- Consistent format across all services
- Easier to build dashboards

### 2. Add Correlation IDs

**Current:** No way to trace related operations  
**Recommended:** Include request_id/operation_id in all logs

```python
import uuid

class RequestContext:
    def __init__(self):
        self.request_id = str(uuid.uuid4())
        self.user_id = None
        self.session_id = None

# In FastAPI dependency
def get_request_context() -> RequestContext:
    context = RequestContext()
    # Set from headers or generate
    return context

# In service methods
logger.info(
    "Tool execution started",
    extra={
        "request_id": context.request_id,
        "session_id": session_id,
        "tool_name": tool_name
    }
)
```

### 3. Standardize Log Levels

**Guidelines:**
- **DEBUG**: Detailed diagnostic info (disabled in production)
- **INFO**: Normal operational events (session created, tool executed)
- **WARNING**: Unexpected but recoverable (auth failed, retry succeeded)
- **ERROR**: Error conditions requiring attention (DB connection failed)
- **CRITICAL**: System-wide failures (service down)

**Current Issues:**
- Some errors logged as DEBUG
- Info logs too verbose (tool import messages)
- No WARNING for security events

**Recommended Mapping:**

| Event Type | Current | Recommended | Rationale |
|------------|---------|-------------|-----------|
| Tool import success | INFO | DEBUG | Too verbose for production |
| Token validation failure | ERROR | WARNING | Expected failure, not system error |
| Missing auth credentials | ERROR | ERROR | Correct (requires attention) |
| Casefile created | INFO | INFO | Correct (operational event) |
| Context save failed | DEBUG | ERROR | Wrong level (data loss risk) |
| Firestore initialization | INFO (5 messages) | INFO (1 message) | Reduce noise |

### 4. Create Log Sanitization Helper

**Create:** `src/coreservice/log_utils.py`

```python
"""Logging utilities for consistent, secure logging."""
import logging
from typing import Any, Dict
from datetime import datetime

# Sensitive field patterns
SENSITIVE_PATTERNS = {
    "password", "passwd", "pwd",
    "token", "access_token", "refresh_token", "bearer",
    "secret", "api_key", "apikey",
    "credential", "auth",
    "ssn", "social_security",
    "credit_card", "card_number",
    "private_key", "privkey"
}

def sanitize_dict(data: Dict[str, Any], redact_value: str = "***REDACTED***") -> Dict[str, Any]:
    """Remove sensitive values from dictionary before logging."""
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        key_lower = key.lower().replace("_", "").replace("-", "")
        
        # Check if key contains sensitive pattern
        is_sensitive = any(pattern in key_lower for pattern in SENSITIVE_PATTERNS)
        
        if is_sensitive:
            sanitized[key] = redact_value
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, redact_value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_dict(item, redact_value) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized

def add_standard_context(extra: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Add standard fields to log extra context."""
    standard = {
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        **kwargs
    }
    return {**standard, **extra}

# Example usage
logger.info(
    "Tool executed",
    extra=add_standard_context(
        sanitize_dict({
            "session_id": session_id,
            "tool_name": tool_name,
            "parameters": parameters,  # Will sanitize sensitive params
            "user_id": user_id
        }),
        operation="tool_execution"
    )
)
```

### 5. Configure Log Formatting

**Create:** `src/coreservice/logging_config.py`

```python
"""Centralized logging configuration."""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict

class StructuredFormatter(logging.Formatter):
    """Format logs as JSON for machine parsing."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def configure_logging(
    level: str = "INFO",
    format_style: str = "json"  # or "text"
) -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_style: "json" for structured logging or "text" for human-readable
    """
    log_level = getattr(logging, level.upper())
    
    if format_style == "json":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("firebase_admin").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)

# Usage in main.py or app.py
if __name__ == "__main__":
    from src.coreservice.config import get_environment
    from src.coreservice.logging_config import configure_logging
    
    env = get_environment()
    log_format = "json" if env == "production" else "text"
    log_level = "INFO" if env == "production" else "DEBUG"
    
    configure_logging(level=log_level, format_style=log_format)
```

### 6. Add Performance Logging

**Pattern:** Time-bound operations with context managers

```python
import time
from contextlib import contextmanager
from typing import Generator, Optional

@contextmanager
def log_operation(
    logger: logging.Logger,
    operation: str,
    level: int = logging.INFO,
    **context
) -> Generator[None, None, None]:
    """
    Context manager for logging operations with timing.
    
    Usage:
        with log_operation(logger, "database_query", user_id=user_id):
            result = db.query(...)
    """
    start = time.time()
    logger.log(level, f"{operation} started", extra=context)
    
    try:
        yield
        duration_ms = int((time.time() - start) * 1000)
        logger.log(
            level,
            f"{operation} completed",
            extra={**context, "duration_ms": duration_ms, "status": "success"}
        )
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        logger.error(
            f"{operation} failed",
            extra={
                **context,
                "duration_ms": duration_ms,
                "status": "error",
                "error_type": type(e).__name__
            }
        )
        raise

# Usage
with log_operation(logger, "tool_execution", session_id=session_id, tool_name=tool_name):
    result = tool_service.execute_tool(...)
```

---

## Implementation Plan

### Phase 1: Security Fixes (1 day)

**Priority:** HIGH  
**Impact:** Prevent credential/data exposure

1. **Remove token logging** (authservice/token.py)
   - Remove `logger.info(f"Token payload: {payload}")`
   - Remove `logger.info(f"Received token: {token[:20]}...")`
   - Only log token length, not content

2. **Sanitize parameter logging** (tool_sessionservice/service.py)
   - Implement `sanitize_dict()` helper
   - Apply to all parameter logging

3. **Remove response body logging** (solidservice/client.py)
   - Remove `logger.debug(f"Response: {response.text}")`
   - Only log status codes

### Phase 2: Consistency Fixes (2 days)

**Priority:** MEDIUM  
**Impact:** Improve observability

1. **Fix logger usage** (pydantic_ai_integration/agents/base.py)
   - Replace `logging.info()` with `logger.info()`
   - Add logger instance at module level

2. **Add user context** (all services)
   - Include `user_id` in all operational logs
   - Add `session_id` where applicable

3. **Standardize formatting**
   - Use f-strings consistently (remove %-formatting)
   - Add structured `extra={}` fields

### Phase 3: Structured Logging (3 days)

**Priority:** LOW  
**Impact:** Enable advanced monitoring

1. **Create helper utilities**
   - `src/coreservice/log_utils.py`
   - `src/coreservice/logging_config.py`

2. **Add correlation IDs**
   - FastAPI middleware for request_id
   - Propagate through all service calls

3. **Implement structured logging**
   - Convert all services to use `extra={}` pattern
   - Configure JSON formatter for production

### Phase 4: Documentation (1 day)

1. **Create logging guide** (`docs/LOGGING_GUIDE.md`)
   - Best practices
   - Security guidelines
   - Code examples

2. **Update developer docs**
   - Add logging section to contribution guide
   - Add linter rules for logging

---

## Testing Recommendations

### 1. Log Output Testing

**Create:** `tests/test_logging.py`

```python
import logging
import pytest
from io import StringIO

def test_no_sensitive_data_in_logs(caplog):
    """Ensure sensitive data never appears in logs."""
    caplog.set_level(logging.DEBUG)
    
    # Simulate operation with sensitive data
    token = "secret_token_abc123"
    password = "supersecret"
    
    # Your service code here
    service.do_something(token=token, password=password)
    
    # Assert sensitive data not in logs
    log_output = caplog.text.lower()
    assert "secret_token" not in log_output
    assert "supersecret" not in log_output
    assert "***redacted***" in log_output or "***" in log_output

def test_structured_logging_format():
    """Ensure logs include required structured fields."""
    with caplog.at_level(logging.INFO):
        service.create_session(user_id="user123", casefile_id="cf_123")
    
    # Check for required fields in extra
    for record in caplog.records:
        if "session created" in record.message.lower():
            assert hasattr(record, "user_id")
            assert hasattr(record, "session_id")
            assert hasattr(record, "casefile_id")
```

### 2. Manual Review Checklist

Before deploying logging changes:

- [ ] Search codebase for `logger.info.*token` (should be 0 results)
- [ ] Search codebase for `logger.*password` (should be 0 results)
- [ ] Search codebase for `logger.*credential` (should be 0 results)
- [ ] Search codebase for `logging\.` in src/ (should use `logger.` instead)
- [ ] Verify all services have logger = logging.getLogger(__name__)
- [ ] Check all exception handlers use logger.exception() not logger.error()
- [ ] Verify production logs don't include DEBUG level messages
- [ ] Test log aggregation parsing (if using ELK/Splunk)

---

## Monitoring & Alerting

### Recommended Log-Based Alerts

1. **High Error Rate**
   - Threshold: >10 ERROR logs per minute
   - Action: Page on-call engineer

2. **Authentication Failures**
   - Threshold: >50 failures per minute from single IP
   - Action: Rate limit or block IP

3. **Database Connection Failures**
   - Threshold: Any CRITICAL log from Firestore
   - Action: Check database health

4. **Performance Degradation**
   - Threshold: >5 operations with duration_ms > 5000
   - Action: Investigate slow queries

### Log Aggregation Setup

**Recommended Tools:**
- **Development:** Console output with text format
- **Staging:** CloudWatch Logs with JSON format
- **Production:** CloudWatch Logs + ELK Stack

**Query Examples (CloudWatch Insights):**

```sql
-- High error rate
fields @timestamp, level, message, error_type
| filter level = "ERROR"
| stats count() as error_count by bin(5m)
| filter error_count > 10

-- Slow operations
fields @timestamp, operation, duration_ms, user_id
| filter duration_ms > 5000
| sort duration_ms desc

-- User activity
fields @timestamp, operation, user_id
| filter user_id = "specific_user"
| sort @timestamp desc
```

---

## Appendix: Log Level Decision Tree

```
Is it an error condition?
├─ YES → ERROR (or CRITICAL if system-wide)
└─ NO → Is it a warning/unexpected condition?
    ├─ YES → WARNING
    └─ NO → Is it user-facing operational info?
        ├─ YES → INFO
        └─ NO → DEBUG
```

**Examples:**

- User creates session → **INFO** (operational)
- Database query slow but succeeded → **WARNING** (unexpected)
- Database connection failed → **ERROR** (error condition)
- Service startup failed → **CRITICAL** (system-wide)
- Parameter validation → **DEBUG** (detailed diagnostic)
- Token claims extracted → **DEBUG** (detailed diagnostic)
- Auth failed for invalid credentials → **WARNING** (expected failure)
- Auth failed due to system error → **ERROR** (system issue)

---

**Last Updated:** October 1, 2025  
**Next Review:** January 1, 2026  
**Maintainer:** MDS Objects API Team
