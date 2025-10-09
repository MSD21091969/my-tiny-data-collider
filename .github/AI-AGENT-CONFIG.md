# AI Agent Autonomous Execution Configuration

**Purpose:** Enable AI code assistants to autonomously execute FASTAPI-REFACTORING-PLAN.md
**Target:** GitHub Copilot, Cursor, Windsurf, Claude, other AI agents
**Branch:** develop
**Status:** Phase 8-10 implementation ready

---

## 🤖 AI Agent Directives

### Primary Task
**Execute:** `AI/recommendations/FASTAPI-REFACTORING-PLAN.md`
**Mode:** Autonomous implementation with validation
**Branch:** develop (checkout and work here)
**Validation:** Run tests after each phase

### Execution Authority
✅ **You are authorized to:**
- Create/modify files in `src/`, `tests/`, `config/`
- Add new middleware files
- Update existing routers and services
- Install Python packages via `requirements.txt`
- Run tests and validation scripts
- Commit changes with descriptive messages
- Create feature branches

❌ **Do NOT:**
- Delete configuration files (`config/*.yaml`)
- Modify `.github/` workflows without review
- Change database schema directly
- Deploy to production
- Modify `pyproject.toml` dependencies without validation

---

## 📋 Execution Plan

### Phase 8: Service Integration (Week 1)
**Goal:** All routes use RequestHub, no direct service calls

**Tasks:**
1. **Extend RequestHub dispatch** (`src/coreservice/request_hub.py`)
   - Add 26 handler methods (see FASTAPI-REFACTORING-PLAN.md §8.2)
   - Import all operation types
   - Map operation names to handlers

2. **Migrate casefile routes** (`src/pydantic_api/routers/casefile.py`)
   - Replace `service.method()` with `hub.dispatch()`
   - Add hooks: `["metrics", "audit"]`
   - Update all 15+ endpoints

3. **Migrate tool session routes** (`src/pydantic_api/routers/tool_session.py`)
   - Replace direct service calls
   - Add session lifecycle hooks
   - Test session state management

**Validation:**
```bash
pytest tests/coreservice/test_request_hub.py -v
pytest tests/integration/test_request_hub_fastapi.py -v
```

### Phase 9: Middleware (Week 2)
**Goal:** Production-grade middleware stack

**Tasks:**
1. **Create middleware directory** (`src/pydantic_api/middleware/`)
   - `auth.py` - JWT validation
   - `logging.py` - Request tracing
   - `rate_limit.py` - 60 req/min per user
   - `error_handler.py` - Standardized errors
   - `metrics.py` - Prometheus metrics

2. **API versioning** (`src/pydantic_api/app.py`)
   - Add `/v1/` prefix to all routes
   - Update OpenAPI config
   - Update router imports

3. **Update app.py**
   - Add all middleware
   - Configure startup/shutdown events
   - Setup exception handlers

**Validation:**
```bash
pytest tests/integration/ -v
curl http://localhost:8000/v1/health
curl http://localhost:8000/v1/docs
```

### Phase 10: Production Readiness (Week 3)
**Goal:** Performance and monitoring

**Tasks:**
1. **Connection pooling** (`src/persistence/firestore_adapter.py`)
   - Implement `FirestoreConnectionPool`
   - Update repositories to use pool
   - Add startup/shutdown events

2. **Caching layer** (`src/coreservice/cache.py`)
   - Implement `CacheService` with Redis
   - Cache session/casefile lookups
   - Add cache invalidation

3. **Monitoring** (`src/pydantic_api/middleware/metrics.py`)
   - Prometheus metrics
   - `/metrics` endpoint
   - Request counters and histograms

**Validation:**
```bash
pytest tests/ -v --cov=src
pytest tests/integration/ -v
# Load test with 100 concurrent requests
```

---

## 🔧 Implementation Guidelines

### Code Style
- **Type hints:** Required on all functions
- **Async/await:** For all I/O operations
- **Docstrings:** Google style (Args, Returns, Raises)
- **Error handling:** Specific exceptions, log with context
- **Naming:** `snake_case` functions, `PascalCase` classes

### Testing Requirements
- **Coverage:** >80% overall, >85% for new code
- **Run after each change:** `pytest tests/ -v`
- **Integration tests:** After each phase
- **Pattern:** Arrange-Act-Assert

### Commit Message Format
```
type(scope): description

- Change 1
- Change 2
- Tests added/updated
```
**Types:** feat, fix, refactor, test, docs, chore

### Branch Strategy
```bash
# Start Phase 8
git checkout develop
git pull origin develop
git checkout -b feature/phase-8-service-integration

# ... implement Phase 8 ...

git add .
git commit -m "feat(request-hub): extend dispatch for all 26 operations"
pytest tests/ -v --cov=src

# If tests pass
git push origin feature/phase-8-service-integration
# Create PR to develop

# Start Phase 9
git checkout develop
git pull origin develop
git checkout -b feature/phase-9-middleware
```

