# Policy Templates

This directory contains reusable policy configurations for tool definitions. These templates ensure consistent security, audit, and session management across all tools.

## Overview

Policy templates are YAML files containing pre-configured policy sections that can be copied into tool definitions. They promote:

- **Consistency**: Same security patterns across similar tools
- **Best practices**: Pre-vetted configurations for common scenarios
- **Maintainability**: Update policies centrally, not in every tool
- **Compliance**: Built-in patterns for audit and security requirements

## Available Templates

### 1. Security Policies (`security_policies.yaml`)

Defines authentication, authorization, and access control patterns.

**Access Levels:**
- `public_access` - No authentication required (health checks, docs)
- `authenticated_access` - Standard authenticated users
- `casefile_access` - Requires casefile context
- `admin_access` - Privileged admin operations
- `experimental_access` - Beta/experimental features

**Integration Patterns:**
- `google_workspace_integration` - Gmail, Drive, Sheets, Calendar
- `external_api_integration` - Generic third-party APIs

**Key Fields:**
- `requires_auth` - Authentication requirement
- `required_permissions` - Permission list
- `timeout_seconds` - Max execution time
- `rate_limit_per_minute` - API throttling
- `visibility` - public/internal/experimental

### 2. Audit Policies (`audit_policies.yaml`)

Defines logging, event tracking, and compliance requirements.

**Audit Levels:**
- `minimal_audit` - Basic logging for low-risk operations
- `standard_audit` - Standard trail for authenticated ops
- `comprehensive_audit` - Full logging for sensitive operations
- `compliance_audit` - Strict regulatory requirements

**Specialized Patterns:**
- `external_api_audit` - Third-party API tracking
- `pipeline_audit` - Multi-step workflow logging
- `debugging_audit` - Verbose development logging

**Redaction Patterns:**
- `pii_redaction` - Personal Identifiable Information
- `phi_redaction` - Protected Health Information (HIPAA)
- `financial_redaction` - Financial/Payment data (PCI-DSS)

**Key Fields:**
- `success_event` / `failure_event` - Event names for monitoring
- `log_response_fields` - Which portions of the response envelope to capture
- `redact_fields` - Sensitive fields to mask before persistence
- `emit_casefile_event` - Whether to record in the casefile audit trail

### 3. Session Policies (`session_policies.yaml`)

Defines session lifecycle and state management.

**Interaction Types:**
- `stateless_operation` - No session required
- `session_required` - Must have active session
- `session_optional` - Session used if present
- `session_creation` - Can create new sessions
- `system_operation` - Background/admin operations

**Specialized Patterns:**
- `long_running_operation` - Extended execution time
- `interactive_operation` - User interaction required
- `background_job` - Async/scheduled tasks

**Logging Levels:**
- `minimal_logging` - High-performance, low detail
- `standard_logging` - Balanced approach
- `secure_logging` - Restricted for sensitive data

**Key Fields:**
- `requires_active_session` - Session must exist
- `allow_new_session` - Can create new session
- `allow_session_resume` - Can continue existing session
- `session_event_type` - request/resume/system
- `log_request_payload` - Log input parameters
- `log_full_response` - Log complete output

## Usage Examples

### Example 1: Standard Gmail Tool

```yaml
name: gmail_send_message
description: Send an email via Gmail API
category: communication

# Copy security policy
business_rules:
  enabled: true
  requires_auth: true
  required_permissions: ["tools:execute", "google:workspace:access"]
  timeout_seconds: 60
  rate_limit_per_minute: 60
  visibility: internal

# Copy session policy
session_policies:
  requires_active_session: true
  allow_new_session: false
  allow_session_resume: true
  session_event_type: request
  log_request_payload: true
  log_full_response: true

# Copy casefile policy (from security template)
casefile_policies:
  requires_casefile: true
  allowed_casefile_states: ["active"]
  enforce_access_control: true
  audit_casefile_changes: true

# Copy audit policy
audit_events:
  success_event: "external_api_success"
  failure_event: "external_api_failure"
  log_response_fields: ["status", "message", "timestamp", "api_endpoint"]
  redact_fields: ["password", "token", "secret", "api_key", "oauth_token"]
  emit_casefile_event: true
```

