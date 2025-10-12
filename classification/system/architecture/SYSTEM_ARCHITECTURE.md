# System Architecture Documentation

**Version:** 1.0.0
**Created:** October 11, 2025
**Last Updated:** October 11, 2025
**Status:** Active Documentation
**Context:** Bottom-up system description from code to architecture

---

## Executive Summary

This document provides a unified, bottom-up description of the Tiny Data Collider system, starting from code implementation and building up to architectural concepts. It consolidates existing overview documentation with systematic classification and versioning practices.

**Key Principles:**

- **Bottom-up approach**: Start with code, build to architecture
- **Unified terminology**: Consistent nomenclature across all layers
- **Classification-driven**: Reference GRAND_CLASSIFICATION_PLAN.md for systematic organization
- **Version-aware**: Track changes and evolution
- **R-A-R pattern**: Request-Action-Response orchestration throughout

---

## Part 1: Code Foundation (Bottom Layer)

### 1.1 Directory Structure & Module Organization

```text
src/
├── __init__.py                          # System bootstrap, version tracking
├── coreservice/                         # Core infrastructure services
│   ├── __init__.py
│   ├── service_container.py            # DI registry: ServiceContainer, ServiceManager
│   ├── context_aware_service.py        # Context propagation, lifecycle hooks
│   ├── service_caching.py              # Resilience: Cache, ConnectionPool, CircuitBreaker
│   ├── service_metrics.py              # Observability: MetricsCollector, PerformanceProfiler
│   ├── config.py                       # MDSConfig, environment validation
│   ├── health_checker.py               # Health check endpoints
│   ├── request_hub.py                  # R-A-R orchestrator
│   └── id_service.py                   # ID generation utilities
├── pydantic_ai_integration/            # Tool engineering framework
│   ├── __init__.py                     # Registry bootstrap from YAML + decorators
│   ├── dependencies.py                 # MDSContext, persistence helpers
│   ├── method_decorator.py             # @register_service_method decorator
│   ├── method_definition.py            # ManagedMethodDefinition schema
│   ├── method_registry.py              # MANAGED_METHODS registry
│   ├── model_registry.py               # Model discovery/lookup
│   ├── session_manager.py              # Tool session lifecycle
│   ├── tool_decorator.py               # @register_mds_tool decorator
│   ├── tool_definition.py              # ManagedToolDefinition schema
│   ├── tool_utils.py                   # Tool execution helpers
│   ├── execution/                      # Tool execution engines
│   ├── integrations/                   # External system adapters
│   └── tools/                          # YAML-backed tool implementations
├── casefileservice/                    # Casefile domain service
│   ├── __init__.py
│   ├── repository.py                   # Firestore persistence
│   ├── service.py                      # ContextAwareService implementation
│   ├── models/
│   │   ├── casefile.py                 # Canonical casefile entity
│   │   └── permission.py               # ACL models
│   ├── mappers/
│   │   └── casefile_mapper.py          # DTO ↔ domain transformations
│   └── tools/                          # Tool specifications
├── communicationservice/               # Communication domain service
├── tool_sessionservice/                # Tool session management
├── authservice/                        # Authentication service
├── persistence/                        # Persistence layer
├── pydantic_api/                       # API layer
├── pydantic_models/                    # Pydantic model definitions
└── toolsets/                           # Toolset configurations
```

### 1.2 Core Classes & Managers

#### Service Infrastructure Classes

| Class | Module | Purpose | Classification |
|-------|--------|---------|----------------|
| `ServiceContainer` | `coreservice/service_container.py` | Lazy DI registry for services/repositories | infrastructure, dependency-injection |
| `ServiceManager` | `coreservice/service_container.py` | High-level service accessor | infrastructure, facade |
| `ContextAwareService` | `coreservice/context_aware_service.py` | Base class with context propagation | infrastructure, lifecycle |
| `ServiceContext` | `coreservice/context_aware_service.py` | Request/session metadata container | infrastructure, context |
| `RequestHub` | `coreservice/request_hub.py` | R-A-R orchestrator | infrastructure, orchestration |
| `MDSConfig` | `coreservice/config.py` | Typed configuration tree | infrastructure, configuration |

#### Tool Engineering Classes

