# 🤖 AI Assistant Repository Intelligence Guide

*Last updated: October 7, 2025*

**Comprehensive knowledge base for AI assistants working with the my-tiny-data-collider repository**

---

## 📋 Repository Overview

**Name**: my-tiny-data-collider
**Owner**: MSD21091969
**Primary Branch**: develop
**Technology Stack**: Python 3.11+, FastAPI, Pydantic, Firebase/Firestore
**Architecture**: Service-Repository pattern with tool-based AI integration

---

## 🗂️ Repository Structure & Navigation

### Core Directories
```
my-tiny-data-collider/
├── src/                          # Source code
│   ├── pydantic_models/          # Data models (100% DTO coverage)
│   ├── casefileservice/          # Casefile CRUD operations
│   ├── communicationservice/     # Chat session management
│   ├── tool_sessionservice/      # Tool execution lifecycle
│   └── pydantic_ai_integration/  # AI tool system
├── config/                       # Configuration files
│   ├── toolsets/                 # Organized tool YAMLs
│   └── methods_inventory_v1.yaml # Method registry (26 methods)
├── docs/                         # Documentation
│   ├── ai-collaboration/         # AI practices & workflows
│   ├── methods/                  # API documentation
│   └── registry/                 # System architecture
├── scripts/                      # Automation scripts
├── tests/                        # Test suites
└── .vscode/                      # VS Code configuration
```

### Key Files for AI Understanding
- **`WORKSESSION_HANDOVER.md`** - Current development state & priorities
- **`AI_WORKSESSION_QUICKSTART.md`** - Getting started guide
- **`TOOL_GENERATION_WORKFLOW.md`** - Tool engineering processes
- **`docs/ai-collaboration/README.md`** - AI collaboration framework

---

## 🎯 Development Practices & Standards

### Code Standards
```python
# Required patterns
async def method_name(self, request: RequestModel) -> ResponseModel:
    """Comprehensive docstring with Args, Returns, Raises."""
    start_time = datetime.now()
    result = await self.repository.operation(request.payload)
    return ResponseModel(
        request_id=request.request_id,
        status=RequestStatus.COMPLETED,
        payload=result,
        metadata={'execution_time_ms': execution_time}
    )
```

**Requirements**:
- Type hints required everywhere
- Pydantic models for all data structures
- Async/await for service methods
- Comprehensive error handling
- 80%+ test coverage

### Architecture Patterns
- **Service-Repository**: Clean separation of business logic and data access
- **Tool Decorator**: `@register_mds_tool` for AI tool registration
- **Request-Response DTOs**: `BaseRequest[T]` → `BaseResponse[T]` pattern
- **Factory Pattern**: YAML → Python tool generation

---

## 🤖 AI Collaboration Framework

### Essential Documentation
- **`docs/ai-collaboration/README.md`** - Framework overview
- **`docs/ai-collaboration/practices/conversation-practices.md`** - How to interact with humans
- **`docs/ai-collaboration/workflows/quality-assurance.md`** - Review standards
- **`docs/ai-collaboration/workflows/develop-branch-guide.md`** - Branch-specific practices

### Prompt Templates
**Location**: `docs/ai-collaboration/prompts/`
- `code-generation.md` - Code creation guidelines
- VS Code integration: `.vscode/prompts/`

### Quality Standards
- **Test Coverage**: 85% minimum for AI-generated code
- **Review Required**: Senior developer review for AI contributions
- **Documentation**: Update all affected READMEs with dates
- **Security**: No AI generation of authentication or sensitive code

---

## 🛠️ Tool Engineering System

### Tool Generation Workflow
```bash
# Generate tools from YAML
python scripts/generate_tools.py

# Generate specific tool
python scripts/generate_tools.py tool_name

# Validate YAML without generation
python scripts/generate_tools.py --validate-only
```

### Tool YAML Structure
```yaml
name: tool_name
description: "Clear description"
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
```

