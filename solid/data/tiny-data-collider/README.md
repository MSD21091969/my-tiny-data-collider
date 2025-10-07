# Tiny Data Collider - Solid Pod Structure

*Last updated: October 7, 2025*

> Working with the Python stack? Run the clean-slate workflow in the repo root first (clone → create venv → `pip install -e ".[dev]"` → `python scripts/generate_tools.py` → `python scripts/import_generated_tools.py`) so the runtime is ready before wiring this pod.

## 📁 Recommended Organization

```
/tiny-data-collider/
├── README.md                    ← You are here!
├── casefiles/                   ← Your casefile data
│   ├── cf_251001_abc123.ttl
│   └── cf_251001_xyz456.ttl
├── sessions/                    ← Session metadata
│   ├── ts_251001_session1.ttl
│   └── ts_251001_session2.ttl
├── corpuses/                    ← Your curated knowledge
│   ├── legal/
│   │   ├── contracts/
│   │   └── clauses/
│   ├── financial/
│   │   ├── statements/
│   │   └── benchmarks/
│   └── technical/
│       ├── code-examples/
│       └── documentation/
├── metadata/                    ← Knowledge graphs & indexes
│   ├── entities.ttl
│   ├── relationships.ttl
│   └── knowledge-graph.ttl
└── insights/                    ← Generated intelligence
    ├── analyses/
    └── patterns/
```

---

## 🔗 Integration with Python Collider

The FastAPI surface in `src/pydantic_api` and the `ToolSessionService` pipeline now treat this pod as the canonical backing store. During a request:

1. `ToolSessionService.create_session` provisions `/sessions/<session>.ttl`.
2. Tool executions persist casefile mutations under `/casefiles/` via `CasefileService`.
3. Generated corpuses (e.g., Gmail caches) sync into `/corpuses/` or `/metadata/`.
4. Downstream analytics from composite tools land in `/insights/`.

Local development defaults to this repository path (`c:\Users\HP\my-tiny-data-collider\solid-data\tiny-data-collider`). Update the Solid pod URL or credentials in `solid-config/config.json` if you relocate the pod.

## 🔁 Tool Session Sync Cycle

- **Create** a session with `CreateSessionRequest` (see `tests/integration/**/` for examples). The response includes the pod-relative session identifier.
- **Execute** tools via `ToolRequest`; success payloads drive corpus writes (e.g., Gmail messages → `/corpuses/email/`).
- **Persist** audit events automatically—the Firestore stub mirrors pod state so replaying sessions restores casefiles.
- **Inspect** resulting TTL files to debug YAML contract changes or audit trails.

---

## 🔐 Access Control

Each folder should have its own `.acl` file:

- **Private:** `casefiles/`, `sessions/` (only you)
- **Selective:** `corpuses/` (you + trusted peers)
- **Public:** `insights/` (shareable results)

---

## 🚀 Next Steps

1. ✅ Created `/tiny-data-collider/` folder
2. ✅ Created README (this file)
3. ✅ Map directory into `solid-config/config.json`
4. ⏳ Create subfolders (casefiles, sessions, corpuses)
5. ⏳ Generate Solid access token for the collider runtime
6. ⏳ Issue a `CreateSessionRequest` via the API and confirm `/sessions/` updates

---

## 📝 Data Sovereignty Manifesto

This pod is YOUR data:
- No corporate extraction
- No surveillance capitalism  
- Full control, full ownership
- Interoperable with any Solid app
- Self-hosted, self-sovereign

**"Let Corporate have their cookies. I'll have my Tiny Data Collider."**

---

Last updated: October 7, 2025
Pod: http://localhost:3000/maassenhochrath@gmail.com/tiny-data-collider/
