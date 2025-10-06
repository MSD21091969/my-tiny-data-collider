# Tool Composition Documentation

## Overview

The Tool Composition system enables orchestration of multiple tools into workflows with conditional logic, error handling, and state management. Composite tools execute sequences of existing tools with branching decisions based on success/failure outcomes.

**Status:** Week 2 - MVP Complete  
**Branch:** feature/tool-composition

---

## Architecture

### Components

```
Composite Tool YAML Definition
    ↓
Tool Factory (generates code)
    ↓
Generated Composite Tool
    ↓
ChainExecutor (orchestrates execution)
    ↓
Individual Tools (echo_tool, gmail_search_messages, etc.)
    ↓
Results aggregated and returned
```

### Key Components

1. **Tool Factory** (`src/pydantic_ai_integration/tools/factory/`)
   - Extended templates support `implementation.type: composite`
   - Generates composite tool code with ChainExecutor integration
   - Validates YAML step definitions

2. **ChainExecutor** (`src/pydantic_ai_integration/tools/chain_executor.py`)
   - Executes tool chains with conditional branching
   - Manages state passing between steps
   - Handles error recovery (retry, continue, stop)
   - Integrates with MDSContext for audit trail

3. **MDSContext Chain Management** (`src/pydantic_ai_integration/dependencies.py`)
   - `plan_tool_chain()` - Records planned chain execution
   - `active_chains` - Tracks named chains
   - `next_planned_tools` - Stores tool sequences

---

## YAML Schema for Composite Tools

### Basic Structure

```yaml
name: my_composite_tool
display_name: "My Composite Tool"
description: "Chains tool A and tool B with conditional logic"
category: "workflows"
version: "1.0.0"

implementation:
  type: composite
  composite:
    steps:
      - tool: tool_a
        inputs:
          param1: "{{ state.input_value }}"
        on_success:
          map_outputs:
            result_field: "step1_output"
          next: tool_b
        on_failure:
          action: stop
          
      - tool: tool_b
        inputs:
          param2: "{{ state.step1_output }}"
        on_success:
          map_outputs:
            final_result: "step2_output"
        on_failure:
          action: retry
          max_retries: 3
```

### Step Definition

Each step in `composite.steps` has:

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `tool` | Yes | string | Name of tool to execute |
| `inputs` | Yes | dict | Input parameters for the tool |
| `on_success` | No | object | What to do if step succeeds |
| `on_failure` | No | object | What to do if step fails |

### Input Variable Interpolation

Inputs support template substitution from chain state:

```yaml
inputs:
  message: "{{ state.user_input }}"        # From initial parameters
  data: "{{ state.step1_result }}"         # From previous step output
  static_value: "literal string"           # Literal value
```

**Template Syntax:**
- `{{ state.variable_name }}` - Substitutes value from chain state
- `{{ variable_name }}` - Also checks chain state
- No template markers - Used as literal value

### on_success Actions

```yaml
on_success:
  # Map output fields to state variables
  map_outputs:
    source_field: "destination_variable"
    
  # Jump to named step
  next: step_name
  
  # If no 'next', continues to next sequential step
```

### on_failure Actions

```yaml
on_failure:
  action: stop         # Stop chain execution (default)
  
  # OR
  
  action: retry
  max_retries: 3
  continue_on_max_retries: false  # Stop if max retries exceeded
  
  # OR
  
  action: continue     # Continue to next step despite failure
  next: recovery_step  # Optional: jump to specific step
```

---

## Examples

### Example 1: Simple Echo Chain

```yaml
name: echo_chain_demo
display_name: "Echo Chain Demo"
description: "Chains three echo_tool calls sequentially"
category: "demo"

parameters:
  - name: initial_message
    type: string
    required: true

implementation:
  type: composite
  composite:
    steps:
      - tool: echo_tool
        inputs:
          message: "{{ state.initial_message }}"
          session_id: "chain_session"
        on_success:
          map_outputs:
            data: "step1_result"
            
      - tool: echo_tool
        inputs:
          message: "Step 2: {{ state.step1_result }}"
          session_id: "chain_session"
        on_success:
          map_outputs:
            data: "step2_result"
            
      - tool: echo_tool
        inputs:
          message: "Step 3: {{ state.step2_result }}"
          session_id: "chain_session"
        on_success:
          map_outputs:
            data: "final_result"
```

**Usage:**
```python
from src.pydantic_ai_integration.dependencies import MDSContext
from src.pydantic_ai_integration.tools.generated.echo_chain_demo import echo_chain_demo

ctx = MDSContext(user_id="user_123", session_id="session_456")
result = await echo_chain_demo(ctx, initial_message="Hello chain!")

print(result["steps_executed"])  # 3
print(result["status"])           # "success"
```