### Registry Systems
```python
# MANAGED_METHODS - Service methods registry
from src.pydantic_ai_integration.method_registry import get_registered_methods
methods = get_registered_methods()  # Returns 26 method definitions

# MANAGED_TOOLS - Tool registry
from src.pydantic_ai_integration.tool_decorator import get_registered_tools
tools = get_registered_tools()  # Returns registered tool definitions
```

---

## 🧪 Testing & Quality Assurance

### Test Execution
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_specific.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run integration tests only
pytest tests/integration/
```

### Test Structure
```python
def test_ai_generated_function():
    """Test AI-generated functionality."""
    # Arrange
    mock_repo = Mock()
    service = Service(mock_repo, mock_id_service)
    request = RequestModel(valid_data)

    # Act
    result = await service.method(request)

    # Assert
    assert result.status == RequestStatus.COMPLETED
    assert result.payload is not None
```

### Quality Gates
- **Unit Tests**: Individual function validation
- **Integration Tests**: Component interaction verification
- **End-to-End Tests**: Complete workflow validation
- **Performance Tests**: Response time <200ms benchmarks

---

## 📚 API Reference & Documentation

### Service Methods (26 total)
**Location**: `docs/methods/`
- **CasefileService** (13): CRUD operations, ACL, workspace sync
- **CommunicationService** (6): Chat sessions, processing
- **ToolSessionService** (5): Tool execution lifecycle
- **External Services** (2): GmailClient, DriveClient

### Method Registry
**Location**: `docs/registry/`
- `reference.md` - Classification schema and statistics
- `CHANGELOG.md` - Version history
- `versioning-guide.md` - Semantic versioning rules

### Data Models
**Location**: `src/pydantic_models/`
- `base/` - BaseRequest[T], BaseResponse[T], RequestStatus
- `operations/` - Service-specific DTOs (100% coverage)
- `canonical/` - Core business entities

---

## 🔄 Development Workflows

### Daily Development Cycle
1. **Planning**: Use AI for task breakdown and design
2. **Implementation**: Leverage Copilot with established templates
3. **Generation**: Use ToolFactory for YAML → Python conversion
4. **Testing**: Apply comprehensive test helpers and validation
5. **Review**: Human review following quality assurance guidelines
6. **Integration**: Automated quality gates and deployment

### Branch Management
- **develop**: Main integration branch (current work location)
- **Feature Branches**: Created from develop for specific enhancements
- **AI Disclosure**: Include AI contribution disclosure in PRs
- **Quality Gates**: All AI-generated content passes review

### Commit Standards
```
type(scope): Short description

- Bullet points with facts only
- No emojis, code examples over prose
```

**Types**: feat, fix, refactor, test, docs, chore

---

## 🚨 Critical Constraints & Rules

### Prohibited AI Uses
- Security-sensitive authentication code
- Production deployment configurations
- Legal or compliance documentation
- Financial calculation logic

### Quality Requirements
- **Test Coverage**: Maintain 80%+ overall coverage
- **Code Quality**: Pylint score >8.0
- **Performance**: API response time <200ms
- **Security**: Input validation and authentication checks

### Documentation Standards
- **README Updates**: Update all affected files with current dates
- **API Documentation**: Comprehensive method docs with examples
- **Cross-References**: Maintain accurate links between documents

---

## 🆘 Troubleshooting & Support

### Common Issues
- **Tool Generation Fails**: Check YAML syntax and method references
- **Import Errors**: Verify MANAGED_METHODS registry is loaded
- **Test Failures**: Check DTO compatibility and mocking setup
- **Performance Issues**: Review async/await patterns and database queries

### Getting Help
- **AI Collaboration**: `docs/ai-collaboration/README.md`
- **Technical Issues**: `docs/methods/README.md` (API reference)
- **Architecture**: `docs/registry/README.md` (system design)
- **Tool Engineering**: `TOOL_GENERATION_WORKFLOW.md`

### Escalation Paths
- **AI Quality Issues**: Contact development team lead
- **Security Concerns**: Escalate to architecture team
- **Performance Problems**: Use GitHub issues with performance label

---

## 📊 Metrics & Success Criteria

### Quality Metrics
- **Code Review Pass Rate**: Target 90% for AI-generated code
- **Test Coverage**: Minimum 85% for new AI contributions
- **Bug Rate**: <5 bugs per 1000 lines of AI-generated code
- **Performance**: Meet established API benchmarks

### Process Metrics
- **AI Usage Rate**: 60-70% of development tasks
- **Review Turnaround**: Maximum 4 hours for standard reviews
- **Integration Success**: 95% successful CI/CD pipeline runs
- **Documentation Compliance**: 100% of changes documented

---

## 🔧 Essential Commands & Scripts

### Development Environment
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn main:app --reload
```

