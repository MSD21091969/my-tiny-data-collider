# Week 2 Quick Start

**One-page guide to get started with Week 2 parallel development**

---

## 🌳 Branch Structure

```
main (production)
 ↓
develop (integration - current)
 ↓
feature/tool-factory-week1 (Week 1 baseline)
 ↓
├── feature/integration-test-templates (Dev A) 3-4 days
├── feature/api-test-templates (Dev B) 3-4 days
├── feature/google-workspace-gmail (Dev C) 5-6 days
├── feature/google-workspace-drive (Dev D) 5-6 days
├── feature/google-workspace-sheets (Dev E) 4-5 days
└── feature/tool-composition (Dev F) 5-7 days
```

---

## 🚀 Quick Start (5 Minutes)

### **1. Clone & Setup**
```powershell
git clone https://github.com/MSD21091969/my-tiny-data-collider.git
cd my-tiny-data-collider
git checkout feature/your-branch-name

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### **2. Verify Setup**
```powershell
python -m pytest tests/generated/test_echo_tool.py -v
# Expected: 9 passed ✅
```

### **3. Sync with Develop**
```powershell
git fetch origin
git merge origin/develop
git push origin feature/your-branch-name
```

### **4. Start Coding!**
```powershell
# Generate a tool
python -m scripts.main config/tools/my_tool.yaml

# Run tests
python -m pytest tests/generated/test_my_tool.py -v

# Commit
git add .
git commit -m "feat: add my_tool"
git push
```

---

## 📋 Your Tasks

| Branch | Developer | Deliverables |
|--------|-----------|--------------|
| `integration-test-templates` | Dev A | Integration test template + 15 tests |
| `api-test-templates` | Dev B | API test template + 12 tests |
| `google-workspace-gmail` | Dev C | 4 Gmail tools + OAuth2 |
| `google-workspace-drive` | Dev D | 5 Drive tools + file handling |
| `google-workspace-sheets` | Dev E | 4 Sheets tools + data transforms |
| `tool-composition` | Dev F | Composition engine + examples |

**See your assigned GitHub issue for detailed tasks!**

---

## ✅ CI/CD Runs Automatically

Every push triggers:
- ✅ Tests on Python 3.12 & 3.13
- ✅ Coverage check (90%+)
- ✅ Linting (ruff, black, isort)
- ✅ YAML validation
- ✅ Security scanning

**Check status:** https://github.com/MSD21091969/my-tiny-data-collider/actions

---

## 📚 Essential Reading

- [README.md](../README.md) - Project overview
- [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) - Daily commands
- [FEATURE_BRANCH_SYNC.md](FEATURE_BRANCH_SYNC.md) - Sync instructions
- [WEEK2_ISSUES.md](WEEK2_ISSUES.md) - Issue templates
- [docs/GITHUB_ACTIONS_GUIDE.md](../docs/GITHUB_ACTIONS_GUIDE.md) - CI/CD guide

---

## 🆘 Common Issues

**Tests failing?**
```powershell
python -m pytest tests/ -v --tb=short
```

**Coverage low?**
```powershell
python -m pytest tests/ --cov=src --cov-report=term-missing
```

**YAML errors?**
```powershell
yamllint config/tools/
python -m scripts.main config/tools/my_tool.yaml
```

---

**Ready? Let's build! 🚀**

For detailed strategy, see: [docs/FEATURE_BRANCH_STRATEGY.md](../docs/FEATURE_BRANCH_STRATEGY.md)
