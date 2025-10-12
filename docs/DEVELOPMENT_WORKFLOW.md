# Multi-Branch PR Development Workflow

## Overview

This document describes the complete development workflow for managing multiple branches, pull requests, and collaborative development using VS Code integration.

## 🎯 Quick Start

### Initial Setup (One Time)
1. **Install Extensions** (already done):
   - GitHub Pull Requests and Issues
   - Git Graph  
   - GitLens

2. **Configure Git**:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

3. **Install GitHub CLI**:
   ```bash
   winget install GitHub.cli
   gh auth login
   ```

## 🔄 Development Workflow

### 1. Start New Feature
```bash
# VS Code Command Palette (Ctrl+Shift+P)
Tasks: Run Task → "Create Feature Branch"
```
Or manually:
```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### 2. Develop & Test
```bash
# Make your changes, then validate
Tasks: Run Task → "Pre-commit Checks"
```
This runs:
- Registry validation (STRICT mode)
- All tests (52+ registry tests)
- Coverage analysis

### 3. Sync with Latest
```bash
Tasks: Run Task → "Sync with Develop"
```
Pulls latest changes from develop and merges into your branch.

### 4. Create Pull Request
```bash
Tasks: Run Task → "Full PR Workflow"
```
This sequence:
1. Syncs with develop
2. Runs all validation checks
3. Creates PR with template

Or manual:
```bash
Tasks: Run Task → "Create Pull Request"
gh pr create --title "Your Title" --body "Description" --base develop
```

### 5. Monitor PR Status
```bash
Tasks: Run Task → "Check PR Status"
```
Shows:
- CI check status
- Review status
- Merge readiness

## 📋 VS Code Integration Features

### GitHub PR Extension
- **Sidebar**: View all PRs, reviews, checks
- **Inline comments**: Review code directly in editor
- **PR creation**: Create PRs from VS Code
- **Status indicators**: See CI status in file explorer

### Git Graph
- **Visual history**: See branch relationships
- **CI status**: Green/red indicators on commits
- **Interactive**: Click commits to see changes

### GitLens
- **Blame annotations**: See who changed what
- **File history**: Track changes over time
- **Compare**: Side-by-side diffs

## 🚦 Branch Strategy

```
main
├── develop
│   ├── feature/auth-improvements
│   ├── feature/registry-validation
│   └── feature/performance-boost
└── hotfix/critical-bug (if needed)
```

### Branch Types
- **`main`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/*`**: Individual features
- **`hotfix/*`**: Critical production fixes

### Branch Protection Rules
- **main**: Requires 1 approval + CI + linear history
- **develop**: Requires 1 approval + CI
- **feature/***: No restrictions but CI must pass

## 🤖 Automated Features

### PR Creation
- Auto-assigns reviewers
- Auto-labels based on files changed
- Size warnings for large PRs
- Template with checklists

### Review Process
- Auto-merge eligible PRs after approval
- Size checks and warnings
- Required status checks
- Conversation resolution required

### CI Integration
- Registry validation on every PR
- 52+ tests automatically run
- Coverage reports generated
- Drift detection

## 📊 Available Tasks

### Branch Management
- `Create Feature Branch` - Interactive branch creation
- `Switch to Develop` - Quick checkout develop
- `Switch to Main` - Quick checkout main
- `Pull Latest Changes` - Update current branch
- `Sync with Develop` - Merge latest develop

### Development
- `Validate Before PR` - Run registry validation
- `Run All Tests` - Execute full test suite
- `Pre-commit Checks` - Validation + tests
- `Get My Extended Toolset` - Setup development tools

### PR Workflow
- `Create Pull Request` - Interactive PR creation
- `Check PR Status` - View PR and CI status
- `Merge Current PR` - Squash and merge
- `Full PR Workflow` - Complete end-to-end flow

### Conflict Resolution
- `Resolve Merge Conflicts` - Launch merge tool
- Manual resolution with VS Code's 3-way merge

## 🔧 Common Workflows

### Working on Multiple Features

```bash
# Feature 1
git checkout -b feature/auth-system
# ... work on auth ...
git push origin feature/auth-system
gh pr create --base develop

# Feature 2 (while Feature 1 in review)
git checkout develop
git checkout -b feature/logging-system
# ... work on logging ...
git push origin feature/logging-system
gh pr create --base develop

# Switch between features
git checkout feature/auth-system
git checkout feature/logging-system
```

### Keeping Features Updated

```bash
# On feature branch
Tasks: Run Task → "Sync with Develop"

# Or manually
git fetch origin
git merge origin/develop
# Resolve conflicts if any
git push origin HEAD
```

### Review Process

1. **Create PR**: Use template checklist
2. **Auto-assignment**: Reviewers auto-assigned
3. **CI checks**: Must pass before merge
4. **Code review**: Address feedback
5. **Auto-merge**: Enabled after approval

### Hotfix Process

```bash
# Critical bug in production
git checkout main
git checkout -b hotfix/critical-issue
# ... fix the issue ...
git push origin hotfix/critical-issue
gh pr create --base main --title "Hotfix: Critical Issue"

# After merge to main, also merge to develop
git checkout develop
git merge main
git push origin develop
```

## 🎨 VS Code UI Elements

### Source Control Panel
- See branch status
- Stage/unstage changes
- Commit with messages
- Push/pull buttons

### GitHub Tab
- View PRs and issues
- See check status
- Review code inline
- Manage notifications

### Command Palette Commands
- `Git: Checkout` - Switch branches
- `GitHub: Create Pull Request` - PR creation
- `Tasks: Run Task` - Execute custom tasks

## 🔍 Monitoring & Debugging

### Check CI Status
```bash
Tasks: Run Task → "Check PR Status"
# Or visit GitHub Actions tab
```

### Local Validation
```bash
# Run same checks as CI
python scripts/validate_registries.py --strict --verbose
python -m pytest tests/registry/ -v
```

### Debug Failed CI
1. Check Actions tab in GitHub
2. Review logs for specific failures
3. Run validation locally
4. Fix issues and push again

## 📈 Best Practices

### ✅ DO
- Run `Pre-commit Checks` before creating PR
- Keep PRs focused and small (<500 lines)
- Use descriptive commit messages
- Fill out PR template completely
- Sync with develop regularly
- Review code thoroughly

### ❌ DON'T
- Commit directly to main/develop
- Create massive PRs (>1000 lines)
- Skip CI checks
- Ignore review feedback
- Force push to shared branches
- Merge without approval

## 🆘 Troubleshooting

### Merge Conflicts
```bash
Tasks: Run Task → "Resolve Merge Conflicts"
# Or manually
git mergetool
# Fix conflicts, then
git add .
git commit
```

### CI Failures
1. Check specific error in Actions tab
2. Run validation locally
3. Fix issues
4. Push again

### PR Stuck
- Check required status checks
- Ensure approvals received
- Verify branch is up to date
- Contact maintainers if blocked

## 🔗 Quick Links

- **GitHub Actions**: View CI/CD runs
- **Pull Requests**: Manage active PRs  
- **Issues**: Track bugs and features
- **Settings > Branches**: Configure protection rules

This workflow enables efficient multi-branch development with proper CI/CD integration and VS Code tooling!