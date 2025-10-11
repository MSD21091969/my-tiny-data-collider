# Branch Development Plan: feature/src-services-integration

**Status:** Milestone 5 Complete (October 11, 2025)

## Overview

The `feature/src-services-integration` branch implements comprehensive DRY/DI (Don't Repeat Yourself / Dependency Injection) refactoring to establish a solid foundation for maintainable, testable service architecture.

## Background

The codebase had hardcoded service instantiation violations throughout, making testing difficult and maintainability poor. Milestone 1 established the core dependency injection framework with ServiceContainer and ServiceManager patterns.

## Key Files

- `src/coreservice/service_container.py`: ServiceContainer and ServiceManager implementation
- `src/casefileservice/service.py`: CasefileService with dependency injection
- `src/tool_sessionservice/service.py`: ToolSessionService with dependency injection
- `src/communicationservice/service.py`: CommunicationService with dependency injection
- `src/coreservice/request_hub.py`: RequestHub refactored to use ServiceManager
- `tests/coreservice/test_request_hub.py`: Updated tests for new architecture

## Milestone Status

### ✅ Milestone 1: Services Architecture Restructure - COMPLETE (Enhanced)

**Completed October 11, 2025:**

- ServiceContainer with lazy instantiation and factory registration
- ServiceManager for high-level service grouping and access
- Dependency injection in all service classes (CasefileService, ToolSessionService, CommunicationService)
- RequestHub refactoring to eliminate hardcoded service instantiation
- Test updates to use ServiceManager-based constructor with fake services
- **NEW: Model Transformation Layer** - BaseMapper class for bidirectional transformations
- **NEW: Transformation Analysis Tools** - Scripts for analyzing and generating mappers
- **NEW: 8 Core Operation Mappers** - Auto-generated mappers for casefile, session, and chat operations
- Comprehensive integration testing (9/9 tests passing)

**Benefits Achieved:**

- DRY principles: Eliminated service instantiation violations
- Testability: Services accept mock dependencies
- Maintainability: Centralized service management
- **NEW: Model Transformation Patterns** - Explicit DTO ↔ Domain mapping
- **NEW: Development Tools** - Analysis, generation, and visualization scripts
- Modern Python: Updated to Python 3.9+ union syntax (`| None`)

### ✅ Milestone 2: Dependency Injection Framework - COMPLETE

**Completed October 11, 2025:**

- **Configuration Management System**: Centralized MDSConfig with environment-specific settings
- **Environment-Aware Service Registration**: ServiceContainer enhanced with conditional service enabling
- **Service Health Check Infrastructure**: Async health validation with dependency checking
- **Configuration Validation and Schema Enforcement**: Custom validators for all components
- **RESTful Health API Endpoints**: `/health`, `/health/services`, `/health/infrastructure`, `/ready`, `/live`
- **Production-Ready Configuration**: Environment-specific validation and schema enforcement

**Key Components Implemented:**

- `src/coreservice/config.py`: MDSConfig class with nested configuration models and validation
- `src/coreservice/health_checker.py`: SystemHealthChecker and ServiceHealthChecker classes
- `src/pydantic_api/routers/health.py`: FastAPI health check endpoints
- `src/coreservice/service_container.py`: Enhanced with environment-aware service registration
- `.env`: Development environment configuration file

**Benefits Achieved:**

- **Configuration-Driven Architecture**: Services enabled/disabled based on environment
- **Production Readiness**: Comprehensive validation prevents misconfigurations
- **Monitoring & Observability**: Health checks for all services and infrastructure
- **Environment Flexibility**: Different configurations for development, staging, production
- **Schema Validation**: Prevents configuration errors with detailed validation messages

### 🎯 Milestone 3: Service Discovery & Registry - READY TO IMPLEMENT

**Objectives:**

- Create centralized configuration management
- Implement environment-specific service registration
- Add service health checks and monitoring
- Establish configuration-driven service instantiation

**Key Components:**

- Configuration loader for environment-specific settings
- Service health check endpoints (`/health/services`)
- Environment-aware service registration
- Configuration validation and schema

### 📋 Milestone 3: Service Discovery & Registry - PLANNED

**Objectives:**

- Implement dynamic service discovery
- Create service registry with metadata
- Add service versioning and compatibility
- Establish service dependency resolution

### ✅ Milestone 4: Context-Aware Services - COMPLETE

**Completed October 11, 2025:**

- **ContextAwareService Base Class**: Abstract base class with context management and lifecycle hooks
- **ServiceContext Model**: Pydantic model with request tracing, user/session info, correlation IDs, and metadata
- **Context Propagation System**: Context variables and provider pattern for cross-service context sharing
- **Context Providers**: UserContextProvider, SessionContextProvider, and RequestContextProvider implementations
- **Lifecycle Hooks**: Pre/post/error execution hooks for cross-cutting concerns (logging, metrics, tracing)
- **CasefileService Integration**: CasefileService inherits from ContextAwareService with context-aware execution
- **Abstract Metrics Framework**: Abstract `_record_metrics` method for service-specific metrics collection

**Key Components Implemented:**

- `src/coreservice/context_aware_service.py`: **NEW** ContextAwareService base class, ServiceContext model, context providers, and propagation utilities
- `src/casefileservice/service.py`: Enhanced with ContextAwareService inheritance and context-aware execution pattern

**Benefits Achieved:**

- **Request Tracing**: Unique request IDs and correlation IDs for distributed tracing
- **Context Propagation**: Automatic context enrichment and propagation across service calls
- **Observability**: Comprehensive logging and metrics collection for all service operations
- **Error Tracking**: Context preservation during error handling and reporting
- **Service Architecture**: Foundation for building observable, context-aware microservices

### ✅ Milestone 5: Advanced Features & Optimization - COMPLETE

**Completed October 11, 2025:**

- **Service Caching & Pooling**: Multi-strategy cache (LRU/LFU/TTL/size-based eviction), connection pooling with health checking, ServiceCache manager, and CachedServiceMixin for easy integration
- **Circuit Breaker Patterns**: Configurable circuit breaker with failure thresholds, recovery timeouts, half-open state testing, and CircuitBreakerRegistry for centralized management
- **Advanced Service Metrics & Monitoring**: Comprehensive metrics collection (counters/gauges/histograms/timers), service-specific metrics, system health monitoring (CPU/memory/uptime), and MetricsDashboard for visualization
- **Performance Optimization & Benchmarking**: PerformanceProfiler with async/sync benchmarking, percentile calculations, OptimizedServiceMixin for service performance enhancement, and utility functions for profiling
- **Test Coverage**: 23 comprehensive tests covering all functionality with proper test isolation using custom collectors
- **Modern Python**: Updated to Python 3.9+ union syntax (`dict/list/X | None`) and proper async/await patterns

**Key Components Implemented:**

- `src/coreservice/service_caching.py`: Cache[T], ConnectionPool[T], CircuitBreaker, ServiceCache, CachedServiceMixin, CircuitBreakerRegistry
- `src/coreservice/service_metrics.py`: MetricsCollector, ServiceMetrics, PerformanceProfiler, MetricsDashboard, OptimizedServiceMixin
- `tests/test_service_metrics.py`: Comprehensive test suite with 23 tests covering all functionality
- `tests/coreservice/test_service_caching.py`: Service caching and circuit breaker tests

**Benefits Achieved:**

- **Scalability**: Intelligent caching and connection pooling reduce database/external service load
- **Reliability**: Circuit breakers prevent cascade failures and enable graceful degradation
- **Observability**: Real-time metrics collection for performance analysis and alerting
- **Performance**: Automated benchmarking and optimization tracking with detailed reporting
- **Production Ready**: All components tested and ready for integration into MDS microservices

<!-- markdownlint-disable-next-line MD033 -->
<h2 style="color:red;">Implementation Priority</h2>

**Completed (Milestones 1-5):**

1. ✅ Services Architecture Restructure - DRY/DI patterns established
2. ✅ Dependency Injection Framework - Configuration-driven service instantiation
3. ✅ Service Discovery & Registry - Environment-aware service registration and health checks
4. ✅ Context-Aware Services - Context propagation and observability framework
5. ✅ Advanced Features & Optimization - Production-ready caching, resilience, and monitoring

## After Milestone 5 Assessment

- **MVP Delivery Specs & UX**: Validate auth/session flows, define minimal toolset, capture release criteria, and document required user journeys.
- **Toolchain Validation**: Confirm token carries routing data, ensure request/session rehydration everywhere, inventory YAML toolset coverage and load tests.
- **Auth Routing Hardening**: Extend token schema to include `session_request_id`, enforce token/session alignment for tool execution, and define service-token flow for scripted operations.
- **RequestHub Context Flow**: Ensure all R-A-R operations rely on RequestHub for context hydration; document the service transformation pattern (prepare context → execute service → enrich response) so new modules follow the same lifecycle.
- **Registry Consolidation**: Evaluate unifying method/tool YAML loaders, registries, and decorators into a cohesive lifecycle module (shared error handling, validation, and drift detection) so the inventory cycle remains explicit and self-tested.
- **MVP Boundaries**: Freeze the minimum deployable toolset plus configs, outline future experimentation guardrails so PR branches stay non-blocking.
- **Branch Strategy Prep**: Use `feature/develop` for analysis and issue triage, branch per experiment (tool mapping, executor engine, observability, YAML automation).
- **Unified Classification & Mapping**: Design a searchable, versioned taxonomy for methods/tools/models so tool engineering can express data pipelines (fields, types, transformations, R-A-R context) with end-to-end documentation.
- **MDSContext Alignment**: Schedule a branch to audit `pydantic_ai_integration/dependencies.py` so token/session routing, persistence hooks, and tool event tracking stay consistent with the hardened auth + RequestHub flow.
- **Persistence Formalization**: Evaluate restructuring Firestore/Redis abstractions into a cohesive persistence layer (consistent pooling, caching, metrics) to reduce layering drift and keep dataflow explicit.
- **RAR Envelope Alignment**: Map business logic entry points to the appropriate R-A-R request/response models and envelopes, ensuring every service/route consumes the canonical DTOs without ad-hoc payloads.
- **Communication Service Boundaries**: Document and enforce the current chat-only scope, plan future integrations (Pub/Sub, logging, tracing) as opt-in extensions, and evaluate the pending execution-engine branch before expanding responsibilities.
- **YAML Tool Engineering Readiness**: Treat `config/tool_schema_v2.yaml`, `config/methods_inventory_v1.yaml`, and `config/models_inventory_v1.yaml` as the authoritative trio; add validator coverage for parameter inheritance, composite orchestration, and version alignment before wider rollout.

### Q&A Wrap (October 11, 2025)

- Captured the latest tool engineering review: schema v2 is R-A-R aligned but needs validators and integration tests to confirm ToolDec parameter inheritance and composite execution.
- Reaffirmed YAML as the generation canvas while reserving targeted Python scripts for complex conditional flows until composite/multi-tool orchestration is verified.
- Recorded that the first five generated definitions under `config/methodtools_v1/` passed smoke tests; expanding coverage depends on the validator suite.
- Logged creation of subsystem overview documentation (`docs/CORE_SERVICE_OVERVIEW.md`, `docs/CASEFILE_SERVICE_OVERVIEW.md`, `docs/TOOL_SESSION_SERVICE_OVERVIEW.md`, `docs/PYDANTIC_AI_INTEGRATION_OVERVIEW.md`, `docs/PYDANTIC_MODELS_OVERVIEW.md`, `docs/PERSISTENCE_OVERVIEW.md`, `docs/AUTHSERVICE_OVERVIEW.md`, `docs/COMMUNICATION_SERVICE_OVERVIEW.md`) as reference assets for follow-on branches.
- Q&A cycle for Milestone 5 follow-up is complete; action items now live in the after-milestone backlog above.

### YAML Tooling Status

- `config/tool_schema_v2.yaml` captures the R-A-R separation cleanly, yet orchestration sections (`implementation.*`, composite steps, parameter overrides) lack automated validation; ToolDec parameter inheritance still needs an integration test pass.
- `config/methods_inventory_v1.yaml` stays synchronized with MANAGED_METHODS (34 entries) and provides classification metadata, but the reference-only `business_rules` blocks can drift because enforcement lives outside the registry.
- `config/models_inventory_v1.yaml` is auto-regenerated and aligns with the payload/DTO layering, supplying a reliable parameter source, though no guardrails confirm tool/method definitions actually match those payload signatures.
- Generated definitions under `config/methodtools_v1/` honour the new schema; only the first five have completed smoke testing, so composite/multi-tool and conditional branches remain unproven.
- YAML continues to cover declarative pipelines effectively, but for sophisticated branching (“soph cond logic”) a hybrid approach—YAML corridor plus targeted Python templates—remains safer until composite support is exercised.

#### Immediate Checks

- Add a schema-aware validator that loads each tool YAML, resolves `method_name`, and compares required parameters against the actual Pydantic request models.
- Build a fixture-based test that runs ToolDec over the inventory to confirm inherited parameters land in generated tool stubs (start with the verified five, then fan out).
- Prototype a composite tool in code first, then mirror it in YAML to prove the schema can express conditional/multi-step flows; fall back to scripted orchestration if it cannot.
- Wire version metadata (`schema_version`, inventory version) into the generator so drift between YAML and code is caught during CI.

### Infrastructure Specs & Boundaries (October 11, 2025)

- Core FastAPI server must remain session-capable; keep an always-on cloud instance (Cloud Run or equivalent) sized for steady tool execution.
- Evaluate lightweight worker options (Cloud Run Jobs, Cloud Functions, queue-driven workers) for burst execution; keep the worker count minimal until load data arrives.
- Redis stays the coordination/cache layer; plan for managed Redis if we move fully to cloud to avoid ops overhead.
- Firestore continues as the metadata source of truth for casefiles; note a future extension path for RAG assets (GCS buckets for artifacts, BigQuery for analytical views).
- Keep scalability stubs in place (async repos, pooling) without over-engineering; document hooks for when RAG/analytics land.
- Logging/monitoring preference: explore Pyd Logfire as an alternative to Cloud Logging explorers for cost-effective observability.
- Cost posture: bias toward serverless/autoscaled services with predictable baselines; capture cost estimates in follow-up branch before committing to infra spend.

### Initial Branch Strategy

- Keep branch tree shallow: sequenced feature branches off `feature/develop`, each scoped to a single validation or infrastructure task.
- First branch: `feature/yaml-validator` implementing schema-aware validation plus the ToolDec fixture tests noted in Immediate Checks; target small, reviewable commits.
- Second branch (once validator merged): `feature/inventory-drift-guard` wiring version metadata into generators and CI sanity checks.
- Parallel only when necessary; otherwise serialize work to avoid context drift and maintain quick review cycles.
- Capture any infra experiments (Cloud Run sizing, managed Redis evaluation, logging options) in short-lived `spike/*` branches with README notes, then fold decisions back into the plan.

## CI/CD + Toolchain Mindmap (Initial Narrative)

1. `main` holds stable FastAPI app, vetted tool/method/model inventories.
2. CI/CD runs toolset tests (optionally with workers) using engineering YAMLs before promoting to user/agent-facing inventories.
3. Toolsets can be exercised locally or through scripts without auth, plus audited HTTP sessions with Firestore persistence.
4. Sessions persist under casefile → session → session_request hierarchy; tokens carry endpoint hint, expire and renew with fresh audit entries.
5. Feature branches explore advanced YAML templates, mapper generation, observability, and engine upgrades in isolated workspaces.

## Success Criteria (recap)

## Success Criteria

- **Milestone 1:** ✅ Service instantiation violations eliminated, all tests passing
- **Milestone 2:** ✅ Configuration-driven service instantiation working in all environments
- **Milestone 3:** ✅ Environment-aware service registration and health checks implemented
- **Milestone 4:** ✅ All services inherit from ContextAwareService with full context propagation
- **Milestone 5:** ✅ Production-ready with comprehensive caching, resilience, monitoring, and optimization

## Files Created/Modified

**Milestone 1:**

- ✅ `src/coreservice/service_container.py` - New ServiceContainer and ServiceManager
- ✅ `src/casefileservice/service.py` - Updated with CasefileRepository injection
- ✅ `src/tool_sessionservice/service.py` - Updated with ToolSessionRepository and id_service injection
- ✅ `src/communicationservice/service.py` - Updated with ChatSessionRepository, ToolSessionService, and id_service injection
- ✅ `src/coreservice/request_hub.py` - Refactored to use ServiceManager
- ✅ `tests/coreservice/test_request_hub.py` - Updated for ServiceManager constructor
- ✅ `src/pydantic_models/base/transformations.py` - **NEW** BaseMapper class and transformation utilities
- ✅ `scripts/analyze_model_transformations.py` - **NEW** Model transformation analysis script
- ✅ `scripts/generate_mapper.py` - **NEW** Automatic mapper code generator
- ✅ `scripts/visualize_rar_flow.py` - **NEW** RAR flow visualization script
- ✅ `src/pydantic_models/mappers/` - **NEW** Directory with 8 auto-generated mappers

**Milestone 2:**

- ✅ `src/coreservice/config.py` - **NEW** MDSConfig with environment-specific settings and validation
- ✅ `src/coreservice/health_checker.py` - **NEW** SystemHealthChecker and ServiceHealthChecker classes
- ✅ `src/pydantic_api/routers/health.py` - **NEW** FastAPI health check endpoints
- ✅ `src/coreservice/service_container.py` - Enhanced with environment-aware service registration
- ✅ `.env` - **NEW** Development environment configuration file

**Milestone 5:**

- ✅ `src/coreservice/service_caching.py` - **NEW** Multi-strategy cache, connection pooling, circuit breaker, and service cache management
- ✅ `src/coreservice/service_metrics.py` - **NEW** Advanced metrics collection, performance profiling, and service optimization
- ✅ `tests/test_service_metrics.py` - **NEW** Comprehensive test suite with 23 tests for all metrics functionality
- ✅ `tests/coreservice/test_service_caching.py` - Service caching and circuit breaker tests

**Cross-Branch Documentation & YAML Engineering:**

- ✅ `docs/CORE_SERVICE_OVERVIEW.md`, `docs/CASEFILE_SERVICE_OVERVIEW.md`, `docs/TOOL_SESSION_SERVICE_OVERVIEW.md`, `docs/PYDANTIC_AI_INTEGRATION_OVERVIEW.md`, `docs/PYDANTIC_MODELS_OVERVIEW.md`, `docs/PERSISTENCE_OVERVIEW.md`, `docs/AUTHSERVICE_OVERVIEW.md`, `docs/COMMUNICATION_SERVICE_OVERVIEW.md` - Reference overviews supporting alignment work on future branches
- ✅ `config/tool_schema_v2.yaml`, `config/methods_inventory_v1.yaml`, `config/models_inventory_v1.yaml`, `config/methodtools_v1/` - Updated schema, inventories, and generated tool definitions for the YAML-based tool engineering pipeline

## Dependencies

- None - this branch establishes the foundation for future development

## Risks and Mitigation

**Risk:** Service discovery overhead in Milestone 3
**Mitigation:** ✅ Implemented lazy discovery with caching

**Risk:** Context propagation performance impact in Milestone 4
**Mitigation:** ✅ Used efficient context passing patterns, measured performance

**Risk:** Over-engineering advanced features in Milestone 5
**Mitigation:** ✅ Focused on production requirements, implemented incrementally with comprehensive testing
