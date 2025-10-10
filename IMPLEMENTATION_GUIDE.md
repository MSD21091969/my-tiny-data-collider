# Implementation Guide for Branch 1: feature/ai-method-integration

This document provides guidance for developers implementing the parameter mapping and method integration functionality in the `feature/ai-method-integration` branch.

## Key Files to Modify

1. **Primary Implementation File**: `src/pydantic_ai_integration/tool_decorator.py`
   - Focus on enhancing the `register_tools_from_yaml()` function
   - Update the `tool_function` implementation inside this function

2. **Supporting Files**:
   - `src/pydantic_ai_integration/tool_definition.py` - May need enhancements to support parameter mapping
   - `src/pydantic_ai_integration/method_registry.py` - For method lookup and parameter extraction

## Implementation Steps

### 1. Enhance YAML Schema for Parameter Mapping

Extend the tool YAML schema to support detailed parameter mapping:

```yaml
# Example enhanced schema
name: "create_casefile"
method_reference:
  service: "CasefileService"
  method: "create_casefile"
parameter_mapping:
  method_params:
    - name: "title"
      source: "title"
      transform: null
    - name: "description"
      source: "description"
      transform: null
    - name: "created_at"
      source: "date_string"
      transform: "parse_datetime"
  tool_params:
    - name: "dry_run"
    - name: "timeout_seconds"
    - name: "execution_mode"
```

### 2. Implement Service Instantiation Logic

Add logic to dynamically instantiate service objects:

```python
def instantiate_service(service_name):
    """Dynamically instantiate a service by name."""
    # Import service class dynamically
    module_path = f"src.{service_name.lower()}"
    try:
        module = importlib.import_module(module_path)
        service_class = getattr(module, service_name)
        
        # Instantiate service with dependencies if needed
        # This could be enhanced with dependency injection
        return service_class()
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Failed to instantiate service '{service_name}': {e}")
```

### 3. Implement Parameter Mapping Logic

Create utilities to map between tool parameters and method parameters:

```python
def map_parameters(tool_params, parameter_mapping):
    """Map tool parameters to method parameters based on mapping configuration."""
    method_params = {}
    tool_specific_params = {}
    
    # Extract method parameters based on mapping
    for param in parameter_mapping.get('method_params', []):
        source_name = param.get('source', param['name'])
        if source_name in tool_params:
            value = tool_params[source_name]
            
            # Apply transformation if specified
            if param.get('transform'):
                value = apply_transform(value, param['transform'])
                
            method_params[param['name']] = value
    
    # Extract tool-specific parameters
    for param in parameter_mapping.get('tool_params', []):
        if param['name'] in tool_params:
            tool_specific_params[param['name']] = tool_params[param['name']]
    
    return method_params, tool_specific_params
```

### 4. Update Tool Function Implementation

Replace the placeholder implementation with actual method calling:

```python
# Inside register_tools_from_yaml function:
async def tool_function(ctx, **kwargs):
    """Enhanced tool function that executes based on YAML configuration."""
    # Extract execution metadata
    execution_type = kwargs.get('execution_type', 'method_wrapper')
    method_name_param = kwargs.get('method_name', method_name)
    parameter_mapping = kwargs.get('parameter_mapping', {})
    dry_run = kwargs.get('dry_run', False)
    
    if dry_run:
        return {
            "status": "dry_run",
            "parameters": kwargs,
            "message": f"Dry run: would execute {tool_name} via {execution_type}"
        }
    
    # Execute based on type
    if execution_type == 'method_wrapper':
        # Parse service and method name
        service_name, method_name_part = method_name_param.split('.')
        
        # Map parameters
        method_params, tool_params = map_parameters(kwargs, parameter_mapping)
        
        # Instantiate service
        service = instantiate_service(service_name)
        
        try:
            # Call method with mapped parameters
            method = getattr(service, method_name_part)
            result = await method(**method_params)
            
            # Return successful result
            return {
                "status": "success",
                "result": result,
                "tool_params": tool_params
            }
        except Exception as e:
            # Handle errors
            return {
                "status": "error",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "tool_params": tool_params
            }
    else:
        # Placeholder for other execution types
        return {
            "status": "not_implemented",
            "message": f"Execution type '{execution_type}' not yet implemented"
        }
```

### 5. Handle Bidirectional Mapping

Add support for mapping method outputs back to tool response format:

```python
def map_method_result_to_tool_response(method_result, output_mapping=None):
    """Map method result to tool response format."""
    if not output_mapping:
        # Default: return result as-is
        return {"result": method_result}
    
    response = {}
    for dest_key, source_path in output_mapping.items():
        # Extract value from nested result using path
        value = extract_value_by_path(method_result, source_path)
        response[dest_key] = value
    
    return response
```

### 6. Implement Orchestration Parameter Handling

Add logic to handle orchestration parameters:

```python
def process_orchestration_parameters(tool_params):
    """Process orchestration parameters to determine execution behavior."""
    execution_config = {
        "dry_run": tool_params.get("dry_run", False),
        "timeout_seconds": tool_params.get("timeout_seconds", 30),
        "retry_count": tool_params.get("retry_count", 0),
        "retry_delay": tool_params.get("retry_delay", 1.0),
    }
    
    return execution_config
```

## Testing Approach

1. **Unit Tests**: Create tests for each component (parameter mapping, service instantiation, etc.)
2. **Integration Tests**: Test full flow from tool invocation to method execution
3. **Edge Cases**: Test error handling, parameter validation, and transformation edge cases

## Next Steps After Implementation

1. **Documentation**: Update tool documentation to reflect new parameter mapping capabilities
2. **Schema Validation**: Add validation for the enhanced YAML schema
3. **Developer Tools**: Create helper utilities for tool engineers to design and validate mappings

## Links to Other Documents

- [Parameter Mapping Analysis](PARAMETER_MAPPING_ANALYSIS.md)
- [Method Parameter Integration](METHOD_PARAMETER_INTEGRATION.md)
- [Analytical Toolset Engineering](ANALYTICAL_TOOLSET_ENGINEERING.md)