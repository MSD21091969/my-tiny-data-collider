# Firestore Indexes Audit Report

**Generated:** October 1, 2025  
**Scope:** All Python files in `src/`  
**Tool:** Manual code inspection  
**Status:** ✅ Complete

---

## Executive Summary

- **Total Firestore Queries Found:** 8 unique queries
- **Compound Queries (Requiring Indexes):** 1 query
- **Single-Field Queries:** 7 queries
- **Documented Indexes:** 0  
- **Status:** 🟡 Low risk - Only 1 compound query found

### Quick Stats

| Metric | Count | Status |
|--------|-------|--------|
| Collections Used | 4 | - |
| Compound Queries | 1 | ⚠️ Needs index |
| Single Field Queries | 7 | ✅ Auto-indexed |
| Subcollections | 2 | - |
| Index Documentation | 0 | ❌ Missing |

---

## What Are Firestore Indexes?

### Background

Firestore automatically creates indexes for:
- Single-field queries (`where("field", "==", value)`)
- Document ID lookups (`.document(id).get()`)

Firestore **requires composite indexes** for:
- Queries with multiple `where()` clauses
- Queries combining `where()` and `order_by()`
- Queries with inequality operators on multiple fields

### Why This Matters

- ❌ **Without Index:** Query fails with error `FAILED_PRECONDITION`
- ✅ **With Index:** Query executes efficiently
- 📊 **Performance:** Indexes improve query speed significantly

---

## Firestore Collections Structure

```
/
├── tool_sessions_index/           # Index collection for sessions
│   └── {session_id}/             # Flat session metadata
├── sessions/                      # Full session data
│   └── {session_id}/
│       ├── requests/              # Subcollection: requests
│       │   └── {request_id}/
│       │       └── events/        # Subcollection: events
│       │           └── {event_id}/
└── casefiles/                     # Casefile documents
    └── {casefile_id}/
```

**Collections:** 4 top-level  
**Subcollections:** 2 (requests, events)  
**Documents:** Variable (user data)

---

## Query Analysis

### 1. ⚠️ Compound Query (NEEDS INDEX)

#### Query Location
- **File:** `src/tool_sessionservice/repository.py`
- **Method:** `list_sessions()`
- **Lines:** 186-188

#### Query Details
```python
query = self.session_index_collection
if user_id:
    query = query.where("user_id", "==", user_id)
if casefile_id:
    query = query.where("casefile_id", "==", casefile_id)
```

#### Analysis
- **Collection:** `tool_sessions_index`
- **Fields Queried:** `user_id`, `casefile_id`
- **Query Type:** Compound equality (2 fields)
- **Index Required:** ✅ YES (when both parameters provided)
- **Scenarios:**
  - `user_id` only: ✅ Auto-indexed
  - `casefile_id` only: ✅ Auto-indexed
  - Both parameters: ⚠️ Requires composite index

#### Impact
- **Severity:** 🟡 MEDIUM
- **Frequency:** Likely infrequent (filtering by user + casefile)
- **Workaround:** Query fails if both filters used simultaneously
- **Error Message:** `FAILED_PRECONDITION: The query requires an index`

#### Recommended Index
```json
{
  "collectionGroup": "tool_sessions_index",
  "queryScope": "COLLECTION",
  "fields": [
    {"fieldPath": "user_id", "order": "ASCENDING"},
    {"fieldPath": "casefile_id", "order": "ASCENDING"}
  ]
}
```

---

### 2. ✅ Single-Field Query (Auto-Indexed)

#### Query Location
- **File:** `src/casefileservice/repository.py`
- **Method:** `list_casefiles()`
- **Line:** 120

#### Query Details
```python
query = self.casefiles_collection
if user_id:
    query = query.where("metadata.created_by", "==", user_id)
```

#### Analysis
- **Collection:** `casefiles`
- **Field Queried:** `metadata.created_by`
- **Query Type:** Single-field equality
- **Index Required:** ❌ NO (auto-indexed by Firestore)
- **Status:** ✅ Works automatically

---

### 3. ✅ Order-By Query (Auto-Indexed)

#### Query Location
- **File:** `src/tool_sessionservice/repository.py`
- **Method:** `get_request_events()`
- **Line:** 175

#### Query Details
```python
events_collection = (self.db.collection("sessions")
                      .document(session_id)
                      .collection("requests")
                      .document(request_id)
                      .collection("events"))
for event_doc in events_collection.order_by("timestamp").stream():
```

#### Analysis
- **Collection:** `events` (subcollection)
- **Field Ordered:** `timestamp`
- **Query Type:** Single-field order
- **Index Required:** ❌ NO (auto-indexed by Firestore)
- **Status:** ✅ Works automatically