### Example 2: Gmail to Drive Pipeline (Production Workflow)

```yaml
name: gmail_to_drive_pipeline
display_name: "Gmail to Drive Pipeline"
description: "Search Gmail and upload messages to Drive"
category: "google_workspace"

parameters:
  - name: search_query
    type: string
    required: true
    description: "Gmail search query"
  
  - name: max_results
    type: integer
    required: false
    default: 10
  
  - name: drive_folder_name
    type: string
    required: true

implementation:
  type: composite
  composite:
    steps:
      # Step 1: Search Gmail
      - tool: gmail_search_messages
        inputs:
          query: "{{ state.search_query }}"
          max_results: "{{ state.max_results }}"
        on_success:
          map_outputs:
            messages: "found_messages"
            message_count: "total_found"
          next: drive_upload_file
        on_failure:
          action: stop
          
      # Step 2: Upload to Drive
      - tool: drive_upload_file
        inputs:
          file_name: "{{ state.drive_folder_name }}_archive.json"
          content: "{{ state.found_messages }}"
          mime_type: "application/json"
        on_success:
          map_outputs:
            file_id: "drive_file_id"
            web_view_link: "archive_link"
        on_failure:
          action: retry
          max_retries: 3
```

**Usage:**
```python
result = await gmail_to_drive_pipeline(
    ctx=ctx,
    search_query="from:notifications@github.com is:unread",
    max_results=50,
    drive_folder_name="GitHub Notifications"
)

print(result["data"]["total_found"])      # Number of emails found
print(result["data"]["drive_file_id"])    # ID of uploaded file
print(result["data"]["archive_link"])     # Web link to file
```

### Example 3: Error Recovery Pattern

```yaml
name: resilient_workflow
description: "Demonstrates error recovery with fallback steps"

implementation:
  type: composite
  composite:
    steps:
      # Try primary data source
      - tool: primary_data_tool
        inputs:
          query: "{{ state.search_term }}"
        on_success:
          map_outputs:
            results: "data"
          next: process_results
        on_failure:
          action: continue
          next: fallback_data_tool
      
      # Fallback to secondary source
      - tool: fallback_data_tool
        inputs:
          query: "{{ state.search_term }}"
        on_success:
          map_outputs:
            results: "data"
          next: process_results
        on_failure:
          action: stop
      
      # Process whichever succeeded
      - tool: process_results
        inputs:
          data: "{{ state.data }}"
        on_failure:
          action: retry
          max_retries: 2
```

---

## Chain Execution Semantics

### Execution Flow

1. **Initialization**
   - Chain ID generated via `MDSContext.plan_tool_chain()`
   - Initial state created from tool parameters
   - Execution log initialized

2. **Step Execution Loop**
   - Load step definition
   - Resolve input templates from state
   - Execute tool via MANAGED_TOOLS registry
   - Record result in execution history

3. **Success Handling**
   - Map specified outputs to state variables
   - Determine next step (explicit `next` or sequential)
   - Continue execution

4. **Failure Handling**
   - Record error in execution history
   - Apply failure policy (stop/retry/continue)
   - Retry with backoff if configured
   - Jump to recovery step if specified

5. **Completion**
   - Aggregate results from all executed steps
   - Return final state with execution metadata
   - Update audit trail in MDSContext

### State Management

**Chain State Dictionary:**
```python
state = {
    "chain_id": "uuid-string",
    "chain_name": "optional_name",
    "started_at": "2025-10-03T...",
    
    # Input parameters
    "param1": "value1",
    "param2": "value2",
    
    # Step outputs (via map_outputs)
    "step1_result": {...},
    "step2_output": {...},
    
    # Retry tracking
    "step_0_retry_count": 2,
}
```

### Execution Result

```python
{
    "success": True,
    "chain_id": "abc-123",
    "chain_name": "gmail_to_drive_pipeline",
    "steps_executed": 2,
    "steps_succeeded": 2,
    "steps_failed": 0,
    "results": [
        {
            "step": "gmail_search_messages",
            "status": "success",
            "result": {...}
        },
        {
            "step": "drive_upload_file",
            "status": "success",
            "result": {...}
        }
    ],
    "execution_history": [...],
    "final_state": {...},
    "completed_at": "2025-10-03T..."
}
```

---

## Conditional Logic Patterns

### Sequential Execution (No Branching)

```yaml
steps:
  - tool: step1
    inputs: {...}
  - tool: step2
    inputs: {...}
  - tool: step3
    inputs: {...}
# Each step executes in order, stops on first failure
```

