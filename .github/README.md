# .github Directory Guide

**Welcome to the CI/CD and operational documentation!**

---

## 📍 You Are Here: `.github/`

This directory contains **operational files** for:
- GitHub Actions workflows
- Week 2 development coordination
- Issue/PR templates

---

## 🚀 Quick Start

### **I'm a new developer**
→ Start with: `../README.md` (project overview)  
→ Then read: `../docs/GITHUB_ACTIONS_GUIDE.md` (how CI/CD works)

### **I'm starting Week 2 work**
→ Start with: `WEEK2_QUICK_START.md` (one-page guide)  
→ Then read: `FEATURE_BRANCH_SYNC.md` (sync your branch)  
→ Check: `WEEK2_ISSUES.md` (your assigned issue)

### **I'm maintaining workflows**
→ Read: `../docs/WORKFLOW_BEST_PRACTICES.md` (maintainer guide)  
→ Edit: `workflows/*.yml` (workflow files)

### **I'm a team lead**
→ Read: `../docs/FEATURE_BRANCH_STRATEGY.md` (strategy)  
→ Use: `WEEK2_ISSUES.md` (create team issues)

---

## 📁 Directory Structure

```
.github/
├── README.md (this file) ← Start here!
├── WEEK2_QUICK_START.md - One-page Week 2 guide
├── FEATURE_BRANCH_SYNC.md - How to sync branches with develop
├── WEEK2_ISSUES.md - Issue templates for all 6 feature branches
├── copilot-instructions.md - GitHub Copilot project context
├── pull_request_template.md - PR template
├── ISSUE_TEMPLATE/ - Issue templates
└── workflows/ - GitHub Actions (7 workflows)
    ├── ci.yml - Main test pipeline
    ├── tool-generation.yml - YAML→Python validation
    ├── feature-branch-monitor.yml - Branch tracking
    ├── auto-docs.yml - Documentation generation
    ├── parallel-branch-tests.yml - Multi-branch testing
    ├── dev-session-readiness.yml - Team kickoff checks
    └── reusable-setup.yml - Shared Python setup
```

---

## 📚 Related Documentation

### **For Developers:**
- [`../README.md`](../README.md) - Project overview
- [`../QUICK_REFERENCE.md`](../QUICK_REFERENCE.md) - Daily commands
- [`../docs/GITHUB_ACTIONS_GUIDE.md`](../docs/GITHUB_ACTIONS_GUIDE.md) - CI/CD guide
- [`../docs/LAYERED_ARCHITECTURE_FLOW.md`](../docs/LAYERED_ARCHITECTURE_FLOW.md) - Architecture

### **For Maintainers:**
- [`../docs/WORKFLOW_BEST_PRACTICES.md`](../docs/WORKFLOW_BEST_PRACTICES.md) - Workflow maintenance
- [`../docs/FEATURE_BRANCH_STRATEGY.md`](../docs/FEATURE_BRANCH_STRATEGY.md) - Branching strategy

### **For Team Leads:**
- [`../docs/WEEK2_KICKOFF_RELEASE_NOTES.md`](../docs/WEEK2_KICKOFF_RELEASE_NOTES.md) - Release notes
- [`WEEK2_ISSUES.md`](WEEK2_ISSUES.md) - Issue templates

---

## 🔧 Workflows Quick Reference

| Workflow | Runs When | Purpose |
|----------|-----------|---------|
| `ci.yml` | Every push/PR | Tests, coverage, linting |
| `tool-generation.yml` | YAML changes | Validates tool generation |
| `feature-branch-monitor.yml` | Feature branches | Branch-specific testing |
| `auto-docs.yml` | YAML merged to develop | Auto-generate TOOL_CATALOG.md |
| `parallel-branch-tests.yml` | Every 6 hours | Test all branches |
| `dev-session-readiness.yml` | Manual/daily | Team kickoff checks |
| `reusable-setup.yml` | Called by others | Shared Python setup |

**View runs:** https://github.com/MSD21091969/my-tiny-data-collider/actions

---

## 🎯 Common Tasks

### **Check CI/CD status:**
```powershell
gh run list --limit 5
```

### **Create Week 2 issues:**
See `WEEK2_ISSUES.md` for commands

### **Sync feature branch:**
See `FEATURE_BRANCH_SYNC.md` for instructions

### **Run readiness check:**
```powershell
gh workflow run dev-session-readiness.yml -f check_type=team-kickoff
```

---

## 📞 Need Help?

- **CI/CD questions:** See `../docs/GITHUB_ACTIONS_GUIDE.md`
- **Workflow issues:** See `../docs/WORKFLOW_BEST_PRACTICES.md`
- **Architecture questions:** See `../docs/LAYERED_ARCHITECTURE_FLOW.md`
- **General questions:** See `../README.md`

---

**Last Updated:** October 2, 2025  
**Maintained by:** Tool Engineering Team
