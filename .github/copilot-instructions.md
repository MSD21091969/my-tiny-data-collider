# Copilot Instructions for my-tiny-data-collider

*Last updated: October 8, 2025*

This file provides GitHub Copilot with context about the repository structure, coding standards, and best practices for AI-assisted development.

## 📋 Project Overview

**Repository**: my-tiny-data-collider  
**Purpose**: AI-powered data processing and integration platform with tool-based architecture  
**Technology Stack**: Python 3.11+, FastAPI, Pydantic, Firebase/Firestore  
**Architecture**: Service-Repository pattern with tool-based AI integration

## 🏗️ Architecture Patterns

### Core Patterns
1. **Service-Repository Pattern**: Clean separation of business logic and data access
2. **Tool Decorator Pattern**: `@register_mds_tool` for AI tool registration
3. **Request-Response DTOs**: `BaseRequest[T]` → `BaseResponse[T]` pattern
4. **Factory Pattern**: YAML → Python tool generation
5. **R-A-R Pattern**: Request-Action-Response model alignment

### Layer Structure
```
API Layer (FastAPI) 
  ↓
Tool Request/Response Layer (ToolRequest[ToolRequestPayload])
  ↓
Method DTO Layer (BaseRequest[Payload] → BaseResponse[Payload])
  ↓
Service Layer (Business Logic)
  ↓
Repository Layer (Data Access)
```

## 💻 Code Standards

### Python Code Style
- **Async/Await**: Use for all service methods
- **Type Hints**: Required everywhere
- **Docstrings**: Comprehensive with Args, Returns, Raises
- **Error Handling**: Try-except blocks with specific exceptions
- **Validation**: Pydantic models for all data structures

### Example Service Method
```python
async def method_name(self, request: RequestModel) -> ResponseModel:
    """
    Brief description of what this method does.
    
    Args:
        request: RequestModel containing operation details
        
    Returns:
        ResponseModel with operation results
        
    Raises:
        ValidationError: If request data is invalid
        ServiceError: If operation fails
    """
    start_time = datetime.now()
    try:
        result = await self.repository.operation(request.payload)
        return ResponseModel(
            request_id=request.request_id,
            status=RequestStatus.COMPLETED,
            payload=result,
            metadata={'execution_time_ms': calculate_time(start_time)}
        )
    except Exception as e:
        # Handle error appropriately
        raise ServiceError(f"Operation failed: {str(e)}")
```

### DTO Pattern Requirements
- Follow Request-Action-Response (R-A-R) pattern
- Use `BaseRequest[PayloadT]` for all request DTOs
- Use `BaseResponse[PayloadT]` for all response DTOs
- Payload classes inherit from `BaseModel`
- Include operation field: `operation: Literal["operation_name"]`

## 🛠️ Tool Engineering

### YAML Tool Definition
Tools are defined in `config/toolsets/` following this structure:
```yaml
name: tool_name
description: "Clear, concise description"
category: "domain"
classification:
  domain: workspace
  subdomain: casefile
  capability: create
  complexity: atomic
  maturity: stable
  integration_tier: internal
implementation:
  type: api_call
  api_call:
    method_name: workspace.casefile.create_casefile
parameters:
  - name: parameter_name
    type: string
    required: true
    description: "Parameter description"
```

### Tool Generation Commands
```bash
# Generate all tools
python scripts/generate_tools.py

# Generate specific tool
python scripts/generate_tools.py tool_name

# Validate YAML only
python scripts/generate_tools.py --validate-only
```

### Tool Decorator Usage
```python
from src.pydantic_ai_integration.tool_decorator import register_mds_tool

@register_mds_tool(
    name="tool_name",
    description="Tool description",
    enabled=True,
    requires_auth=True
)
async def tool_function(ctx: MDSContext, **kwargs):
    """Tool implementation"""
    # Business logic here
    return result
```

## 📚 Key File Locations

### Documentation
- `docs/ai-collaboration/` - AI collaboration framework and practices
- `docs/methods/` - API method documentation (26 methods)
- `docs/registry/` - System architecture and classification
- `AI_ASSISTANT_KNOWLEDGE_BASE.md` - Comprehensive repository guide
- `AI_WORKSESSION_QUICKSTART.md` - Quick start for AI sessions
- `TOOL_GENERATION_WORKFLOW.md` - Tool development processes

### Source Code
- `src/pydantic_models/` - Data models (100% DTO coverage)
- `src/casefileservice/` - Casefile CRUD operations
- `src/communicationservice/` - Chat session management
- `src/tool_sessionservice/` - Tool execution lifecycle
- `src/pydantic_ai_integration/` - AI tool system and registry

### Configuration
- `config/toolsets/` - Tool YAML definitions
- `config/methods_inventory_v1.yaml` - Method registry (26 methods)
- `pyproject.toml` - Project configuration
- `pytest.ini` - Test configuration

