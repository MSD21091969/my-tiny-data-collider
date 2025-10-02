# Changelog

All notable changes to the My Tiny Data Collider project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Week 2 kickoff release notes (`docs/WEEK2_KICKOFF_RELEASE_NOTES.md`) covering the new branch topology and readiness tasks.
- Repository-wide pull request template aligned with Week 2 checklists.

### Planned
- Integration test templates
- API test templates
- Google Workspace toolset (Gmail, Drive, Sheets)
- Tool composition and chaining framework
- Agent-driven tool selection
- Document analysis toolset
- Web scraping toolset

---

## [0.1.0] - 2025-10-02

### Added - Week 1: Tool Factory MVP ✅

#### Core Features
- **Tool Factory**: YAML-driven Python code generation
  - Jinja2 templates for tool and test generation
  - Support for 4 implementation types: simple, api_call, data_transform, composite
  - Parameter validation with Pydantic v2 constraints
  - Automatic test generation from examples and error scenarios

#### Policy System
- **Business Rules**: Access control, permissions, timeout configuration
- **Session Policies**: Session lifecycle management, request/response logging
- **Casefile Policies**: Data access control, casefile state validation
- **Audit Config**: Success/failure events, field filtering, audit trail

#### Architecture
- **N-Tier Layered Architecture**: API → Service → Tool → Persistence
- **Request/Response Models**: Different models per layer (RequestEnvelope, ToolRequest, MDSContext)
- **Context Propagation**: user_id, session_id, casefile_id flow through all layers
- **Service Layer Enforcement**: Policies enforced before tool execution

#### Generated Tools
- `echo_tool`: Example tool with 9/9 passing tests
  - Parameter validation (min/max length/value)
  - Example-driven behavior tests
  - Error scenario tests
  - Audit trail integration

#### Documentation
- `README.md`: Comprehensive project overview with testing philosophy
- `docs/POLICY_AND_USER_ID_FLOW.md`: Policy and user_id propagation
- `docs/LAYERED_ARCHITECTURE_FLOW.md`: N-tier architecture and request/response patterns
- `docs/TOOLENGINEERING_FOUNDATION.md`: Core design principles
- `.github/copilot-instructions.md`: Development guidelines for Copilot

#### Testing
- **Unit Tests**: Tool layer, business logic validation
- **Integration Tests**: Service layer (planned)
- **API Tests**: HTTP layer (planned)
- Multi-level testing strategy documented

#### Infrastructure
- Python 3.12+ with Pydantic v2
- FastAPI for HTTP API
- Firestore for persistence
- PyYAML for configuration parsing
- pytest with pytest-asyncio for testing

### Fixed
- Repository indentation errors in `casefileservice/repository.py`
- Legacy key migration (sessions → session_ids)
- Corrupted `google_workspace/clients.py` file recreated
- Template test generation (removed status field assumption)
- Pydantic v2 error message matching in tests
- YAML syntax errors in echo_tool.yaml

### Changed
- Updated tool templates to inject session/casefile/audit policies
- Enhanced test templates with example-driven testing
- Improved parameter validation with proper Pydantic v2 constraints

---

## [0.0.1] - 2025-09-XX (Pre-MVP)

### Added
- Initial project structure
- Basic service layer (CommunicationService, ToolSessionService, CasefileService)
- Pydantic models (shared, tool_session, communication, casefile)
- MDSContext for context propagation
- Tool decorator (`@register_mds_tool`)
- SOLID Pod integration (experimental)
- Firestore persistence layer

---

## Version History

- **0.1.0** (2025-10-02): Week 1 MVP - Tool Factory with policy system
- **0.0.1** (2025-09-XX): Initial structure and services

---

## Notes

### Versioning Strategy
- **MAJOR**: Breaking changes to architecture or API
- **MINOR**: New features (toolsets, policy types, layers)
- **PATCH**: Bug fixes, documentation updates

### Branch Strategy
- `main`: Stable releases
- `feature/*`: Feature development (current: `feature/tool-factory-week1`)
- `docs/*`: Documentation improvements
- `fix/*`: Bug fixes

### Release Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped in `setup.py`
- [ ] Tagged in git