| Class | Module | Purpose | Classification |
|-------|--------|---------|----------------|
| `ManagedToolDefinition` | `pydantic_ai_integration/tool_definition.py` | Tool metadata + execution schema | tool-engineering, definition |
| `ManagedMethodDefinition` | `pydantic_ai_integration/method_definition.py` | Method metadata + classification | method-engineering, definition |
| `MDSContext` | `pydantic_ai_integration/dependencies.py` | Runtime context for tool execution | tool-engineering, context |
| `MANAGED_TOOLS` | `pydantic_ai_integration/tool_decorator.py` | Global tool registry | tool-engineering, registry |
| `MANAGED_METHODS` | `pydantic_ai_integration/method_registry.py` | Global method registry | method-engineering, registry |

#### Domain Service Classes

| Class | Module | Purpose | Classification |
|-------|--------|---------|----------------|
| `CasefileService` | `casefileservice/service.py` | Casefile business logic | domain-service, workspace |
| `CasefileRepository` | `casefileservice/repository.py` | Firestore persistence adapter | persistence, repository |
| `CasefileModel` | `casefileservice/models/casefile.py` | Canonical casefile entity | domain-model, entity |
| `CasefileMapper` | `casefileservice/mappers/casefile_mapper.py` | DTO ↔ domain transformations | mapping, transformation |

### 1.3 Method & Tool Definitions

#### Core Methods (MANAGED_METHODS Registry)

| Method Name | Service | Domain | Capability | Complexity | Classification |
|-------------|---------|--------|------------|------------|----------------|
| `create_casefile` | CasefileService | workspace | create | atomic | stable, internal |
| `get_casefile` | CasefileService | workspace | read | atomic | stable, internal |
| `update_casefile` | CasefileService | workspace | update | atomic | stable, internal |
| `delete_casefile` | CasefileService | workspace | delete | atomic | stable, internal |
| `list_casefiles` | CasefileService | workspace | read | atomic | stable, internal |
| `add_session_to_casefile` | CasefileService | workspace | update | atomic | stable, internal |
| `grant_permission` | CasefileService | workspace | update | atomic | stable, internal |
| `revoke_permission` | CasefileService | workspace | update | atomic | stable, internal |
| `list_permissions` | CasefileService | workspace | read | atomic | stable, internal |
| `check_permission` | CasefileService | workspace | read | atomic | stable, internal |

#### Tool Implementations (MANAGED_TOOLS Registry)

| Tool Name | Method Reference | Category | Execution Pattern | Classification |
|-----------|------------------|----------|-------------------|----------------|
| `create_casefile_tool` | CasefileService.create_casefile | workspace_management | simple | method_wrapper, basic |
| `get_casefile_tool` | CasefileService.get_casefile | workspace_management | simple | method_wrapper, basic |
| `update_casefile_tool` | CasefileService.update_casefile | workspace_management | simple | method_wrapper, basic |
| `delete_casefile_tool` | CasefileService.delete_casefile | workspace_management | simple | method_wrapper, basic |
| `list_casefiles_tool` | CasefileService.list_casefiles | workspace_management | simple | method_wrapper, basic |
| `add_session_to_casefile_tool` | CasefileService.add_session_to_casefile | workspace_management | simple | method_wrapper, basic |

---

## Part 2: Service Layer Architecture

### 2.1 Service Container & Dependency Injection

**ServiceContainer** (`coreservice/service_container.py`):

- Lazy-loaded DI registry
- Manages service lifecycles
- Provides typed accessors for services/repositories
- Classification: infrastructure, dependency-injection

**ServiceManager** (`coreservice/service_container.py`):

- High-level facade over ServiceContainer
- Groups related services by domain
- Provides business-logic access patterns
- Classification: infrastructure, facade

### 2.2 Context Propagation Framework

**ContextAwareService** (`coreservice/context_aware_service.py`):

- Abstract base class for all domain services
- Implements context injection and lifecycle hooks
- Provides async/sync execution wrappers
- Classification: infrastructure, lifecycle

**ServiceContext** (`coreservice/context_aware_service.py`):
- Pydantic model containing request metadata
- Includes user_id, session_id, casefile_id, correlation_id
- Propagated through all service calls
- Classification: infrastructure, context

### 2.3 Request-Action-Response (R-A-R) Orchestration

**RequestHub** (`coreservice/request_hub.py`):

- Central orchestrator for all operations
- Routes BaseRequest objects to appropriate handlers
- Implements R-A-R pattern: Request → Action → Response
- Classification: infrastructure, orchestration

**R-A-R Flow**:

1. **Request**: Typed request object with operation metadata
2. **Action**: Service execution with context and hooks
3. **Response**: Typed response with audit metadata

---