### Conditional Branching

```yaml
steps:
  - tool: validation_tool
    inputs: {...}
    on_success:
      next: process_valid_data
    on_failure:
      next: handle_invalid_data
  
  - tool: process_valid_data
    inputs: {...}
  
  - tool: handle_invalid_data
    inputs: {...}
```

### Retry with Fallback

```yaml
steps:
  - tool: primary_service
    inputs: {...}
    on_failure:
      action: retry
      max_retries: 3
      continue_on_max_retries: true
      next: backup_service
  
  - tool: backup_service
    inputs: {...}
```

### Continue Despite Errors

```yaml
steps:
  - tool: optional_enrichment
    inputs: {...}
    on_failure:
      action: continue  # Don't let failure block pipeline
  
  - tool: required_processing
    inputs: {...}
    on_failure:
      action: stop      # This one must succeed
```

---

## Integration Testing

### Test Structure

```python
# tests/integration/test_tool_composition.py

import pytest
from src.pydantic_ai_integration.dependencies import MDSContext
from src.pydantic_ai_integration.tools.generated.echo_chain_demo import echo_chain_demo

@pytest.mark.integration
@pytest.mark.asyncio
async def test_echo_chain_success():
    """Test successful chain execution."""
    ctx = MDSContext(
        user_id="test_user",
        session_id="test_session"
    )
    
    result = await echo_chain_demo(
        ctx=ctx,
        initial_message="Test message"
    )
    
    assert result["status"] == "success"
    assert result["steps_executed"] == 3
    assert "final_result" in result["data"]["final_state"]

@pytest.mark.integration
@pytest.mark.asyncio
async def test_chain_with_failure():
    """Test chain execution with step failure."""
    # TODO: Create test scenario where step fails
    pass

@pytest.mark.integration
@pytest.mark.asyncio
async def test_chain_retry_logic():
    """Test retry behavior on transient failures."""
    # TODO: Mock tool to fail N times then succeed
    pass
```

### Policy Enforcement Tests

```python
@pytest.mark.integration
async def test_composite_tool_requires_casefile():
    """Test that composite tools enforce casefile policies."""
    ctx = MDSContext(
        user_id="test_user",
        session_id="test_session",
        casefile_id=None  # Missing required casefile
    )
    
    with pytest.raises(PolicyViolationError):
        await gmail_to_drive_pipeline(
            ctx=ctx,
            search_query="test",
            drive_folder_name="Test"
        )
```

---

## Tool Factory Integration

### Generating Composite Tools

```bash
# Create YAML definition
# config/tools/my_workflow.yaml

# Generate tool
python scripts/generate_tools.py my_workflow

# Generated files:
# - src/pydantic_ai_integration/tools/generated/my_workflow.py
# - tests/generated/test_my_workflow.py
```

### Template Extensions

The tool template (`src/pydantic_ai_integration/tools/factory/templates/tool_template.py.jinja2`) includes:

```jinja
{% if tool.implementation.type == 'composite' %}
from ..chain_executor import ChainExecutor

# ... in function body ...

executor = ChainExecutor(ctx)

initial_state = {
    {% for param in tool.parameters %}
    "{{ param.name }}": {{ param.name }},
    {% endfor %}
}

steps = {{ tool.implementation.composite.steps | tojson }}

chain_result = await executor.execute_chain(
    steps=steps,
    initial_state=initial_state,
    chain_name="{{ tool.name }}"
)

result = {
    "tool": "{{ tool.name }}",
    "status": "success" if chain_result.get("success") else "failure",
    "chain_id": chain_result.get("chain_id"),
    "steps_executed": chain_result.get("steps_executed"),
    "data": chain_result
}
{% endif %}
```

---

## Best Practices

### 1. Design Composite Tools for Reusability

```yaml
# ❌ Bad: Tightly coupled, hard-coded values
steps:
  - tool: gmail_search_messages
    inputs:
      query: "from:specific@email.com"  # Hard-coded

# ✅ Good: Parameterized, reusable
parameters:
  - name: search_query
    type: string
    required: true

steps:
  - tool: gmail_search_messages
    inputs:
      query: "{{ state.search_query }}"
```

### 2. Handle Errors Gracefully

```yaml
# ✅ Always specify on_failure behavior
steps:
  - tool: external_api_call
    on_failure:
      action: retry
      max_retries: 3
  
  - tool: critical_operation
    on_failure:
      action: stop  # Don't continue if this fails
```

### 3. Map Outputs Explicitly

