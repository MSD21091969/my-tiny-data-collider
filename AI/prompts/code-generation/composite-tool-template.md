# Composite Tool Pattern Template

*Last updated: October 8, 2025*  
*Sync status: ✅ UP TO DATE (October 8, 2025 - Foundation Sync)*

Template for creating composite tools that orchestrate multiple methods in workflow sequences.

## Context

**Repository**: my-tiny-data-collider  
**Architecture**: 6-Layer Model System with parameter inheritance  
**Pattern**: Composite tool orchestration with step dependencies  
**Location**: `config/toolsets/workflows/`

## Task Definition

Create a composite tool that:
- Orchestrates multiple method calls in sequence
- Maps outputs from one step to inputs of the next
- Merges parameters from all referenced methods
- Handles error propagation and rollback scenarios

## Template Structure

```yaml
# Composite tool name convention: {domain}.{workflow_name}
name: workspace.create_casefile_with_chat

# Clear description of the complete workflow
description: "Creates a new casefile and initializes a chat session for it"

# Category typically reflects the primary domain
category: "workspace"

# Classification for composite tools
classification:
  domain: workspace
  subdomain: workflow           # Use 'workflow' for composite operations
  capability: create
  complexity: composite         # REQUIRED: composite for multi-step tools
  maturity: stable
  integration_tier: internal

# Composite implementation with orchestration details
implementation:
  type: composite               # REQUIRED: composite type
  
  composite:
    # Execution strategy
    strategy: sequential        # sequential | parallel | conditional
    
    # Ordered list of steps
    steps:
      # Step 1: Create casefile
      - step_id: create_casefile
        method_name: workspace.casefile.create_casefile
        description: "Create the casefile entity"
        
        # Input mapping (optional for first step)
        input_mapping:
          title: $input.casefile_title
          description: $input.casefile_description
        
        # Output mapping - define which values to extract
        output_mapping:
          casefile_id: payload.casefile_id
          casefile_status: payload.status
        
        # Error handling for this step
        on_error:
          strategy: abort         # abort | continue | retry
          rollback: true          # Whether to rollback on error
      
      # Step 2: Create chat session
      - step_id: create_chat
        method_name: communication.chat_session.create_chat_session
        description: "Initialize chat session for the casefile"
        
        # Reference output from previous step
        input_mapping:
          casefile_id: $step.create_casefile.casefile_id
          session_name: $input.chat_name
          context: $step.create_casefile
        
        # Output mapping
        output_mapping:
          chat_session_id: payload.session_id
          chat_status: payload.status
        
        on_error:
          strategy: abort
          rollback: true
    
    # Rollback configuration
    rollback:
      enabled: true
      steps:
        - step_id: delete_chat
          condition: create_chat.failed
          method_name: communication.chat_session.delete_chat_session
          input_mapping:
            session_id: $step.create_chat.chat_session_id
        
        - step_id: delete_casefile
          condition: any_failed
          method_name: workspace.casefile.delete_casefile
          input_mapping:
            casefile_id: $step.create_casefile.casefile_id
    
    # Transaction settings
    transaction:
      enabled: true
      isolation_level: read_committed
      timeout_seconds: 30

# Parameters merged from all referenced methods
# AUTO-INHERITED from create_casefile + create_chat_session
# Override only if transformation needed
parameters:
  # Parameters from create_casefile
  - name: casefile_title
    type: string
    required: true
    description: "Title for the new casefile"
    source_step: create_casefile
    source_param: title
  
  - name: casefile_description
    type: string
    required: false
    description: "Description for the new casefile"
    source_step: create_casefile
    source_param: description
  
  # Parameters from create_chat_session
  - name: chat_name
    type: string
    required: false
    description: "Name for the chat session"
    source_step: create_chat
    source_param: session_name
  
  # Composite-specific parameters
  - name: auto_start_chat
    type: boolean
    required: false
    default: true
    description: "Whether to automatically start the chat session"

# Merged return value from all steps
returns:
  type: object
  description: "Combined results from casefile and chat creation"
  properties:
    casefile_id:
      type: string
      description: "Created casefile identifier"
      source: create_casefile.output.casefile_id
    
    casefile_status:
      type: string
      description: "Casefile status"
      source: create_casefile.output.status
    
    chat_session_id:
      type: string
      description: "Created chat session identifier"
      source: create_chat.output.session_id
    
    chat_status:
      type: string
      description: "Chat session status"
      source: create_chat.output.status

# Example showing the complete workflow
examples:
  - description: "Create casefile with chat session"
    input:
      casefile_title: "Investigation Case 001"
      casefile_description: "Fraud investigation case"
      chat_name: "Case Discussion"
      auto_start_chat: true
    output:
      casefile_id: "cf_12345"
      casefile_status: "active"
      chat_session_id: "cs_67890"
      chat_status: "active"
    execution_flow:
      - step: create_casefile
        status: completed
        duration_ms: 150
      - step: create_chat
        status: completed
        duration_ms: 100

# Metadata
metadata:
  version: "1.0.0"
  tags: ["composite", "workflow", "casefile", "chat"]
  requires_auth: true
  estimated_duration_ms: 300
  rate_limit: 50  # Lower limit for composite operations
```

