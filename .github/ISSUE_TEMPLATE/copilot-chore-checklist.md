---
name: "Copilot chore checklist"
about: "Detailed recurring maintenance chores for the GitHub Copilot agent"
title: "[Copilot] <short-name-for-run>"
labels:
  - chore
  - automation
assignees:
  - github-copilot
---

## Summary
Provide a two-sentence overview of why this chore run is being kicked off (e.g., weekly maintenance, pre-release hardening, post-incident sweep).

## Prep
- [ ] Confirm the repository is on the expected branch (`main`) and up to date with `origin/main`.
- [ ] Review `.github/copilot-instructions.md` for any recent updates that change the operating contract.

## Core chores
- [ ] Run the full automated test suite with `pytest` and capture the results.
- [ ] Start the FastAPI server via `python main.py` to ensure it boots cleanly with `ENVIRONMENT=development` and `USE_MOCKS=true`.
- [ ] Exercise the casefile and tool session APIs (or equivalent service calls) to confirm ID prefixes (`cf_`, `ts_`, `sr_`, `te_`, `cs_`) are still produced as expected.
- [ ] Verify mock persistence still mirrors Firestore shape by inspecting recent mock writes or running targeted repository unit tests if available.
- [ ] Review `requirements.txt` for outdated pins and open a follow-up ticket if any patch/minor upgrades are available.

## Optional stretch tasks
- [ ] Smoke-test Firestore connectivity (set `USE_MOCKS=false`) if credentials are available in the environment.
- [ ] Re-run `tests/test_id_prefixes.py` separately to collect focused diagnostics on ID-generation regressions.

## Observations & follow-ups
Document anything notable that Copilot finds (test failures, startup warnings, dependency updates needed). Link to newly created issues or PRs when applicable.
