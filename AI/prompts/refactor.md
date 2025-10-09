# Refactor Code

**Variables:** `{{TARGET}}` `{{PATTERN}}` `{{REASON}}`

**Constraints:**
- DRY: Define once, inherit everywhere
- Keep R-A-R pattern intact
- Type hints required
- No breaking changes

**Context:**
- 6-Layer Model: Base → Payloads → DTOs → Methods → Tools → YAML
- Parameter inheritance: DTO → Method → Tool (extract on-demand via Pydantic)
- RequestHub: Central orchestrator with hooks

**Steps:**
1. Read `{{TARGET}}` and dependencies
2. Apply `{{PATTERN}}` (extract method/class/function)
3. Update imports in dependent files
4. Run full test suite: `pytest -v`
5. Update HANDOVER.md with changes

**Validation:**
- All tests pass
- No duplicate code
- Type checking passes

**Output:** Refactored code + test results