---

### 4-8. ✅ Direct Document Lookups (No Index Needed)

#### Locations
1. `src/tool_sessionservice/repository.py:68` - Get session by ID
2. `src/tool_sessionservice/repository.py:84` - Get session by ID
3. `src/tool_sessionservice/repository.py:120` - Get request by ID
4. `src/tool_sessionservice/repository.py:132` - Get request by ID
5. `src/casefileservice/repository.py:85` - Get casefile by ID

#### Pattern
```python
doc = self.db.collection("collection_name").document(doc_id).get()
```

#### Analysis
- **Query Type:** Document ID lookup
- **Index Required:** ❌ NO (document IDs are inherently indexed)
- **Status:** ✅ Works automatically

---

## Index Documentation Status

### Current State
- ❌ No `firestore.indexes.json` file exists
- ❌ No index documentation in `docs/`
- ❌ No index documentation in code comments
- ⚠️ Production deployments may fail on compound queries

### Recommended Index File

Create `firestore.indexes.json` in project root:

```json
{
  "indexes": [
    {
      "collectionGroup": "tool_sessions_index",
      "queryScope": "COLLECTION",
      "fields": [
        {
          "fieldPath": "user_id",
          "order": "ASCENDING"
        },
        {
          "fieldPath": "casefile_id",
          "order": "ASCENDING"
        }
      ]
    }
  ],
  "fieldOverrides": []
}
```

---

## Deployment Instructions

### Option 1: Deploy via Firebase CLI

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Deploy indexes
firebase deploy --only firestore:indexes --project YOUR_PROJECT_ID
```

### Option 2: Deploy via gcloud CLI

```bash
# Create index
gcloud firestore indexes composite create \
  --collection-group=tool_sessions_index \
  --query-scope=COLLECTION \
  --field-config field-path=user_id,order=ascending \
  --field-config field-path=casefile_id,order=ascending \
  --project=YOUR_PROJECT_ID
```

### Option 3: Create via Console

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Navigate to **Firestore Database** > **Indexes**
4. Click **Create Index**
5. Configure:
   - Collection ID: `tool_sessions_index`
   - Fields:
     - `user_id` (Ascending)
     - `casefile_id` (Ascending)
   - Query scope: Collection
6. Click **Create**

### Option 4: Automatic Creation (Development Only)

Run the failing query in development:
```python
# This will fail with a helpful error containing a link
await repository.list_sessions(user_id="user123", casefile_id="cf_251001_ABC")
```

The error message contains a URL to automatically create the index:
```
FAILED_PRECONDITION: The query requires an index. You can create it here:
https://console.firebase.google.com/...?create_composite_index=...
```

⚠️ **Not recommended for production** - indexes should be pre-created.

---

## Testing Compound Queries

### Test Script

Create `scripts/test_compound_query.py`:

```python
"""Test compound Firestore query to verify index exists."""

import asyncio
from src.tool_sessionservice.repository import ToolSessionRepository