## Execution Strategies

### Sequential Execution
```yaml
composite:
  strategy: sequential  # Steps execute one after another
  steps:
    - step_id: step1
      method_name: method1
    - step_id: step2
      method_name: method2
```

### Parallel Execution
```yaml
composite:
  strategy: parallel  # Steps execute concurrently
  steps:
    - step_id: fetch_user
      method_name: get_user
    - step_id: fetch_settings
      method_name: get_settings
  # Results merged after all complete
```

### Conditional Execution
```yaml
composite:
  strategy: conditional
  steps:
    - step_id: check_exists
      method_name: check_entity
    
    - step_id: create_new
      method_name: create_entity
      condition: $step.check_exists.exists == false
    
    - step_id: update_existing
      method_name: update_entity
      condition: $step.check_exists.exists == true
```

## Input/Output Mapping

### Referencing Input Parameters
```yaml
input_mapping:
  field: $input.parameter_name  # From tool input
```

### Referencing Previous Step Output
```yaml
input_mapping:
  field: $step.step_id.output_field      # From specific step
  field: $previous.output_field          # From immediately previous step
  field: $step.step_id.payload.field_id  # Nested access
```

### Using Constants
```yaml
input_mapping:
  field: "constant_value"  # String literal
  count: 42                # Numeric literal
  enabled: true            # Boolean literal
```

### Transformations
```yaml
input_mapping:
  field: $transform.uppercase($input.name)
  count: $transform.add($step.prev.count, 1)
  combined: $transform.concat($input.first, " ", $input.last)
```

## Error Handling

### Abort Strategy
```yaml
on_error:
  strategy: abort       # Stop execution immediately
  rollback: true        # Execute rollback steps
  propagate: true       # Propagate error to caller
```

### Continue Strategy
```yaml
on_error:
  strategy: continue    # Continue to next step
  default_value: null   # Use default if step fails
  log_error: true       # Log but don't fail
```

### Retry Strategy
```yaml
on_error:
  strategy: retry
  max_attempts: 3
  backoff: exponential  # linear | exponential | fixed
  delay_seconds: 1
  on_exhausted: abort
```

## Rollback Configuration

### Simple Rollback
```yaml
rollback:
  enabled: true
  steps:
    - step_id: cleanup
      method_name: delete_resource
      input_mapping:
        resource_id: $step.create.resource_id
```

### Conditional Rollback
```yaml
rollback:
  enabled: true
  steps:
    - step_id: cleanup_user
      condition: create_user.failed
      method_name: delete_user
    
    - step_id: cleanup_profile
      condition: create_profile.failed
      method_name: delete_profile
```

## Validation Checklist

- [ ] Tool name follows convention: {domain}.{workflow_name}
- [ ] Implementation type is "composite"
- [ ] Classification complexity is "composite"
- [ ] All method references exist in MANAGED_METHODS
- [ ] Step IDs are unique within the workflow
- [ ] Input/output mappings are valid
- [ ] Error handling strategy defined for each step
- [ ] Rollback steps defined if needed
- [ ] Parameters merged from all methods
- [ ] Returns structure includes all step outputs
- [ ] Examples show complete execution flow

## Generation & Testing

```bash
# Generate composite tool
python scripts/generate_tools.py workspace.create_casefile_with_chat

# Validate tool definition
python scripts/validate_dto_alignment.py

# Test execution (if test harness available)
python scripts/test_composite_tool.py workspace.create_casefile_with_chat
```

## Best Practices

### Do
✅ Use sequential strategy for dependent steps  
✅ Use parallel strategy for independent operations  
✅ Include rollback for state-changing operations  
✅ Map outputs explicitly for clarity  
✅ Provide meaningful step IDs and descriptions  
✅ Handle errors at each step  
✅ Document execution flow in examples

### Don't
❌ Create overly complex workflows (>5 steps)  
❌ Ignore error handling and rollback  
❌ Duplicate method parameters manually  
❌ Use undefined step IDs in mappings  
❌ Nest composite tools (flatten instead)  
❌ Skip transaction configuration for critical operations

## Related Resources

- [Tool Schema v2](../../../config/tool_schema_v2.yaml)
- [Method Registry](../../../config/methods_inventory_v1.yaml)
- [Simple Tool Template](tool-yaml-template.md)
- [HANDOVER Document](../../../HANDOVER.md)

---

**Note**: Composite tools are powerful but complex. Start with simple sequential workflows and add complexity only when needed. Consider whether multiple simple tools might be clearer than one complex composite tool.