## Part 3: Tool Engineering Framework

### 3.1 Registry System

**MANAGED_METHODS** (`pydantic_ai_integration/method_registry.py`):

- Global registry of service methods
- Populated from YAML inventories and decorators
- Provides discovery and lookup APIs
- Classification: method-engineering, registry

**MANAGED_TOOLS** (`pydantic_ai_integration/tool_decorator.py`):

- Global registry of executable tools
- Populated from YAML definitions and decorators
- Provides execution and discovery APIs
- Classification: tool-engineering, registry

### 3.2 Tool Definition Schema

**ManagedToolDefinition** (`pydantic_ai_integration/tool_definition.py`):

- Core schema for tool metadata
- Includes classification, parameters, implementation
- Supports method inheritance and orchestration
- Classification: tool-engineering, definition

**Tool Classification Dimensions** (aligned with GRAND_CLASSIFICATION_PLAN.md):

- **Category**: workspace_management, communication_management, automation
- **Execution Pattern**: simple, composite, orchestrator
- **Complexity Tier**: basic, intermediate, advanced
- **Parameter Strategy**: direct_pass, transform, composite, orchestrated

### 3.3 Method Definition Schema

**ManagedMethodDefinition** (`pydantic_ai_integration/method_definition.py`):

- Core schema for method metadata
- Includes classification and parameter profiles
- Supports DTO mapping and data flow patterns
- Classification: method-engineering, definition

**Method Classification Dimensions** (aligned with GRAND_CLASSIFICATION_PLAN.md):

- **Domain**: workspace, communication, automation
- **Capability**: create, read, update, delete, process, search
- **Complexity**: atomic, composite, pipeline
- **Integration Tier**: internal, external, hybrid

---

## Part 4: Domain Services Implementation

### 4.1 CasefileService Domain

**CasefileService** (`casefileservice/service.py`):

- Extends ContextAwareService
- Implements casefile CRUD operations
- Integrates with metrics and audit hooks
- Classification: domain-service, workspace

**CasefileRepository** (`casefileservice/repository.py`):

- Firestore persistence adapter
- Manages casefile documents and subcollections
- Provides query and mutation operations
- Classification: persistence, repository

**CasefileModel** (`casefileservice/models/casefile.py`):

- Canonical domain entity
- Used for persistence and business logic
- Mapped to/from DTOs via mappers
- Classification: domain-model, entity

### 4.2 CommunicationService Domain

**CommunicationService** (`communicationservice/service.py`):

- Handles chat sessions and messaging
- Manages conversation state and history
- Integrates with external communication APIs
- Classification: domain-service, communication

### 4.3 ToolSessionService Domain

**ToolSessionService** (`tool_sessionservice/service.py`):

- Manages tool execution sessions
- Tracks tool chains and conversation history
- Provides session lifecycle management
- Classification: domain-service, automation

---

## Part 5: Persistence & Data Layer

### 5.1 Repository Pattern

**Repository Classes**:

- Extend base repository interfaces
- Provide domain-specific query methods
- Handle Firestore document/subcollection operations
- Classification: persistence, repository

### 5.2 Model Registry System

**ModelRegistry** (`pydantic_ai_integration/model_registry.py`):

- Discovers and validates Pydantic models
- Organizes models by layer and domain
- Provides lookup APIs for DTO mapping
- Classification: model-engineering, registry

**Model Layers** (aligned with GRAND_CLASSIFICATION_PLAN.md):

- **Layer 0**: Base types and primitives
- **Layer 1**: Payload models (requests/responses)
- **Layer 2**: DTOs (data transfer objects)
- **Layer 3**: Canonical domain models
- **Layer 4**: External integration models
- **Layer 5**: View models and projections

---

## Part 6: API & Integration Layer

### 6.1 Pydantic API Layer

**API Routers** (`pydantic_api/routers/`):

- FastAPI router implementations
- Map HTTP requests to service operations
- Handle serialization and validation
- Classification: api-layer, routing

### 6.2 External Integrations

**Integration Adapters** (`pydantic_ai_integration/integrations/`):

- Wrappers for external services (Gmail, Drive, etc.)
- Provide unified interfaces for tool execution
- Handle authentication and rate limiting
- Classification: integration, adapter

---

## Part 7: Configuration & Toolsets

### 7.1 YAML Inventories

**methods_inventory_v1.yaml** (`config/`):

- Source of truth for method definitions
- Contains classification metadata
- Drives tool generation and validation
- Classification: configuration, inventory

