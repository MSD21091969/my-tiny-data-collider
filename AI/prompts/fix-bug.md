# Fix Bug

**Variables:** `{{FILE}}` `{{ERROR}}` `{{LINE}}`

**Constraints:**
- Type hints required
- async/await for I/O
- No emojis in code
- Update tests if needed

**Context:**
- Project: my-tiny-data-collider
- Python: 3.13.5
- Pattern: R-A-R (Request-Action-Response)
- See: HANDOVER.md for architecture

**Steps:**
1. Read `{{FILE}}`
2. Locate error at line `{{LINE}}`
3. Fix with minimal changes
4. Run tests: `pytest tests/{{TEST_FILE}} -v`
5. Update HANDOVER.md if architecture affected

**Output:** Fixed code + test results