### Tool Engineering
```bash
# Generate all tools
python scripts/generate_tools.py

# Generate specific tool
python scripts/generate_tools.py tool_name

# Validate YAML
python scripts/generate_tools.py --validate-only

# Clean generated files
.\scripts\cleanup_generated_files.ps1
```

### Testing & Quality
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/test_specific.py -v

# Code quality check
pylint src/
```

### Documentation
```bash
# Generate API docs
python scripts/generate_method_docs.py

# Show registered tools
python scripts/show_tools.py
```

---

## 🎯 Current Development Priorities

### Priority 1: DTO Inheritance (Immediate)
**Objective**: Tools inherit method DTOs directly from MANAGED_METHODS registry
**Implementation**: Update ToolFactory → Modify templates → Remove parameter duplication
**Success Criteria**: Tools automatically sync with method contract changes

### Priority 2: Enhanced Tool YAML Schema
**Objective**: Extend YAML to optionally generate embedded DTOs
**Benefits**: Self-contained tool definitions with version control

### Priority 3: R-A-R Alignment
**Objective**: Align all DTOs across layers with R-A-R specifications
**Scope**: Complete Request-Action-Response pattern alignment

---

## 📖 Key Documentation References

| Topic | Primary Document | Secondary References |
|-------|------------------|---------------------|
| **AI Collaboration** | `docs/ai-collaboration/README.md` | `docs/ai-collaboration/practices/`, `docs/ai-collaboration/workflows/` |
| **Tool Engineering** | `TOOL_GENERATION_WORKFLOW.md` | `src/pydantic_ai_integration/tools/`, `config/toolsets/` |
| **API Reference** | `docs/methods/README.md` | `docs/methods/workspace/`, `docs/methods/communication/` |
| **System Architecture** | `docs/registry/README.md` | `docs/registry/reference.md`, `src/pydantic_models/` |
| **Quality Assurance** | `docs/ai-collaboration/workflows/quality-assurance.md` | `tests/`, `pytest.ini` |
| **Development Setup** | `AI_WORKSESSION_QUICKSTART.md` | `WORKSESSION_HANDOVER.md`, `.vscode/settings.json` |

---

## 🤝 Human-AI Collaboration Protocols

### Communication Standards
- **Clarity**: Use precise, unambiguous language
- **Context**: Provide sufficient background and constraints
- **Specificity**: Define exact requirements and acceptance criteria
- **Structure**: Organize requests in logical, scannable formats

### Quality Validation
- **Review Required**: All AI-generated code undergoes human review
- **Testing Mandatory**: Automated and manual validation required
- **Documentation**: Record successful patterns and lessons learned
- **Standards Compliance**: Follow established project conventions

### Feedback Loop
- **Iterative Process**: Expect multiple refinement cycles
- **Specific Feedback**: Provide actionable improvement suggestions
- **Pattern Documentation**: Record successful approaches for future use
- **Continuous Learning**: Update practices based on outcomes

---

**This guide provides comprehensive intelligence for effective AI assistance with the my-tiny-data-collider repository. Use it to understand context, navigate the codebase, and follow established practices.** 🤖📚