### Scripts
- `scripts/generate_tools.py` - Tool generation
- `scripts/show_tools.py` - Display registered tools
- `scripts/audit_pydantic_examples.py` - Model validation

## 🧪 Testing Standards

### Test Coverage Requirements
- **Minimum Coverage**: 80% overall, 85% for new AI-generated code
- **Test Types**: Unit, integration, and end-to-end tests
- **Performance**: API response time <200ms

### Test Structure
```python
def test_function_name():
    """Test description following AAA pattern."""
    # Arrange
    mock_repo = Mock()
    service = ServiceClass(mock_repo, mock_id_service)
    request = RequestModel(valid_test_data)
    
    # Act
    result = await service.method(request)
    
    # Assert
    assert result.status == RequestStatus.COMPLETED
    assert result.payload is not None
    mock_repo.method.assert_called_once()
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/test_specific.py -v

# Run by marker
pytest -m unit
```

## 🔒 Security Requirements

### Authentication & Authorization
- All service methods require user authentication
- Use `user_id` from request context
- Validate permissions before operations
- Include audit trail in metadata

### Input Validation
- Validate all inputs with Pydantic models
- Sanitize user-provided data
- Check for SQL injection, XSS risks
- Rate limit API endpoints

### Prohibited AI Uses
- Do not generate authentication/authorization code
- Do not create production deployment configs
- Do not write financial calculation logic
- Do not generate legal/compliance documentation

## 📊 Quality Standards

### Code Quality
- **Pylint Score**: >8.0
- **Type Coverage**: 100% type hints
- **Documentation**: All public methods documented
- **Error Handling**: Comprehensive exception handling

### Review Process
- All AI-generated code requires human review
- Senior developer approval for significant changes
- PR must include tests and documentation updates
- CI/CD pipeline must pass all checks

## 🔄 Development Workflow

### Daily Development Cycle
1. **Planning**: Use AI for task breakdown and design
2. **Implementation**: Leverage Copilot with established patterns
3. **Generation**: Use ToolFactory for YAML → Python conversion
4. **Testing**: Apply comprehensive test helpers and validation
5. **Review**: Human review following quality guidelines
6. **Integration**: Automated quality gates and deployment

### Commit Standards
```
type(scope): Short description

- Bullet point with factual changes
- Another bullet point
- No emojis, code examples over prose
```

**Types**: feat, fix, refactor, test, docs, chore

## 🎯 Current Priorities

### Priority 1: DTO Inheritance
- Tools should inherit parameters from method DTOs
- Eliminate parameter duplication in tool YAMLs
- Update ToolFactory to resolve methods from MANAGED_METHODS
- Ensure type-safe mapping from tool parameters to method DTOs

### Priority 2: R-A-R Pattern Alignment
- All DTOs must follow Request-Action-Response pattern
- Format: `{Action}Request(BaseRequest[{Action}Payload])`
- Ensure consistency across all layers
- Update documentation and examples

### Priority 3: Method Registry Enhancement
- Maintain 26 registered methods in MANAGED_METHODS
- Accurate model references in `methods_inventory_v1.yaml`
- Complete API documentation for all methods
- Classification schema compliance

## 📖 Documentation Standards

### README Updates
- Update all affected README files with current dates
- Include clear examples and usage instructions
- Cross-reference related documentation
- Keep table of contents current

### API Documentation
- Document all public methods with examples
- Include request/response models
- Show error cases and handling
- Provide integration examples

### Inline Comments
- Use comments sparingly, prefer self-documenting code
- Explain complex algorithms or business logic
- Document workarounds or technical debt
- Reference related issues or decisions

## 🆘 Troubleshooting

### Common Issues
- **Tool Generation Fails**: Check YAML syntax and method references
- **Import Errors**: Verify MANAGED_METHODS registry is loaded
- **Test Failures**: Check DTO compatibility and mocking setup
- **Performance Issues**: Review async/await patterns and queries

### Getting Help
- Review `AI_ASSISTANT_KNOWLEDGE_BASE.md` for comprehensive guidance
- Check `docs/ai-collaboration/` for AI practices
- Consult `TOOL_GENERATION_WORKFLOW.md` for tool engineering
- See `docs/methods/` for API reference

## 🔗 Related Resources

- [AI Collaboration Framework](../docs/ai-collaboration/README.md)
- [Develop Branch Guide](../docs/ai-collaboration/workflows/develop-branch-guide.md)
- [Quality Assurance](../docs/ai-collaboration/workflows/quality-assurance.md)
- [Conversation Practices](../docs/ai-collaboration/practices/conversation-practices.md)
- [VS Code Setup](../docs/ai-collaboration/practices/vscode-setup.md)

---

**Note**: This file is version-controlled and should be updated when major architecture or process changes occur. Keep it synchronized with the main documentation.
