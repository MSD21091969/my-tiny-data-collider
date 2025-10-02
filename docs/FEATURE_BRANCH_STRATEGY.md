# Feature Branch Strategy - Week 2 Development Plan

**Date:** October 2, 2025  
**Current Status:** Week 1 Complete - Tool Factory MVP  
**Base Branch:** `feature/tool-factory-week1` (ready for merge to `main`)

---

## 🎯 Overview

With the Tool Factory MVP complete and tested, we're ready to parallelize development across multiple feature branches. This document outlines the branch strategy and work distribution for Week 2.

---

## 🌳 Branch Strategy

### **Main Branches**

```
main (production)
    ↓
develop (integration)
    ↓
feature/tool-factory-week1 (✅ COMPLETE - ready to merge)
    ↓
[Week 2 Feature Branches - parallel development]
```

---

## 📋 Week 2 Feature Branches

### **Branch 1: `feature/integration-test-templates`**

**Owner:** Developer A  
**Base:** `feature/tool-factory-week1`  
**Goal:** Generate integration tests for service layer policy enforcement

**Tasks:**
- [ ] Create integration test template (`templates/integration_test_template.py.jinja2`)
- [ ] Extend Tool Factory to generate service-layer tests
- [ ] Test policy enforcement scenarios:
  - Session policies (requires_active_session, allow_new_session)
  - Casefile policies (enforce_access_control, requires_casefile)
  - Business rules (required_permissions, timeout)
- [ ] Generate integration tests for echo_tool
- [ ] Document in `docs/INTEGRATION_TESTING.md`

**Deliverables:**
- Integration test template
- Generated tests for echo_tool (service layer)
- 15+ integration tests passing
- Documentation

**Dependencies:** None (can start immediately)

**Estimated Time:** 3-4 days

---

### **Branch 2: `feature/api-test-templates`**

**Owner:** Developer B  
**Base:** `feature/tool-factory-week1`  
**Goal:** Generate API tests for HTTP layer end-to-end validation

**Tasks:**
- [ ] Create API test template (`templates/api_test_template.py.jinja2`)
- [ ] Extend Tool Factory to generate HTTP-layer tests
- [ ] Test scenarios:
  - JWT authentication
  - RequestEnvelope → JSON response flow
  - HTTP error codes (401, 403, 404, 500)
  - Trace ID propagation
- [ ] Mock FastAPI TestClient setup
- [ ] Generate API tests for echo_tool
- [ ] Document in `docs/API_TESTING.md`

**Deliverables:**
- API test template
- Generated tests for echo_tool (HTTP layer)
- 12+ API tests passing
- Documentation

**Dependencies:** None (can start immediately)

**Estimated Time:** 3-4 days

---

### **Branch 3: `feature/google-workspace-gmail`**

**Owner:** Developer C  
**Base:** `feature/tool-factory-week1`  
**Goal:** Implement Gmail toolset with real API integration

**Tasks:**
- [ ] Create YAML definitions for Gmail tools:
  - `gmail_list_messages.yaml`
  - `gmail_send_message.yaml`
  - `gmail_search_messages.yaml`
  - `gmail_get_message.yaml`
- [ ] Implement API client wrappers (extend `src/pydantic_ai_integration/google_workspace/clients.py`)
- [ ] Add OAuth2 authentication flow
- [ ] Implement `implementation.type: api_call` in templates
- [ ] Generate and test all Gmail tools
- [ ] Add integration with casefile storage
- [ ] Document in `docs/GMAIL_TOOLS.md`

**Deliverables:**
- 4 Gmail tools with YAML configs
- API client implementation
- Unit + integration tests passing
- Documentation

**Dependencies:** None (models already exist)

**Estimated Time:** 5-6 days

---

### **Branch 4: `feature/google-workspace-drive`**

**Owner:** Developer D  
**Base:** `feature/tool-factory-week1`  
**Goal:** Implement Drive toolset with file operations

**Tasks:**
- [ ] Create YAML definitions for Drive tools:
  - `drive_list_files.yaml`
  - `drive_upload_file.yaml`
  - `drive_download_file.yaml`
  - `drive_create_folder.yaml`
  - `drive_share_file.yaml`
