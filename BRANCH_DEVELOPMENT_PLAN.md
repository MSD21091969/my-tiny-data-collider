# Branch Development Plan: feature/src-services-integration

**Status:** Milestone 1 Complete (October 11, 2025)

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

### ✅ Milestone 1: Services Architecture Restructure - COMPLETE

**Completed October 11, 2025:**

- ServiceContainer with lazy instantiation and factory registration
- ServiceManager for high-level service grouping and access
- Dependency injection in all service classes (CasefileService, ToolSessionService, CommunicationService)
- RequestHub refactoring to eliminate hardcoded service instantiation
- Test updates to use ServiceManager-based constructor with fake services
- Comprehensive integration testing (9/9 tests passing)

**Benefits Achieved:**

- DRY principles: Eliminated service instantiation violations
- Testability: Services accept mock dependencies
- Maintainability: Centralized service management
- Modern Python: Updated to Python 3.9+ union syntax (`| None`)

### 🎯 Milestone 2: Dependency Injection Framework - READY TO IMPLEMENT

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

### 📋 Milestone 4: Context-Aware Services - PLANNED

**Objectives:**

- Implement ContextAwareService base class
- Add context propagation across service calls
- Create context providers and enrichers
- Establish cross-cutting concerns (logging, metrics, tracing)

### 📋 Milestone 5: Advanced Features & Optimization - PLANNED

**Objectives:**

- Implement service caching and pooling
- Add circuit breaker patterns
- Create service metrics and monitoring
- Establish performance optimization

## Implementation Priority

**Immediate (Milestone 2):**

1. Configuration management system
2. Environment-specific service registration
3. Service health checks
4. Configuration validation

**Short-term (Milestones 3-4):**

1. Service discovery implementation
2. Context-aware service base class
3. Cross-cutting concerns
4. Service instrumentation

**Long-term (Milestone 5):**

1. Performance optimization
2. Advanced monitoring
3. Service resilience patterns
4. Production readiness

## Success Criteria

- **Milestone 1:** ✅ Service instantiation violations eliminated, all tests passing
- **Milestone 2:** Configuration-driven service instantiation working in all environments
- **Milestone 3:** Dynamic service discovery with automatic registration
- **Milestone 4:** All services inherit from ContextAwareService with full context propagation
- **Milestone 5:** Production-ready with comprehensive monitoring and optimization

## Files Created/Modified

**Milestone 1:**

- ✅ `src/coreservice/service_container.py` - New ServiceContainer and ServiceManager
- ✅ `src/casefileservice/service.py` - Updated with CasefileRepository injection
- ✅ `src/tool_sessionservice/service.py` - Updated with ToolSessionRepository and id_service injection
- ✅ `src/communicationservice/service.py` - Updated with ChatSessionRepository, ToolSessionService, and id_service injection
- ✅ `src/coreservice/request_hub.py` - Refactored to use ServiceManager
- ✅ `tests/coreservice/test_request_hub.py` - Updated for ServiceManager constructor

## Dependencies

- None - this branch establishes the foundation for future development

## Risks and Mitigation

**Risk:** Configuration complexity in Milestone 2
**Mitigation:** Start with simple YAML configs, add validation early

**Risk:** Service discovery overhead in Milestone 3
**Mitigation:** Implement lazy discovery with caching

**Risk:** Context propagation performance impact in Milestone 4
**Mitigation:** Use efficient context passing patterns, measure performance

**Risk:** Over-engineering advanced features in Milestone 5
**Mitigation:** Focus on production requirements, implement incrementally