async def test_compound_query():
    """Test filtering sessions by user_id AND casefile_id."""
    repo = ToolSessionRepository()
    
    try:
        # This requires a composite index
        sessions = await repo.list_sessions(
            user_id="test_user_123",
            casefile_id="cf_251001_ABC"
        )
        print(f"✅ Query succeeded! Found {len(sessions)} sessions")
        print("Index is configured correctly.")
        
    except Exception as e:
        if "FAILED_PRECONDITION" in str(e):
            print("❌ Query failed: Missing composite index")
            print("Create index using firestore.indexes.json")
        else:
            print(f"❌ Query failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_compound_query())
```

### Expected Outcomes

**Without Index:**
```
❌ Query failed: Missing composite index
Create index using firestore.indexes.json
```

**With Index:**
```
✅ Query succeeded! Found 0 sessions
Index is configured correctly.
```

---

## Recommendations

### 1. Create Index File 🔴 HIGH PRIORITY

**Action:** Create `firestore.indexes.json` in project root

**Why:** 
- Prevents production failures
- Documents required indexes
- Enables automated deployment
- Version-controlled infrastructure

**Effort:** 5 minutes

---

### 2. Deploy Index to Firestore 🔴 HIGH PRIORITY

**Action:** Run `firebase deploy --only firestore:indexes`

**Why:**
- Enables compound query functionality
- Prevents runtime errors
- Required before using `list_sessions()` with both filters

**Effort:** 5 minutes + index build time (~5-30 minutes depending on data size)

---

### 3. Add Index Status to Documentation 🟡 MEDIUM PRIORITY

**Action:** Create `docs/FIRESTORE_SETUP.md` documenting:
- Required indexes
- How to deploy indexes
- How to verify indexes exist
- Common index-related errors

**Effort:** 30 minutes

---

### 4. Add Defensive Coding 🟡 MEDIUM PRIORITY

**Action:** Update `list_sessions()` to catch index errors:

```python
async def list_sessions(
    self, 
    user_id: Optional[str] = None, 
    casefile_id: Optional[str] = None
) -> List[ToolSession]:
    """List sessions with optional filtering."""
    
    # Warn if compound query without index
    if user_id and casefile_id:
        logger.warning(
            "Compound query on user_id + casefile_id requires "
            "composite index. See docs/FIRESTORE_SETUP.md"
        )
    
    try:
        sessions: List[ToolSession] = []
        
        query = self.session_index_collection
        if user_id:
            query = query.where("user_id", "==", user_id)
        if casefile_id:
            query = query.where("casefile_id", "==", casefile_id)
            
        for index_snapshot in query.stream():
            session = await self.get_session(index_snapshot.id)
            if session:
                sessions.append(session)
                
        return sessions
        
    except Exception as e:
        if "FAILED_PRECONDITION" in str(e):
            raise ValueError(
                "Missing Firestore index. Run: "
                "firebase deploy --only firestore:indexes"
            ) from e
        raise
```

**Effort:** 15 minutes

---

### 5. Monitor Index Usage 🟢 LOW PRIORITY

**Action:** Add logging for compound queries:

```python
if user_id and casefile_id:
    logger.info(
        "Executing compound query",
        extra={
            "user_id": user_id,
            "casefile_id": casefile_id,
            "query_type": "compound"
        }
    )
```

**Why:** Track how often compound queries are used

**Effort:** 5 minutes

---

## Future Considerations

### Potential New Indexes Needed

As the application evolves, these queries may require indexes:

1. **Filter sessions by status and date**
   ```python
   query.where("status", "==", "active").order_by("created_at")
   ```
   - Collection: `tool_sessions_index`
   - Fields: `status` (asc), `created_at` (asc/desc)

2. **Filter casefiles by tags and created date**
   ```python
   query.where("tags", "array-contains", "urgent").order_by("created_at")
   ```
   - Collection: `casefiles`
   - Fields: `tags` (array), `created_at` (asc/desc)

3. **Complex tool event queries**
   ```python
   query.where("tool_name", "==", "gmail_search").order_by("timestamp")
   ```
   - Collection group: `events`
   - Fields: `tool_name` (asc), `timestamp` (asc/desc)

### Index Best Practices

1. **Create indexes before deploying code** that uses them
2. **Test compound queries** in development first
3. **Monitor index usage** via Firebase Console
4. **Clean up unused indexes** to reduce storage costs
5. **Document all indexes** in `firestore.indexes.json`

---

## Summary

**Current State:** 🟡 Good
- Only 1 compound query found
- Query is low-frequency (list sessions filtered by user + casefile)
- All other queries use auto-indexes

**Critical Action:** Create composite index for `tool_sessions_index` collection

**Risk Level:** LOW
- Application mostly works without index
- Only fails when calling `list_sessions(user_id=X, casefile_id=Y)` with both params
- Easy to fix (5 minutes to create index file + deploy)

**Recommended Next Steps:**
1. ✅ Create `firestore.indexes.json` (this report includes template)
2. ✅ Deploy index to Firestore
3. ✅ Test compound query
4. ✅ Document in `docs/FIRESTORE_SETUP.md`
5. ✅ Add defensive error handling

---

## Appendix: Complete firestore.indexes.json

Save this as `firestore.indexes.json` in project root:

```json
{
  "indexes": [
    {
      "collectionGroup": "tool_sessions_index",
      "queryScope": "COLLECTION",
      "fields": [
        {
          "fieldPath": "user_id",
          "order": "ASCENDING"
        },
        {
          "fieldPath": "casefile_id",
          "order": "ASCENDING"
        }
      ]
    }
  ],
  "fieldOverrides": []
}
```

**Deployment Command:**
```bash
firebase deploy --only firestore:indexes --project YOUR_PROJECT_ID
```

**Verification:**
```bash
# List all indexes
firebase firestore:indexes

# Or via gcloud
gcloud firestore indexes composite list --project=YOUR_PROJECT_ID
```

---

**Generated:** October 1, 2025  
**Next Review:** After adding new compound queries  
**Related Documents:**
- `src/tool_sessionservice/repository.py` - Contains compound query
- `src/casefileservice/repository.py` - Contains single-field queries
- Firebase Console > Firestore > Indexes
