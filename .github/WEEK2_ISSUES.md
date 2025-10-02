# Week 2 Feature Branch Issues

**Purpose:** Track progress on Week 2 parallel development

---

## 📝 Issue Templates for GitHub

### **Issue #1: Integration Test Templates**

**Title:** `[Week 2] Implement Integration Test Templates`

**Labels:** `enhancement`, `week-2`, `testing`, `integration-tests`

**Assignee:** Dev A

**Description:**
```markdown
## 🎯 Goal
Generate integration tests for service layer policy enforcement.

## 📋 Tasks
- [ ] Create `templates/integration_test_template.py.jinja2`
- [ ] Extend Tool Factory to generate service-layer tests
- [ ] Test policy enforcement scenarios:
  - [ ] Session policies (requires_active_session, allow_new_session)
  - [ ] Casefile policies (enforce_access_control, requires_casefile)
  - [ ] Business rules (required_permissions, timeout)
- [ ] Generate integration tests for echo_tool
- [ ] Add 15+ integration test cases
- [ ] Document in `docs/INTEGRATION_TESTING.md`

## 📊 Acceptance Criteria
- [ ] Template generates valid pytest integration tests
- [ ] All echo_tool integration tests pass
- [ ] Coverage ≥ 90% for service layer
- [ ] Documentation complete

## 🔗 Branch
`feature/integration-test-templates`

## ⏱️ Estimate
3-4 days

## 📚 Resources
- [Service Layer Architecture](docs/LAYERED_ARCHITECTURE_FLOW.md)
- [Policy Flow](docs/POLICY_AND_USER_ID_FLOW.md)
- [Quick Reference](QUICK_REFERENCE.md)
```

---

### **Issue #2: API Test Templates**

**Title:** `[Week 2] Implement API Test Templates`

**Labels:** `enhancement`, `week-2`, `testing`, `api-tests`

**Assignee:** Dev B

**Description:**
```markdown
## 🎯 Goal
Generate API tests for HTTP layer end-to-end validation.

## 📋 Tasks
- [ ] Create `templates/api_test_template.py.jinja2`
- [ ] Extend Tool Factory to generate HTTP-layer tests
- [ ] Test scenarios:
  - [ ] JWT authentication
  - [ ] RequestEnvelope → JSON response flow
  - [ ] HTTP error codes (401, 403, 404, 500)
  - [ ] Trace ID propagation
- [ ] Mock FastAPI TestClient setup
- [ ] Generate API tests for echo_tool
- [ ] Add 12+ API test cases
- [ ] Document in `docs/API_TESTING.md`

## 📊 Acceptance Criteria
- [ ] Template generates valid FastAPI tests
- [ ] All echo_tool API tests pass
- [ ] Coverage ≥ 90% for HTTP layer
- [ ] Documentation complete

## 🔗 Branch
`feature/api-test-templates`

## ⏱️ Estimate
3-4 days
```

---

### **Issue #3: Gmail Tools**

**Title:** `[Week 2] Implement Gmail Toolset`

**Labels:** `enhancement`, `week-2`, `google-workspace`, `gmail`

**Assignee:** Dev C

**Tasks:** Create 4 Gmail tools (list, send, search, get) with OAuth2

**Branch:** `feature/google-workspace-gmail`

**Estimate:** 5-6 days

---

### **Issue #4: Drive Tools**

**Title:** `[Week 2] Implement Drive Toolset`

**Labels:** `enhancement`, `week-2`, `google-workspace`, `drive`

**Assignee:** Dev D

**Tasks:** Create 5 Drive tools (list, upload, download, create folder, share) with file handling

**Branch:** `feature/google-workspace-drive`

**Estimate:** 5-6 days

---

### **Issue #5: Sheets Tools**

**Title:** `[Week 2] Implement Sheets Toolset`

**Labels:** `enhancement`, `week-2`, `google-workspace`, `sheets`

**Assignee:** Dev E

**Tasks:** Create 4 Sheets tools (batch get, batch update, append, create) with data transforms

**Branch:** `feature/google-workspace-sheets`

**Estimate:** 4-5 days

---

### **Issue #6: Tool Composition**

**Title:** `[Week 2] Implement Tool Composition Engine`

**Labels:** `enhancement`, `week-2`, `architecture`, `composition`

**Assignee:** Dev F

**Tasks:** Implement tool chaining with conditional execution

**Branch:** `feature/tool-composition`

**Estimate:** 5-7 days

---

## 🚀 Quick Create Script

```powershell
# Create all 6 issues at once
gh issue create --title "[Week 2] Implement Integration Test Templates" `
  --label "enhancement,week-2,testing" `
  --body "See .github/WEEK2_ISSUES.md - Issue #1"

gh issue create --title "[Week 2] Implement API Test Templates" `
  --label "enhancement,week-2,testing" `
  --body "See .github/WEEK2_ISSUES.md - Issue #2"

gh issue create --title "[Week 2] Implement Gmail Toolset" `
  --label "enhancement,week-2,google-workspace" `
  --body "See .github/WEEK2_ISSUES.md - Issue #3"

gh issue create --title "[Week 2] Implement Drive Toolset" `
  --label "enhancement,week-2,google-workspace" `
  --body "See .github/WEEK2_ISSUES.md - Issue #4"

gh issue create --title "[Week 2] Implement Sheets Toolset" `
  --label "enhancement,week-2,google-workspace" `
  --body "See .github/WEEK2_ISSUES.md - Issue #5"

gh issue create --title "[Week 2] Implement Tool Composition Engine" `
  --label "enhancement,week-2,architecture" `
  --body "See .github/WEEK2_ISSUES.md - Issue #6"
```
