# Contributing

Concise playbook for collaborating on `my-tiny-data-collider`.

---

## Branch & PR Flow

| Branch | Purpose |
| --- | --- |
| `main` | Production-ready artefacts only |
| `develop` | Integration branch for completed work |
| `feature/*` | Scoped changes branched from `develop` |
| `hotfix/*` | Emergency fixes branched from `main` |

Workflow: branch → commit with clear scope → open PR to `develop` → ensure green checks → merge → promote `develop` → `main` when release-ready.

---

## Coding Standards

- Follow PEP 8, enforce type hints, and keep docstrings on public APIs short and factual.
- Import order: stdlib → third-party → local (`src/...`).
- Pydantic models live in `src/pydantic_models/**` (purpose-based structure); service returns `BaseResponse[...]` instances; no raw dicts across layers.
- YAML under `config/tools/**` is the source of truth. After edits run `python scripts/generate_tools.py` and commit regenerated artefacts when they matter.

---

## Testing & Quality Gates

- Run targeted suites before every PR: unit, integration, and API as needed. The minimal smoke guard is `pytest tests/integration/test_tool_response_wrapping.py -q`.
- Keep generated tests in sync with their YAML spec. Delete/regen when classification moves.
- Linting/formatting: rely on the tooling shipped in `.[dev]`; do not add unrelated style churn.

---

## AI Code Assist Expectations

- Treat assistants as pair programmers: gather context first, plan with explicit TODOs, and execute steps immediately after describing them.
- Prefer precise edits (`apply_patch`) and avoid reformatting outside the change scope.
- Regenerate tools/tests after YAML changes, run a relevant test, and report results (PASS/FAIL) rather than claiming success without evidence.
- Keep responses concise, technical, and free of filler. No fabricated behaviour; surface blockers with proposed next steps.
- When documentation is altered, ensure related handover/README content stays aligned.

---

## PR Checklist

- [ ] Clean branch history and descriptive commit messages (`feat:`, `fix:`, …).
- [ ] Dependencies installed via `pip install -e ".[dev]"` when environment drift is suspected.
- [ ] `python scripts/generate_tools.py` re-run if YAML moved or changed.
- [ ] Relevant tests executed locally with captured output; attach context in PR.
- [ ] Docs and handover notes updated when behaviour/process shifts.

---

Questions? See `README.md` for the high-level system map and `HANDOVER.md` for the current operational checklist.
