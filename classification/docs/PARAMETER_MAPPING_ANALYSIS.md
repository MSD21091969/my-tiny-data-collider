# Parameter Mapping Analysis

## Overview

The classification system found in the `config` folder is primarily designed to enable tool engineers to map request/response model fields and engineer combinations analytically. This mapping system serves as the bridge between tool parameter definitions and the actual method parameters needed for execution, while also supporting orchestration parameters that control execution behavior.

## Current Implementation

In the current system, YAML configuration files in `config/methodtools_v1/` define tools that are linked to service methods. For example:

```yaml
# CasefileService_create_casefile_tool.yaml
name: "create_casefile"
description: "Create a new casefile"
category: "casefiles"
method_reference:
  service: "CasefileService"
  method: "create_casefile"
```

However, these configurations currently lack detailed parameter mapping capabilities. The system doesn't have a clear way to:

1. Map tool parameters to method parameters
2. Handle nested parameter structures
3. Transform data types between tool and method contexts
4. Validate parameter compatibility

## The Classification Challenge

The classification system you've introduced in the `config` folder aims to solve this problem by providing a structured way to:

- Analyze parameter relationships between tools and methods
- Define transformation rules for parameter mapping
- Enable analytical engineering of parameter combinations
- Create a consistent mapping approach across all tools
- Distinguish between method parameters and orchestration parameters
- Handle bidirectional mapping for both inputs and outputs

This is particularly important because tools often have parameters that don't directly match their corresponding method parameters in name, structure, or type. Additionally, some parameters are meant for orchestration rather than being passed to methods.

## Relationship to Branch 1 (feature/ai-method-integration)

This classification system is **directly relevant to branch 1** (feature/ai-method-integration) because that branch is focused on method calling integration and parameter handling. The implementation in branch 1 would use this classification to:

1. Properly route parameters from tool invocations to method calls
2. Transform parameter values as needed
3. Validate parameter compatibility before method execution
4. Handle bidirectional mapping for both inputs and outputs
5. Process orchestration parameters separately from method parameters
6. Coordinate execution behavior based on orchestration parameters

## Bidirectional Mapping

The classification system must handle both directions of data flow:

**Input Mapping:**
- Tool parameters → Method parameters
- User inputs → Service method requirements
- Default values and transformations

**Output Mapping:**
- Method return values → Tool response format
- Error outputs → Standardized tool error responses
- Metadata enrichment for responses

## Orchestration Parameters

A key insight is the distinction between method parameters and orchestration parameters:

**Method Parameters:**
- Passed directly to the underlying service method
- Must match the method's expected signature
- May require transformations before passing

**Orchestration Parameters:**
- Used by the tool execution framework
- Control execution behavior, not method behavior
- Examples:
  - `dry_run`: For preview mode execution
  - `timeout_seconds`: For execution timeouts
  - `retry_policy`: For configuring retry behavior
  - `execution_mode`: For controlling execution flow

## Engineering Tools for Tools

The classification system enables "engineering tools for tools" - meta-tooling that makes it easier to build and configure tools:

1. **Mapping Definition Tools:**
   - YAML schema validators for mapping configurations
   - Mapping analyzers to detect potential issues

2. **Parameter Relationship Analyzers:**
   - Tools to identify common mapping patterns
   - Consistency checkers across similar tools

3. **Orchestration Configuration Tools:**
   - Configuration templates for common orchestration patterns
   - Validation tools for orchestration parameters

Without this classification system, the method integration in branch 1 would lack the necessary information to properly connect tool parameters with method parameters and handle orchestration parameters correctly.