- [ ] Implement API client wrappers
- [ ] Add OAuth2 authentication flow
- [ ] Handle file uploads/downloads (base64 encoding)
- [ ] Generate and test all Drive tools
- [ ] Add integration with casefile storage
- [ ] Document in `docs/DRIVE_TOOLS.md`

**Deliverables:**
- 5 Drive tools with YAML configs
- API client implementation
- Unit + integration tests passing
- Documentation

**Dependencies:** None (models already exist)

**Estimated Time:** 5-6 days

---

### **Branch 5: `feature/google-workspace-sheets`**

**Owner:** Developer E  
**Base:** `feature/tool-factory-week1`  
**Goal:** Implement Sheets toolset with data operations

**Tasks:**
- [ ] Create YAML definitions for Sheets tools:
  - `sheets_batch_get.yaml`
  - `sheets_batch_update.yaml`
  - `sheets_append_values.yaml`
  - `sheets_create_spreadsheet.yaml`
- [ ] Implement API client wrappers
- [ ] Add OAuth2 authentication flow
- [ ] Handle data transforms (CSV → Sheets)
- [ ] Generate and test all Sheets tools
- [ ] Add integration with casefile storage
- [ ] Document in `docs/SHEETS_TOOLS.md`

**Deliverables:**
- 4 Sheets tools with YAML configs
- API client implementation
- Unit + integration tests passing
- Documentation

**Dependencies:** None (models already exist)

**Estimated Time:** 4-5 days

---

### **Branch 6: `feature/tool-composition`**

**Owner:** Developer F  
**Base:** `feature/tool-factory-week1`  
**Goal:** Enable tool chaining and composition workflows

**Tasks:**
- [ ] Extend MDSContext with chain management
- [ ] Implement `implementation.type: composite` in templates
- [ ] Create chain execution engine
- [ ] Add conditional execution (on_success, on_failure)
- [ ] Implement chain state management
- [ ] Create example composite tool (e.g., gmail_to_drive pipeline)
- [ ] Document in `docs/TOOL_COMPOSITION.md`

**Deliverables:**
- Composite tool type implementation
- Chain execution engine
- Example composite tool
- Unit + integration tests
- Documentation

**Dependencies:** None (architectural extension)

**Estimated Time:** 5-7 days

---

## 🔄 Workflow Guidelines

### **Starting a New Feature Branch**

```bash
# 1. Checkout base branch
git checkout feature/tool-factory-week1
git pull origin feature/tool-factory-week1

# 2. Create your feature branch
git checkout -b feature/your-feature-name

# 3. Make changes, commit regularly
git add .
git commit -m "feat: description"

# 4. Push to remote
git push origin feature/your-feature-name

# 5. Create Pull Request to feature/tool-factory-week1
```

### **Commit Message Convention**

```
feat: Add integration test templates
fix: Correct policy enforcement in service layer
docs: Update Gmail tools documentation
test: Add API tests for echo_tool
refactor: Improve tool factory template generation
chore: Update dependencies
```

### **Pull Request Requirements**

- [ ] All tests passing (unit + integration + API if applicable)
- [ ] Documentation updated
- [ ] Code follows existing patterns
- [ ] No merge conflicts with base branch
- [ ] Reviewed by at least one team member

---

## 🎯 Integration Strategy

### **Week 2 Timeline**

```
Day 1-2:   Branch creation, initial setup
Day 3-5:   Core implementation
Day 6-7:   Testing and documentation
Day 8:     Code review
Day 9:     Merge to integration branch
Day 10:    Final integration testing
```

### **Integration Branch: `develop`**

Create a `develop` branch to integrate all Week 2 features:

```bash
# Create develop branch from feature/tool-factory-week1
git checkout feature/tool-factory-week1
git checkout -b develop

# Push to remote
git push origin develop
```

**Merge Order:**
1. `feature/integration-test-templates` → `develop`
2. `feature/api-test-templates` → `develop`
3. `feature/google-workspace-gmail` → `develop`
4. `feature/google-workspace-drive` → `develop`
5. `feature/google-workspace-sheets` → `develop`
6. `feature/tool-composition` → `develop`