### Example 2: Debug/Testing Tool

```yaml
name: echo_tool
description: Simple echo for testing
category: utilities

# Copy public access (no auth required)
business_rules:
  enabled: true
  requires_auth: false
  required_permissions: []
  timeout_seconds: 10
  visibility: experimental

# Copy stateless operation
session_policies:
  requires_active_session: false
  allow_new_session: false
  allow_session_resume: false
  session_event_type: request
  log_request_payload: true
  log_full_response: true

# Copy minimal audit
audit_events:
  success_event: "debug_tool_success"
  failure_event: "debug_tool_failure"
  log_response_fields: []
  redact_fields: []
  emit_casefile_event: false
```

### Example 3: Pipeline Tool

```yaml
name: gmail_to_drive_pipeline
description: Multi-step workflow
category: automation

# Copy casefile access (needs context)
business_rules:
  enabled: true
  requires_auth: true
  required_permissions: ["tools:execute", "casefile:read"]
  timeout_seconds: 120  # Longer for pipeline
  visibility: internal

# Copy session required
session_policies:
  requires_active_session: true
  allow_new_session: false
  allow_session_resume: true
  session_event_type: request
  log_request_payload: true
  log_full_response: false  # Large pipeline output

# Copy casefile policy
casefile_policies:
  requires_casefile: true
  allowed_casefile_states: ["active"]
  enforce_access_control: true
  audit_casefile_changes: true

# Copy pipeline audit
audit_events:
  success_event: "pipeline_success"
  failure_event: "pipeline_failure"
  log_response_fields:
    - "status"
    - "message"
    - "timestamp"
    - "steps_completed"
    - "total_steps"
  redact_fields: ["password", "token", "secret", "api_key"]
  emit_casefile_event: true
```

## Best Practices

1. **Choose the Right Template**
   - Match access level to tool sensitivity
   - Consider external API requirements
   - Balance logging detail with performance

2. **Customize When Needed**
   - Adjust timeout_seconds for tool requirements
   - Add specific permissions to required_permissions
   - Modify redact_fields for your data model

3. **Combine Multiple Templates**
   - Security + Audit + Session = Complete policy
   - Mix patterns (e.g., authenticated + external API)
   - Layer redaction patterns for compliance

4. **Document Deviations**
   - If you customize a template, document why
   - Add comments explaining non-standard settings
   - Update tool documentation with security implications

5. **Regular Review**
  - Audit policy usage across tools
  - Update templates as requirements evolve
  - Ensure compliance standards are met and reflected in `audit_events`

## Policy Selection Guide

| Tool Type | Security | Session | Audit |
|-----------|----------|---------|-------|
| Public API | `public_access` | `stateless_operation` | `minimal_audit` |
| Read-only tool | `authenticated_access` | `session_required` | `standard_audit` |
| Data modification | `casefile_access` | `session_required` | `comprehensive_audit` |
| Gmail/Drive tool | `google_workspace_integration` | `session_required` | `external_api_audit` |
| Pipeline | `casefile_access` | `session_required` | `pipeline_audit` |
| Debug tool | `experimental_access` | `session_optional` | `debugging_audit` |
| Admin operation | `admin_access` | `system_operation` | `compliance_audit` |

## Integration with Tool Factory

When using the tool factory to generate code from YAML:

1. Factory reads policy sections from tool YAML
2. Generates Python code with policy enforcement
3. Applies validation based on business_rules
4. Emits audit events per `audit_events`
5. Manages session lifecycle per session_policies

Policy templates ensure generated code follows consistent patterns.

## Maintenance

**When to Update Templates:**
- New compliance requirements
- Security best practices evolve
- Performance optimization needed
- New integration patterns emerge

**How to Update:**
1. Modify template in this directory
2. Document change in template comments
3. Update tools using that template
4. Test affected tools
5. Deploy and monitor

## See Also

- `../tool_schema_v2.yaml` - Complete schema documentation
- `../tools/README.md` - Tool organization and classification
- `../../docs/TOOL_COMPOSITION.md` - Tool engineering architecture
