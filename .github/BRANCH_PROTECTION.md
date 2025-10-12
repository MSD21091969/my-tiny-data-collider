# Branch Protection Configuration

This file documents the recommended branch protection rules for this repository.
These should be configured in GitHub Settings > Branches.

## Main Branch Protection Rules

### `main` branch:
- [x] Require a pull request before merging
  - [x] Require approvals: 1
  - [x] Dismiss stale PR approvals when new commits are pushed
  - [x] Require review from code owners
- [x] Require status checks to pass before merging
  - [x] Require branches to be up to date before merging
  - Required status checks:
    - `Registry Validation / Validate Method & Tool Registries`
    - `Registry Validation / Run Registry Tests`
- [x] Require conversation resolution before merging
- [x] Require signed commits
- [x] Require linear history
- [x] Include administrators

### `develop` branch:
- [x] Require a pull request before merging
  - [x] Require approvals: 1
  - [ ] Dismiss stale PR approvals (more flexible for dev)
  - [ ] Require review from code owners (optional for dev)
- [x] Require status checks to pass before merging
  - [x] Require branches to be up to date before merging
  - Required status checks:
    - `Registry Validation / Validate Method & Tool Registries`
    - `Registry Validation / Run Registry Tests`
- [x] Require conversation resolution before merging
- [ ] Require signed commits (optional for dev)
- [ ] Require linear history (allow merge commits in dev)
- [ ] Include administrators (allow admin bypass in dev)

## Setup Instructions

1. Go to GitHub repository Settings
2. Navigate to Branches section
3. Click "Add rule" for each branch
4. Configure settings as documented above
5. Save each rule

## Auto-merge Configuration

Enable auto-merge for PRs that meet criteria:
- All status checks pass
- Required reviews approved
- No conflicting reviews
- Branch is up to date

## Merge Strategies

- **main**: Squash and merge (clean history)
- **develop**: Create merge commit (preserve feature branch context)
- **feature/***: Any strategy allowed

## Status Checks Required

All branches require these status checks:
- Registry validation (STRICT mode)
- Registry tests (all 52+ tests)
- Code coverage maintained
- No validation errors or drift

## Review Requirements

- **main**: 1+ approving review from maintainers
- **develop**: 1+ approving review (any collaborator)
- **feature/***: No requirements (but CI must pass)

## Bypass Permissions

- Repository administrators can bypass all rules
- Use sparingly and only for hotfixes
- Document any bypasses in commit messages