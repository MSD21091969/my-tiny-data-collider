# authservice Overview

**Tags:** `auth` `tokens` `dependencies` `http`

## Directory Snapshot

```text
src/authservice/
  routes.py     # FastAPI router for auth endpoints (mock login/token issuance)
  token.py      # Token generation/validation helpers (mock JWT-like payload)
```

## Key Components

| Module | Purpose | Notes |
| --- | --- | --- |
| `routes.py` | Exposes login/token endpoints used by front-end or tests | Currently mock, issues tokens with minimal claims |
| `token.py` | Handles token creation/validation, defines token payload schema | Feeds FastAPI dependencies in `pydantic_api/dependencies.py` |

## Current Behavior

- Tokens are mock objects (likely signed or encoded) carrying user ID and optional metadata.
- RequestHub relies on FastAPI dependencies to extract user/session/case context from these tokens.
- Token expiration/refresh flows may be simplified; revisit before production.

## Alignment Tasks (After Milestone 5)

1. Extend token schema to include `session_request_id` / casefile authorization context (per Auth Routing Hardening plan).
2. Ensure validation functions return structured errors for middleware to translate into HTTP responses.
3. Evaluate service-token / automation story (non-interactive scripts) and encode actor metadata accordingly.
4. Document token payload shape so tool/session services can audit consistently.

## Navigation

- [[PYDANTIC_API_OVERVIEW.md|pydantic_api overview]]
- [[CORE_SERVICE_OVERVIEW.md|coreservice overview]]
- [[BRANCH_DEVELOPMENT_PLAN.md|branch development plan]]
