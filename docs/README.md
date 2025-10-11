# Documentation Index

**Project:** Tiny Data Collider (MDS - My Data System)  
**Last Updated:** October 11, 2025

---

## 📚 Table of Contents

- [Architecture Documentation](#architecture-documentation)
- [Service Documentation](#service-documentation)
- [Registry System](#registry-system)
- [Implementation Guides](#implementation-guides)
- [Specifications](#specifications)
- [Archive](#archive)

---

## 🏗️ Architecture Documentation

**Location:** [`docs/architecture/`](./architecture/)

Core architectural components and system-wide patterns.

| Document | Description | Status |
|----------|-------------|--------|
| [Core Service Overview](./architecture/CORE_SERVICE_OVERVIEW.md) | RequestHub, ServiceContainer, context management | ✅ Current |
| [Persistence Overview](./architecture/PERSISTENCE_OVERVIEW.md) | Firestore/Redis integration patterns | ✅ Current |
| [Persistence Layer](./architecture/PERSISTENCE_LAYER.md) | BaseRepository pattern, connection pooling, caching | ✅ Current |
| [Pydantic AI Integration](./architecture/PYDANTIC_AI_INTEGRATION_OVERVIEW.md) | Tool/method registration, MDSContext, session management | ✅ Current |
| [Pydantic API Overview](./architecture/PYDANTIC_API_OVERVIEW.md) | FastAPI application, middleware, routers | ✅ Current |
| [Pydantic Models Overview](./architecture/PYDANTIC_MODELS_OVERVIEW.md) | Request/Response models, transformations | ✅ Current |

**Key Concepts:**
- Request-Action-Response (R-A-R) pattern
- Service-Repository pattern
- Dependency injection with ServiceContainer
- Context propagation and lifecycle hooks

---

## 🔧 Service Documentation

**Location:** [`docs/services/`](./services/)

Individual service implementations and their responsibilities.

| Service | Document | Responsibilities |
|---------|----------|-----------------|
| **Auth Service** | [AUTHSERVICE_OVERVIEW.md](./services/AUTHSERVICE_OVERVIEW.md) | JWT token generation, validation, user authentication |
| **Casefile Service** | [CASEFILE_SERVICE_OVERVIEW.md](./services/CASEFILE_SERVICE_OVERVIEW.md) | Workspace management, permissions, document storage |
| **Communication Service** | [COMMUNICATION_SERVICE_OVERVIEW.md](./services/COMMUNICATION_SERVICE_OVERVIEW.md) | Chat sessions, message handling, tool integration |
| **Tool Session Service** | [TOOL_SESSION_SERVICE_OVERVIEW.md](./services/TOOL_SESSION_SERVICE_OVERVIEW.md) | Tool execution lifecycle, session tracking, audit trails |

**Service Patterns:**
- All services use dependency injection
- Context-aware execution with ServiceContext
- Repository pattern for data access
- Async/await throughout

---

## 🔧 Registry System

**Location:** [`docs/registry/`](./registry/)

Complete documentation for the unified registry consolidation system (TIER 3 #7).

| Document | Description | Audience |
|----------|-------------|----------|
| [Registry Consolidation Guide](./registry/REGISTRY_CONSOLIDATION.md) | **Main guide** - Usage, validation modes, troubleshooting | Developers, Operators |
| [Registry Consolidation Summary](./registry/REGISTRY_CONSOLIDATION_SUMMARY.md) | Project completion summary, phases, statistics | Project Managers |
| [Registry Consolidation Analysis](./registry/REGISTRY_CONSOLIDATION_ANALYSIS.md) | Initial analysis and design decisions | Architects |

**Quick Start:**
```python
from pydantic_ai_integration import initialize_registries

result = initialize_registries()
if not result.success:
    raise RuntimeError(f"Registry validation failed: {result.errors}")
```

**Key Features:**
- ✅ Unified loading with `RegistryLoader`
- ✅ Validation modes: STRICT/WARNING/OFF
- ✅ Coverage, consistency, drift detection
- ✅ CI/CD integration
- ✅ 52 comprehensive tests (100% passing)

**Status:** ✅ Complete (Phase 6/6) - October 11, 2025

---

## 📖 Implementation Guides

**Location:** [`docs/guides/`](./guides/)

Step-by-step guides for implementing specific features.

| Guide | Description | Use Case |
|-------|-------------|----------|
| [Token Schema](./guides/TOKEN_SCHEMA.md) | JWT token structure, claims, service tokens | Authentication, authorization |
| [Request Context Flow](./guides/REQUEST_CONTEXT_FLOW.md) | R-A-R lifecycle, context preparation, hooks | Service development |

**Topics Covered:**
- Token payload structure and routing metadata
- Session context propagation
- Service transformation pattern (prepare → execute → enrich)
- Pre/post execution hooks

---

## 📋 Specifications

**Location:** [`docs/specifications/`](./specifications/)

Project specifications, requirements, and inventory documents.

| Document | Description | Status |
|----------|-------------|--------|
| [MVP Specification](./specifications/MVP_SPECIFICATION.md) | Minimum viable product definition, user journeys, acceptance criteria | ✅ Complete |
| [Toolset Inventory Coverage](./specifications/TOOLSET_INVENTORY_COVERAGE.md) | Complete tool inventory, coverage analysis, recommendations | ✅ Complete |

**MVP Details:**
- 10 essential tools across 5 user journeys
- 100% YAML validation (all 10 MVP tools)
- Integration tests: 5/7 passing (71%)
- Performance targets: p95 <500ms

**Toolset Coverage:**
- 34 methods with tool definitions (100% coverage)
- Classification by domain, capability, complexity
- Load testing recommendations

---

## 📦 Archive

**Location:** [`docs/archive/`](./archive/)

Historical documentation and superseded design documents.

| Document | Reason for Archive |
|----------|-------------------|
| ANALYTICAL_TOOLSET_ENGINEERING.md | Superseded by TOOLSET_INVENTORY_COVERAGE.md |
| METHOD_PARAMETER_INTEGRATION.md | Integrated into PYDANTIC_AI_INTEGRATION_OVERVIEW.md |
| PARAMETER_MAPPING_ANALYSIS.md | Superseded by registry consolidation docs |
| TOOL_DEVELOPMENT_WORKFLOW.md | Integrated into REGISTRY_CONSOLIDATION.md |

---

## 🗺️ Documentation Structure

```
docs/
├── README.md                          # This file - main index
├── architecture/                      # System architecture
│   ├── CORE_SERVICE_OVERVIEW.md
│   ├── PERSISTENCE_OVERVIEW.md
│   ├── PERSISTENCE_LAYER.md
│   ├── PYDANTIC_AI_INTEGRATION_OVERVIEW.md
│   ├── PYDANTIC_API_OVERVIEW.md
│   └── PYDANTIC_MODELS_OVERVIEW.md
├── services/                          # Individual services
│   ├── AUTHSERVICE_OVERVIEW.md
│   ├── CASEFILE_SERVICE_OVERVIEW.md
│   ├── COMMUNICATION_SERVICE_OVERVIEW.md
│   └── TOOL_SESSION_SERVICE_OVERVIEW.md
├── registry/                          # Registry consolidation
│   ├── REGISTRY_CONSOLIDATION.md           # Main guide
│   ├── REGISTRY_CONSOLIDATION_SUMMARY.md   # Project summary
│   └── REGISTRY_CONSOLIDATION_ANALYSIS.md  # Design analysis
├── guides/                            # Implementation guides
│   ├── TOKEN_SCHEMA.md
│   └── REQUEST_CONTEXT_FLOW.md
├── specifications/                    # Project specs
│   ├── MVP_SPECIFICATION.md
│   └── TOOLSET_INVENTORY_COVERAGE.md
└── archive/                           # Historical docs
    ├── ANALYTICAL_TOOLSET_ENGINEERING.md
    ├── METHOD_PARAMETER_INTEGRATION.md
    ├── PARAMETER_MAPPING_ANALYSIS.md
    └── TOOL_DEVELOPMENT_WORKFLOW.md
```

---

## 🎯 Quick Navigation

### For New Developers
1. Start with [Core Service Overview](./architecture/CORE_SERVICE_OVERVIEW.md)
2. Read [Pydantic AI Integration](./architecture/PYDANTIC_AI_INTEGRATION_OVERVIEW.md)
3. Review [MVP Specification](./specifications/MVP_SPECIFICATION.md)
4. Check [Registry Consolidation Guide](./registry/REGISTRY_CONSOLIDATION.md)

### For Service Development
1. [Request Context Flow](./guides/REQUEST_CONTEXT_FLOW.md)
2. [Token Schema](./guides/TOKEN_SCHEMA.md)
3. [Persistence Layer](./architecture/PERSISTENCE_LAYER.md)
4. Relevant service overview from [`services/`](./services/)

### For Tool Engineering
1. [Registry Consolidation Guide](./registry/REGISTRY_CONSOLIDATION.md)
2. [Pydantic AI Integration](./architecture/PYDANTIC_AI_INTEGRATION_OVERVIEW.md)
3. [Toolset Inventory](./specifications/TOOLSET_INVENTORY_COVERAGE.md)

### For Operations
1. [Registry Consolidation Guide](./registry/REGISTRY_CONSOLIDATION.md) (CI/CD section)
2. [MVP Specification](./specifications/MVP_SPECIFICATION.md)
3. [Persistence Layer](./architecture/PERSISTENCE_LAYER.md) (metrics section)

---

## 📝 Documentation Standards

### File Naming Convention
- Use `SCREAMING_SNAKE_CASE.md` for all documentation files
- Descriptive names that indicate content purpose
- Suffix with `_OVERVIEW`, `_GUIDE`, `_SPECIFICATION`, `_SUMMARY` as appropriate

### Document Structure
All documents should include:
- **Tags:** `#tag1` `#tag2` for searchability
- **Table of Contents:** For documents >200 lines
- **Status:** Current, Complete, In Progress, Archived
- **Last Updated:** Date of last significant change
- **Related Documents:** Cross-references to other docs

### Maintenance
- Review quarterly for accuracy
- Archive outdated documents
- Update cross-references when moving files
- Keep README.md index current

---

## 🔄 Related Resources

- [Branch Development Plan](../BRANCH_DEVELOPMENT_PLAN.md) - Project roadmap and milestone tracking
- [GitHub Workflows](../.github/workflows/README.md) - CI/CD documentation
- [Scripts Documentation](../scripts/) - Tool development and validation scripts
- [Project README](../README.md) - Project overview and setup instructions

---

## 📞 Support

For questions or clarifications about documentation:

1. Check the relevant document's Table of Contents
2. Review cross-referenced documents
3. Search for tags/keywords across docs
4. Open an issue with specific questions

---

**Last Updated:** October 11, 2025  
**Documentation Version:** 2.0 (Post-reorganization)  
**Total Documents:** 18 active documents across 5 categories