### **Final Merge to Main**

After all features integrated and tested:

```bash
# Merge develop → main
git checkout main
git merge develop
git push origin main
```

---

## 📊 Success Metrics

### **Per Feature Branch**

- ✅ All tests passing (minimum 90% coverage)
- ✅ Documentation complete
- ✅ Code review approved
- ✅ No breaking changes to base functionality

### **Week 2 Overall**

- ✅ 20+ new tools generated (Gmail, Drive, Sheets)
- ✅ Integration test framework functional
- ✅ API test framework functional
- ✅ Tool composition working
- ✅ All 6 feature branches merged to develop
- ✅ Comprehensive documentation updated

---

## 🛠️ Development Environment Setup

### **For Each Developer**

```bash
# 1. Clone repository
git clone https://github.com/MSD21091969/my-tiny-data-collider.git
cd my-tiny-data-collider

# 2. Checkout your feature branch
git checkout -b feature/your-feature-name feature/tool-factory-week1

# 3. Setup virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify setup
python -m pytest tests/generated/test_echo_tool.py -v
# Expected: 9 passed ✅

# 6. Read documentation
# - README.md
# - QUICK_REFERENCE.md
# - docs/LAYERED_ARCHITECTURE_FLOW.md
```

---

## 📚 Reference Documentation

### **Essential Reading**

1. **[README.md](../README.md)** - Project overview
2. **[QUICK_REFERENCE.md](../QUICK_REFERENCE.md)** - Daily commands
3. **[LAYERED_ARCHITECTURE_FLOW.md](LAYERED_ARCHITECTURE_FLOW.md)** - Architecture patterns
4. **[POLICY_AND_USER_ID_FLOW.md](POLICY_AND_USER_ID_FLOW.md)** - Policy system
5. **[YAML_DRIVEN_MODELS.md](YAML_DRIVEN_MODELS.md)** - Model generation

### **Tool Factory Usage**

```bash
# Generate a tool
python -m scripts.main config/tools/my_tool.yaml

# Run tests
python -m pytest tests/generated/test_my_tool.py -v

# Generate all tools
python -m scripts.main config/tools/*.yaml
```

---

## 🎓 Best Practices

### **Do's**
✅ Follow existing patterns in `echo_tool.yaml`  
✅ Write tests at appropriate layer (unit/integration/API)  
✅ Document new features in `docs/`  
✅ Keep commits small and focused  
✅ Run tests before pushing  
✅ Update CHANGELOG.md with changes  

### **Don'ts**
❌ Don't edit generated files directly (regenerate from YAML)  
❌ Don't skip tests (maintain 90%+ coverage)  
❌ Don't merge without code review  
❌ Don't break existing functionality  
❌ Don't commit sensitive data (.env files)  

---

## 🚀 Getting Started Checklist

### **For Team Lead**
- [ ] Create `develop` branch from `feature/tool-factory-week1`
- [ ] Assign developers to feature branches
- [ ] Set up code review assignments
- [ ] Schedule daily standups
- [ ] Create project board with tasks

### **For Each Developer**
- [ ] Read all essential documentation
- [ ] Setup development environment
- [ ] Verify tests passing (9/9 for echo_tool)
- [ ] Checkout assigned feature branch
- [ ] Review assigned tasks
- [ ] Reach out with questions

---

## 📞 Communication

- **Daily Standup:** 9:00 AM (15 minutes)
- **Code Review:** Async via GitHub PRs
- **Questions:** GitHub Issues or team chat
- **Documentation:** Update as you go

---

## 🎯 Summary

**Week 1 Achievement:** ✅ Tool Factory MVP Complete  
**Week 2 Goal:** Parallelize development across 6 feature branches  
**Expected Outcome:** 20+ production-ready tools, comprehensive testing framework, tool composition support

**Let's build! 🚀**

---

**Created:** October 2, 2025  
**Status:** Ready for Team Distribution  
**Next Action:** Assign developers and create branches