---

## 🚀 Getting Started

### Prerequisites Check
```bash
# Verify Python environment
python --version  # Should be 3.13+

# Verify dependencies
pip install -r requirements.txt

# Verify tests pass
pytest tests/ -v

# Verify tools generated
python scripts/show_tools.py
```

### Start Autonomous Execution
```bash
# 1. Checkout develop branch
git checkout develop
git pull origin develop

# 2. Read the plan
cat AI/recommendations/FASTAPI-REFACTORING-PLAN.md

# 3. Read architecture
cat ARCHITECTURE.md

# 4. Start Phase 8
# Follow FASTAPI-REFACTORING-PLAN.md §8.2
# Implement all 26 RequestHub handlers
```

---

## ✅ Validation After Each Step

### After Modifying RequestHub
```bash
pytest tests/coreservice/test_request_hub.py -v
python scripts/validate_dto_alignment.py
mypy src/coreservice/request_hub.py
```

### After Modifying Routes
```bash
pytest tests/integration/test_request_hub_fastapi.py -v
# Start API server
uvicorn src.pydantic_api.app:app --reload --port 8000
# Test endpoints manually
curl -X POST http://localhost:8000/v1/casefiles/hub \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "description": "Test"}'
```

### After Adding Middleware
```bash
pytest tests/integration/ -v
# Check middleware order
# Check error handling
# Check metrics endpoint
curl http://localhost:8000/metrics
```

### Before Committing
```bash
# Full test suite
pytest tests/ -v --cov=src --cov-report=html

# Type checking
mypy src/

# Linting (optional)
pylint src/ --rcfile=.pylintrc

# Verify no regressions
python scripts/validate_dto_alignment.py
python scripts/show_tools.py
```

---

## 🎯 Success Criteria

### Phase 8 Complete When:
- [ ] All 26 handler methods in RequestHub
- [ ] All casefile routes use `hub.dispatch()`
- [ ] All tool session routes use `hub.dispatch()`
- [ ] Hooks enabled on all operations
- [ ] All tests pass (8/8 minimum)
- [ ] No direct service calls in routers

### Phase 9 Complete When:
- [ ] 5 middleware files created and configured
- [ ] All routes have `/v1/` prefix
- [ ] Authentication validates JWT
- [ ] Rate limiting active (60 req/min)
- [ ] Error responses standardized
- [ ] OpenAPI docs at `/v1/docs`

### Phase 10 Complete When:
- [ ] Connection pooling active
- [ ] Redis caching implemented
- [ ] Metrics exposed at `/metrics`
- [ ] Load test passes (100 req/s)
- [ ] Documentation updated
- [ ] Deployment guide created

---

## 🔍 Troubleshooting

### If Tests Fail
1. Read error message carefully
2. Check if imports are correct
3. Verify DTO alignment: `python scripts/validate_dto_alignment.py`
4. Check service method signatures
5. Review ARCHITECTURE.md for patterns

### If Import Errors
1. Check `config/models_inventory_v1.yaml` for model paths
2. Verify `config/methods_inventory_v1.yaml` for method definitions
3. Regenerate tools: `python scripts/generate_tools.py`
4. Check UTF-8 encoding in generated files

### If RequestHub Dispatch Fails
1. Verify operation name matches handler key
2. Check handler method signature
3. Ensure all imports at top of file
4. Verify service methods exist
5. Check request/response types match

---

## 📊 Progress Tracking

### Report Format
After each phase, provide:
```
Phase X: [Name] - [Status]
---
Completed:
- ✅ Task 1
- ✅ Task 2

In Progress:
- 🔄 Task 3 (50%)

Blocked:
- ❌ Task 4 (reason)

Tests:
- Unit: X/Y passing
- Integration: X/Y passing
- Coverage: X%

Next Steps:
1. Task A
2. Task B
```

---

## 🤝 Collaboration Mode

### When to Ask for Help
- Database schema changes required
- Production deployment decisions
- Security policy changes
- Breaking API changes
- Architecture decisions not covered in plan

### When to Proceed Autonomously
- Implementing handlers per plan
- Adding middleware per examples
- Writing tests
- Updating documentation
- Fixing bugs found during implementation
- Refactoring within established patterns

---

## 📚 Reference Documents

**Primary:** `AI/recommendations/FASTAPI-REFACTORING-PLAN.md`
**Architecture:** `ARCHITECTURE.md`
**Code Patterns:** `.github/copilot-instructions.md`
**Decisions:** `AI/decisions/adr-001-parameter-inheritance.md`
**Navigation:** `DOCS-STRUCTURE.md`

---

**Status:** Ready for autonomous execution
**Branch:** develop
**Last Updated:** October 9, 2025
**Execution Mode:** Full autonomy within defined scope