```yaml
# ✅ Clear output mapping
on_success:
  map_outputs:
    messages: "gmail_messages"      # Descriptive names
    file_id: "uploaded_file_id"
    
# Then use in next step:
inputs:
  data: "{{ state.gmail_messages }}"
```

### 4. Document Complex Workflows

```yaml
documentation:
  summary: |
    This composite tool orchestrates:
    1. Search Gmail for invoices
    2. Extract PDF attachments
    3. Upload to Drive folder
    4. Update spreadsheet log
    
    Prerequisites:
    - Gmail read permission
    - Drive write permission
    - Active casefile
```

### 5. Use Descriptive Tool Names

```yaml
# ❌ Bad
name: tool1
steps:
  - tool: tool2
    
# ✅ Good
name: invoice_archival_pipeline
steps:
  - tool: gmail_search_messages
  - tool: extract_attachments
  - tool: drive_upload_files
```

---

## Limitations & Future Enhancements

### Current Limitations (Week 2)

1. **Linear execution only** - No parallel step execution
2. **Simple templating** - No complex expressions or transformations
3. **No loops** - Can't iterate over arrays of items
4. **No conditional steps** - Can't skip steps based on state values
5. **Limited state inspection** - Can't query state in YAML conditions

### Planned Enhancements (Week 3+)

#### Parallel Execution

```yaml
steps:
  - parallel:
      - tool: fetch_data_source_1
      - tool: fetch_data_source_2
      - tool: fetch_data_source_3
    wait_for: all  # or "any" or "first_success"
```

#### Loop Support

```yaml
steps:
  - tool: gmail_search_messages
    on_success:
      map_outputs:
        messages: "message_list"
  
  - loop:
      over: "{{ state.message_list }}"
      as: "current_message"
      steps:
        - tool: process_single_message
          inputs:
            message: "{{ current_message }}"
```

#### Conditional Steps

```yaml
steps:
  - tool: check_balance
    on_success:
      map_outputs:
        balance: "account_balance"
  
  - tool: send_alert
    when: "{{ state.account_balance < 100 }}"
    inputs:
      message: "Low balance alert"
```

#### Data Transformations

```yaml
steps:
  - tool: fetch_raw_data
    on_success:
      map_outputs:
        data: "raw_data"
      transform:
        filtered_data: "{{ state.raw_data | filter(lambda x: x.value > 50) }}"
```

---

## Troubleshooting

### Common Issues

**Issue: "Tool not found in registry"**
```
Solution: Ensure the tool is registered with @register_mds_tool
and imported before composite tool execution
```

**Issue: "Variable not found in chain state"**
```yaml
# Check map_outputs names match input templates
on_success:
  map_outputs:
    result: "step1_output"  # Must match...

inputs:
  data: "{{ state.step1_output }}"  # ...this reference
```

**Issue: "Chain execution stopped unexpectedly"**
```
Check on_failure policies - default is "stop"
Add explicit on_failure: { action: continue } if needed
```

**Issue: "Max retries exceeded"**
```yaml
# Increase retry limit or add fallback
on_failure:
  action: retry
  max_retries: 5  # Increase if needed
  continue_on_max_retries: true  # Don't fail, use fallback
  next: fallback_step
```

---

## API Reference

### ChainExecutor

```python
class ChainExecutor:
    """Executes composite tool chains."""
    
    def __init__(self, ctx: MDSContext)
    
    async def execute_chain(
        self,
        steps: List[Dict[str, Any]],
        initial_state: Optional[Dict[str, Any]] = None,
        chain_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a chain of tool steps.
        
        Args:
            steps: List of step definitions
            initial_state: Initial state dict
            chain_name: Optional chain name
            
        Returns:
            Dict with execution results
            
        Raises:
            ChainExecutionError: If chain fails without recovery
        """
```

### MDSContext Chain Methods

```python
def plan_tool_chain(
    self,
    tools: List[Dict[str, Any]],
    reasoning: str = None,
    chain_name: str = None
) -> str:
    """Plan a sequence of tools.
    
    Args:
        tools: List of tools with name and parameters
        reasoning: Optional explanation
        chain_name: Optional name for reference
        
    Returns:
        Chain ID
    """
```

---

## References

- [Tool Factory Documentation](../README.md#tool-factory)
- [YAML Schema v2](../../config/tool_schema_v2.yaml)
- [Layered Architecture](LAYERED_ARCHITECTURE_FLOW.md)
- [Policy Flow](POLICY_AND_USER_ID_FLOW.md)

---

**Document Version:** 1.0  
**Last Updated:** October 3, 2025  
**Status:** Week 2 MVP Complete  
**Next Steps:** Parallel execution, loops, conditional steps (Week 3+)