**methodtools_v1/*.yaml** (`config/methodtools_v1/`):

- Tool definitions with execution metadata
- Reference methods for parameter inheritance
- Include orchestration and business rules
- Classification: configuration, tool-definition

### 7.2 Tool Schema

**tool_schema_v2.yaml** (`config/`):

- Canonical schema for tool definitions
- Defines validation rules and structure
- Supports simple, composite, and orchestrator patterns
- Classification: configuration, schema

---

## Part 8: System Flow & Interactions

### 8.1 Request Processing Flow

```text
HTTP Request
    ↓
API Router (pydantic_api)
    ↓
RequestHub.dispatch() (coreservice)
    ↓
ServiceManager.get_service() (coreservice)
    ↓
DomainService.execute() (casefileservice, etc.)
    ↓
Repository.operation() (casefileservice, etc.)
    ↓
Response with Context Metadata
```

### 8.2 Tool Execution Flow

```text
Tool Request
    ↓
MANAGED_TOOLS lookup (pydantic_ai_integration)
    ↓
Method Resolution (MANAGED_METHODS)
    ↓
Parameter Mapping & Validation
    ↓
Service Execution with Context
    ↓
Response with Audit Metadata
```

### 8.3 Context Propagation

```text
ServiceContext Creation
    ↓
Injected into all service calls
    ↓
Available in lifecycle hooks
    ↓
Enriches metrics and audit trails
    ↓
Persisted with session state
```

---

## Part 9: Classification & Versioning Integration

### 9.1 Alignment with GRAND_CLASSIFICATION_PLAN.md

**Tool Classification**:

- Categories: workspace_management, communication_management, automation
- Execution Patterns: simple (method_wrapper), composite, orchestrator
- Parameter Strategies: direct_pass, transform, composite, orchestrated

**Method Classification**:

- Domains: workspace, communication, automation
- Capabilities: create, read, update, delete, process, search
- Complexity Levels: atomic, composite, pipeline

**Model Classification**:

- Layers: layer_0_base, layer_1_payloads, layer_2_dtos, layer_3_canonical
- Domains: casefile_domain, tool_session_domain, communication_domain

### 9.2 Versioning Practices

**Semantic Versioning**:

- Tools: version field in ManagedToolDefinition
- Methods: version field in ManagedMethodDefinition
- APIs: version in endpoint paths
- Schemas: version in YAML filenames

**Change Tracking**:

- Registry timestamps for registration tracking
- Audit trails for execution history
- Documentation updates with change logs

---

## Part 10: Current State & Next Steps

### 10.1 System Health Metrics

Based on System State Analysis (October 11, 2025):

- **Tools**: 36 registered (100% categorized, 94% method-referenced)
- **Methods**: 34 registered (100% tool-covered)
- **Models**: 80+ in registry across 5 layers
- **Versioning**: 0% custom versions (all at 1.0.0)
- **Classification**: Well-established domain/capability structure

### 10.2 Identified Gaps

1. **Versioning Maturity**: Implement systematic versioning practices
2. **Composite Tools**: Define execution patterns for non-method tools
3. **Parameter Mapping**: Formalize tool ↔ method parameter relationships
4. **Orchestration**: Standardize orchestration parameters and handlers

### 10.3 Next Development Phases

#### Phase 1: Foundation Enhancement

- Implement extended classification schemas
- Add parameter mapping infrastructure
- Create orchestration handler registry

#### Phase 2: Tool Engineering

- Build meta-tooling for analysis
- Generate parameter mappings
- Validate classification consistency

#### Phase 3: Integration

- Integrate mappings into runtime
- Enhance tool decorators
- Add transformation engine

---

## Change Log

**October 11, 2025**:

- Created unified system documentation from bottom-up approach
- Consolidated existing overview docs (coreservice, pydantic_ai_integration, casefileservice)
- Integrated GRAND_CLASSIFICATION_PLAN.md references
- Added classification and versioning practices
- Included current system state metrics

---

## Navigation

- [[GRAND_CLASSIFICATION_PLAN.md|Grand Classification Plan]]
- [[SYSTEM_STATE_ANALYSIS.md|System State Analysis]]
- [[CORE_SERVICE_OVERVIEW.md|Core Service Overview]]
- [[PYDANTIC_AI_INTEGRATION_OVERVIEW.md|AI Integration Overview]]
- [[CASEFILE_SERVICE_OVERVIEW.md|Casefile Service Overview]]
 
 