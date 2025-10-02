# Tool Composition Engine

The Tool Composition Engine provides a powerful framework for chaining and composing multiple tools together to create complex workflows. This document describes the architecture, usage patterns, and API reference for tool composition.

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Architecture](#architecture)
4. [Usage Patterns](#usage-patterns)
5. [API Reference](#api-reference)
6. [Examples](#examples)
7. [Best Practices](#best-practices)
8. [Error Handling](#error-handling)

## Overview

The Tool Composition Engine enables:

- **Sequential Execution**: Execute tools one after another, optionally passing results between them
- **Parallel Execution**: Execute multiple tools concurrently for improved performance
- **Chain Validation**: Validate tool chains before execution to catch configuration errors early
- **State Management**: Track chain execution status, results, and history
- **Composite Tools**: Register predefined tool chains as reusable composite tools
- **Error Handling**: Flexible error handling with stop-on-error and continue-on-error modes

## Core Concepts

### Tool Chain

A tool chain is an ordered list of tool definitions, where each definition specifies:

```python
{
    "tool_name": "example_tool",    # Name of the tool to execute
    "parameters": {                 # Parameters to pass to the tool
        "value": 42,
        "option": "setting"
    }
}
```

### Chain Execution Modes

1. **Sequential**: Tools execute one after another in order
   - Results can be passed between tools
   - Execution stops or continues on error based on configuration
   - Preserves execution order in results

2. **Parallel**: Tools execute concurrently
   - Results maintain original chain order
   - All tools are attempted regardless of errors (configurable)
   - Suitable for independent operations

### Composite Tools

Composite tools are predefined tool chains registered with metadata:

- Reusable across different contexts
- Self-contained with execution configuration
- Support parameter overrides at execution time
- Can be discovered via the tool registry

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                    MDSContext                            │
│  - validate_chain()                                      │
│  - get_chain_results()                                   │
│  - get_chain_status()                                    │
│  - Active chain tracking                                 │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                 ChainExecutor                            │
│  - execute_chain()                                       │
│  - Sequential execution                                  │
│  - Parallel execution                                    │
│  - Error handling                                        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│              Tool Registry                               │
│  - MANAGED_TOOLS (individual tools)                      │
│  - COMPOSITE_TOOLS (predefined chains)                   │
└─────────────────────────────────────────────────────────┘
```

### Key Components

1. **MDSContext**: Provides chain validation and state management methods
2. **ChainExecutor**: Orchestrates chain execution with support for different modes
3. **CompositeToolDefinition**: Model for registered composite tools
4. **Tool Registry**: Central registry for both individual and composite tools

## Usage Patterns

### Pattern 1: Simple Sequential Chain

Execute tools one after another:

```python
from src.pydantic_ai_integration.dependencies import MDSContext
from src.pydantic_ai_integration.chains import ChainExecutor, ChainExecutionMode

# Create context
context = MDSContext(
    user_id="user123",
    session_id="ts_session_001",
    casefile_id="cf_251001_ABC"
)

# Define chain
chain = [
    {"tool_name": "example_tool", "parameters": {"value": 10}},
    {"tool_name": "another_example_tool", "parameters": {"name": "test", "count": 1}}
]

# Execute
executor = ChainExecutor(context)
result = await executor.execute_chain(
    tools=chain,
    mode=ChainExecutionMode.SEQUENTIAL
)

print(f"Status: {result['status']}")
print(f"Results: {result['results']}")
```

### Pattern 2: Sequential Chain with Result Passing

Pass results from one tool to the next:

```python
result = await executor.execute_chain(
    tools=chain,
    mode=ChainExecutionMode.SEQUENTIAL,
    pass_results=True  # Enable result passing
)

# Second tool receives _previous_result in parameters
```

### Pattern 3: Parallel Execution

Execute tools concurrently:

```python
chain = [
    {"tool_name": "example_tool", "parameters": {"value": 1}},
    {"tool_name": "example_tool", "parameters": {"value": 2}},
    {"tool_name": "example_tool", "parameters": {"value": 3}}
]

result = await executor.execute_chain(
    tools=chain,
    mode=ChainExecutionMode.PARALLEL
)

# All tools execute concurrently
```

### Pattern 4: Named Chain Tracking

Track chains by name for later retrieval:

```python
result = await executor.execute_chain(
    tools=chain,
    mode=ChainExecutionMode.SEQUENTIAL,
    chain_name="data_processing_workflow"
)

# Retrieve chain status later
status = context.get_chain_status(chain_name="data_processing_workflow")
results = context.get_chain_results(chain_name="data_processing_workflow")
```

### Pattern 5: Using Composite Tools

Execute predefined composite tools:

```python
from src.pydantic_ai_integration.tools.example_composite_tools import execute_composite_tool

# Execute a registered composite tool
result = await execute_composite_tool(
    context=context,
    composite_tool_name="data_enrichment_chain"
)

# With parameter overrides
result = await execute_composite_tool(
    context=context,
    composite_tool_name="validation_chain",
    override_parameters={
        "example_tool.value": 100  # Override specific tool parameter
    }
)
```

### Pattern 6: Registering Custom Composite Tools

Create reusable composite tools:

```python
from src.pydantic_ai_integration.tool_decorator import register_composite_tool

my_workflow = register_composite_tool(
    name="custom_analysis",
    description="Custom data analysis workflow",
    tool_chain=[
        {"tool_name": "example_tool", "parameters": {"value": 50}},
        {"tool_name": "advanced_tool", "parameters": {
            "input_data": {"type": "analysis"},
            "options": {"detailed": True}
        }},
        {"tool_name": "another_example_tool", "parameters": {
            "name": "summary",
            "count": 1
        }}
    ],
    category="analysis",
    execution_mode="sequential",
    pass_results=True,
    stop_on_error=True
)
```

## API Reference

### MDSContext Chain Methods

#### `validate_chain(tools: List[Dict[str, Any]]) -> Dict[str, Any]`

Validates a tool chain before execution.

**Parameters:**
- `tools`: List of tool definitions

**Returns:**
```python
{
    "valid": bool,           # Whether chain is valid
    "errors": List[str],     # List of validation errors
    "warnings": List[str],   # List of warnings
    "tool_count": int        # Number of tools in chain
}
```

**Example:**
```python
validation = context.validate_chain(chain)
if not validation["valid"]:
    print(f"Errors: {validation['errors']}")
```

#### `get_chain_results(chain_id: str = None, chain_name: str = None) -> List[Dict[str, Any]]`

Retrieves results from all tools executed in a chain.

**Parameters:**
- `chain_id`: Chain identifier (optional)
- `chain_name`: Chain name (optional, alternative to ID)

**Returns:**
List of tool results with:
- `tool_name`: Name of the tool
- `event_id`: Event identifier
- `position`: Position in chain
- `timestamp`: Execution timestamp
- `parameters`: Tool parameters
- `result_summary`: Tool result
- `duration_ms`: Execution duration

**Example:**
```python
results = context.get_chain_results(chain_id="chain_uuid")
for result in results:
    print(f"{result['tool_name']}: {result['result_summary']}")
```

#### `get_chain_status(chain_id: str = None, chain_name: str = None) -> Dict[str, Any]`

Gets the status of a chain.

**Parameters:**
- `chain_id`: Chain identifier (optional)
- `chain_name`: Chain name (optional, alternative to ID)

**Returns:**
Chain status information including start time, tools, and completion status.

**Example:**
```python
status = context.get_chain_status(chain_name="my_workflow")
print(f"Started: {status['started_at']}")
print(f"Tools: {len(status['tools'])}")
```

### ChainExecutor

#### `__init__(context: MDSContext)`

Creates a chain executor.

**Parameters:**
- `context`: MDSContext for execution

#### `execute_chain(...) -> Dict[str, Any]`

Executes a tool chain.

**Parameters:**
- `tools`: List of tool definitions
- `mode`: Execution mode (SEQUENTIAL or PARALLEL)
- `chain_name`: Optional name for the chain
- `stop_on_error`: Whether to stop on first error (default: True)
- `pass_results`: Whether to pass results between tools (default: False)

**Returns:**
```python
{
    "status": ChainStatus,      # COMPLETED, FAILED, or PARTIALLY_COMPLETED
    "chain_id": str,            # Chain identifier
    "results": List[Dict],      # List of tool results
    "summary": {
        "total_tools": int,
        "successful": int,
        "failed": int,
        "duration_ms": int,
        "mode": str
    }
}
```

**Example:**
```python
executor = ChainExecutor(context)
result = await executor.execute_chain(
    tools=chain,
    mode=ChainExecutionMode.SEQUENTIAL,
    chain_name="my_chain",
    stop_on_error=True,
    pass_results=True
)
```

### Composite Tool Functions

#### `register_composite_tool(...) -> CompositeToolDefinition`

Registers a composite tool.

**Parameters:**
- `name`: Unique identifier
- `description`: What the composite tool does
- `tool_chain`: List of tool definitions
- `category`: Tool category (default: "composite")
- `version`: Version string (default: "1.0.0")
- `execution_mode`: "sequential" or "parallel" (default: "sequential")
- `stop_on_error`: Whether to stop on error (default: True)
- `pass_results`: Whether to pass results (default: True)
- `enabled`: Whether tool is enabled (default: True)
- `requires_auth`: Whether auth is required (default: True)
- `required_permissions`: List of required permissions (default: [])
- `timeout_seconds`: Max execution time (default: 300)

**Returns:**
CompositeToolDefinition instance

#### `get_composite_tool(name: str) -> Optional[CompositeToolDefinition]`

Retrieves a composite tool by name.

**Parameters:**
- `name`: Composite tool name

**Returns:**
CompositeToolDefinition or None if not found

#### `execute_composite_tool(...) -> Dict[str, Any]`

Executes a registered composite tool.

**Parameters:**
- `context`: MDSContext for execution
- `composite_tool_name`: Name of composite tool
- `override_parameters`: Optional parameter overrides

**Returns:**
Execution results (same format as execute_chain)

## Examples

### Example 1: Data Processing Pipeline

```python
# Define a data processing pipeline
pipeline = [
    # Step 1: Validate input
    {
        "tool_name": "example_tool",
        "parameters": {"value": 100}
    },
    # Step 2: Process data
    {
        "tool_name": "advanced_tool",
        "parameters": {
            "input_data": {"source": "validation"},
            "options": {"process": True}
        }
    },
    # Step 3: Generate output
    {
        "tool_name": "another_example_tool",
        "parameters": {"name": "output", "count": 1}
    }
]

# Execute with result passing
executor = ChainExecutor(context)
result = await executor.execute_chain(
    tools=pipeline,
    mode=ChainExecutionMode.SEQUENTIAL,
    chain_name="data_pipeline",
    pass_results=True,
    stop_on_error=True
)

if result["status"] == ChainStatus.COMPLETED:
    print("Pipeline completed successfully")
    for i, tool_result in enumerate(result["results"], 1):
        print(f"Step {i}: {tool_result['tool_name']} - {tool_result['duration_ms']}ms")
```

### Example 2: Parallel Batch Processing

```python
# Process multiple items in parallel
batch_items = [
    {"tool_name": "example_tool", "parameters": {"value": i}}
    for i in range(1, 11)  # Process 10 items
]

result = await executor.execute_chain(
    tools=batch_items,
    mode=ChainExecutionMode.PARALLEL,
    chain_name="batch_processing",
    stop_on_error=False  # Process all items even if some fail
)

successful = result["summary"]["successful"]
failed = result["summary"]["failed"]
print(f"Processed: {successful} successful, {failed} failed")
```

### Example 3: Conditional Execution

```python
# Execute chain and check status before proceeding
validation_chain = [
    {"tool_name": "example_tool", "parameters": {"value": 50}}
]

validation_result = await executor.execute_chain(
    tools=validation_chain,
    mode=ChainExecutionMode.SEQUENTIAL
)

if validation_result["status"] == ChainStatus.COMPLETED:
    # Validation passed, continue with processing
    processing_chain = [
        {"tool_name": "advanced_tool", "parameters": {
            "input_data": {"validated": True},
            "options": {"mode": "production"}
        }}
    ]
    
    processing_result = await executor.execute_chain(
        tools=processing_chain,
        mode=ChainExecutionMode.SEQUENTIAL
    )
```

### Example 4: Using Predefined Composite Tools

```python
# Execute a predefined data enrichment workflow
result = await execute_composite_tool(
    context=context,
    composite_tool_name="data_enrichment_chain"
)

# Execute validation workflow
validation_result = await execute_composite_tool(
    context=context,
    composite_tool_name="validation_chain"
)

# Execute parallel processing workflow
parallel_result = await execute_composite_tool(
    context=context,
    composite_tool_name="parallel_processing_chain"
)
```

## Best Practices

### 1. Chain Design

- **Keep chains focused**: Each chain should accomplish a single high-level task
- **Validate early**: Use `validate_chain()` before execution to catch errors
- **Name chains**: Use descriptive chain names for tracking and debugging
- **Document intent**: Include clear descriptions in composite tool definitions

### 2. Error Handling

- **Use stop_on_error for dependencies**: When tools depend on previous results
- **Use continue_on_error for batch processing**: When processing independent items
- **Check result status**: Always verify the chain status before using results
- **Handle partial completion**: Plan for PARTIALLY_COMPLETED status in batch operations

### 3. Performance

- **Use parallel mode for independent tools**: Significantly reduces total execution time
- **Set appropriate timeouts**: Configure timeout_seconds based on expected duration
- **Pass results judiciously**: Only enable pass_results when needed
- **Monitor chain performance**: Track duration_ms for optimization opportunities

### 4. Maintainability

- **Register composite tools for reuse**: Create reusable workflows as composite tools
- **Use consistent parameter naming**: Follow conventions across tool definitions
- **Version composite tools**: Use version field to track changes
- **Document parameters**: Clearly document expected parameters and formats

### 5. State Management

- **Track active chains**: Use chain_name for long-running workflows
- **Store chain results**: Persist important chain results for auditing
- **Use chain IDs for correlation**: Link related operations via chain_id
- **Clean up completed chains**: Remove completed chains to prevent memory growth

## Error Handling

### Error Types

1. **Validation Errors**: Chain structure or configuration issues
   - Missing tool_name
   - Invalid parameters
   - Empty chains

2. **Execution Errors**: Issues during tool execution
   - Tool not found
   - Tool disabled
   - Parameter validation failures
   - Runtime exceptions

3. **Timeout Errors**: Chain exceeds configured timeout
   - Individual tool timeouts
   - Overall chain timeout

### Handling Strategies

#### Stop on Error (Default)

```python
result = await executor.execute_chain(
    tools=chain,
    mode=ChainExecutionMode.SEQUENTIAL,
    stop_on_error=True  # Stop at first error
)

if result["status"] == ChainStatus.FAILED:
    # Check which tool failed
    for tool_result in result["results"]:
        if "error" in tool_result:
            print(f"Failed at: {tool_result['tool_name']}")
            print(f"Error: {tool_result['error']}")
            break
```

#### Continue on Error

```python
result = await executor.execute_chain(
    tools=chain,
    mode=ChainExecutionMode.SEQUENTIAL,
    stop_on_error=False  # Continue despite errors
)

# Process all results
for tool_result in result["results"]:
    if tool_result["success"]:
        print(f"Success: {tool_result['tool_name']}")
    else:
        print(f"Failed: {tool_result['tool_name']} - {tool_result['error']}")
```

#### Validation Before Execution

```python
# Validate before executing
validation = context.validate_chain(chain)

if not validation["valid"]:
    print("Chain validation failed:")
    for error in validation["errors"]:
        print(f"  - {error}")
    # Handle validation errors
    return

# Execute only if valid
result = await executor.execute_chain(tools=chain, mode=ChainExecutionMode.SEQUENTIAL)
```

### Status Codes

- **PENDING**: Chain not yet started
- **RUNNING**: Chain currently executing
- **COMPLETED**: All tools completed successfully
- **FAILED**: Chain execution failed (all tools failed or stopped on error)
- **PARTIALLY_COMPLETED**: Some tools succeeded, some failed

## Advanced Topics

### Custom Chain Execution Logic

You can subclass ChainExecutor to implement custom execution logic:

```python
from src.pydantic_ai_integration.chains import ChainExecutor

class CustomExecutor(ChainExecutor):
    async def _execute_single_tool(self, tool_name, parameters, chain_id, chain_name, position):
        # Add custom pre-processing
        print(f"Executing {tool_name} at position {position}")
        
        # Call parent implementation
        result = await super()._execute_single_tool(
            tool_name, parameters, chain_id, chain_name, position
        )
        
        # Add custom post-processing
        print(f"Completed {tool_name}: {result['success']}")
        
        return result
```

### Chain Metrics and Monitoring

Track chain performance:

```python
result = await executor.execute_chain(tools=chain, mode=ChainExecutionMode.SEQUENTIAL)

# Analyze performance
total_duration = result["summary"]["duration_ms"]
avg_duration = total_duration / result["summary"]["total_tools"]

print(f"Total duration: {total_duration}ms")
print(f"Average per tool: {avg_duration}ms")

# Get detailed timing per tool
for tool_result in result["results"]:
    print(f"{tool_result['tool_name']}: {tool_result['duration_ms']}ms")
```

### Dynamic Chain Construction

Build chains dynamically based on runtime conditions:

```python
def build_processing_chain(data_type: str) -> List[Dict[str, Any]]:
    """Build chain based on data type."""
    chain = [
        {"tool_name": "example_tool", "parameters": {"value": 1}}
    ]
    
    if data_type == "complex":
        chain.append({
            "tool_name": "advanced_tool",
            "parameters": {
                "input_data": {"type": data_type},
                "options": {"detailed": True}
            }
        })
    
    chain.append({
        "tool_name": "another_example_tool",
        "parameters": {"name": "finalize", "count": 1}
    })
    
    return chain

# Use dynamic chain
chain = build_processing_chain("complex")
result = await executor.execute_chain(tools=chain, mode=ChainExecutionMode.SEQUENTIAL)
```

## Conclusion

The Tool Composition Engine provides a flexible and powerful framework for building complex workflows from individual tools. By supporting both sequential and parallel execution, comprehensive error handling, and reusable composite tools, it enables sophisticated automation scenarios while maintaining simplicity and clarity in implementation.

For questions or issues, refer to the test suite in `tests/test_tool_composition.py` for additional examples and edge cases.
