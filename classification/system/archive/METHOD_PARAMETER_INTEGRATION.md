# Method Parameter Integration

## The Problem

In the current implementation of the tool system, there's a disconnect between how tools define their parameters and how the underlying methods expect parameters. Let's examine a typical tool YAML definition from `config/methodtools_v1/`:

```yaml
name: "create_casefile"
description: "Create a new casefile"
category: "casefiles"
method_reference:
  service: "CasefileService"
  method: "create_casefile"
tool_params:
  - name: "dry_run"
    type: "boolean"
    description: "Preview mode without execution"
    default: false
```

When this tool is invoked, how does the system know which parameters should be passed to the `create_casefile` method versus which parameters are tool-specific (like `dry_run`)? The system currently lacks a formal mechanism to make this distinction.

## The Classification Solution

Your classification approach in the `config` folder aims to create a structured mapping between:

1. **Tool Parameters**: Parameters defined in the tool YAML
2. **Method Parameters**: Parameters expected by the underlying service method

This classification would define relationships such as:
- Direct mappings (tool.title → method.title)
- Transformations (tool.date_string → method.date as DateTime)
- Nested mappings (tool.user.id → method.user_id)

## Why This Belongs in Branch 1

Branch 1 (feature/ai-method-integration) is focused on implementing the actual method calling functionality. The classification system you've created provides the essential mapping information needed to:

1. Determine which parameters to extract from the tool invocation
2. Transform these parameters into the format expected by the method
3. Validate that all required method parameters are provided

Without this classification, branch 1 would need to implement its own parameter mapping logic, likely resulting in inconsistencies across different tool implementations.

## Implementation Approach

In branch 1, this classification would be used to enhance the `register_tools_from_yaml()` function in `tool_decorator.py`. The function would:

1. Load your classification mapping
2. Use it when executing the tool function
3. Apply the appropriate transformations before calling the actual service method

This creates a flexible, configuration-driven approach to parameter mapping that can be extended without code changes.