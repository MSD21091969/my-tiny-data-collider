# Core Toolsets

*Last updated: October 7, 2025*

Essential business functionality implementing primary use cases and core operations.

## Purpose

Core toolsets contain the fundamental building blocks of the system - the tools that implement the main business logic and primary user workflows. These are the most stable, well-tested, and frequently used tools.

## Characteristics

- **High Stability**: Mature, well-tested implementations
- **Business Critical**: Core functionality that users depend on
- **Standard Patterns**: Follow established implementation patterns
- **Comprehensive Coverage**: Complete feature sets for business domains

## Current Toolsets

### Casefile Management
**Location**: `core/casefile_management/`
**Business Domain**: Casefile lifecycle operations
**Implementation**: API calls to CasefileService
**Tools**: 5 (CRUD + list operations)

#### Tools Included
- `create_casefile_tool.yaml` - Create new casefiles with metadata
- `get_casefile_tool.yaml` - Retrieve casefile details
- `update_casefile_tool.yaml` - Modify casefile information
- `delete_casefile_tool.yaml` - Remove casefiles
- `list_casefiles_tool.yaml` - Query multiple casefiles

#### Business Rules
- Requires user authentication
- Casefile-specific permissions (read/write)
- Audit logging enabled
- Session tracking required

#### Integration Pattern
- Internal service calls only
- Synchronous operations
- Standard error handling
- Full audit trail

## Adding New Core Tools

### When to Add to Core
- Implements primary business functionality
- Part of main user workflows
- Requires high reliability and testing
- Follows established patterns

### Process
1. Identify appropriate business domain subdirectory
2. Create tool YAML following core patterns
3. Ensure business rules alignment
4. Add comprehensive testing
5. Update documentation

### Naming Convention
`{business_domain}_{operation_type}/`

Examples:
- `user_management/` - User account operations
- `document_processing/` - Document handling
- `communication_handling/` - Message processing