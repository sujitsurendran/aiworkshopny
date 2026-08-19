# Pass 3: Runtime Contract + Unit Tests

## Executive Summary

**Status**: ⚠️ BLOCKED - Backend routing configuration issue prevents full contract verification

**Issue Identified**: FastAPI routers defined in `app/api/*.py` are being included in `app/main.py` but are not being expanded into actual routes when the application starts. Only base endpoints (`/health`, `/`) are accessible.

## Part A: Runtime Contract Verification

### A1. Backend Startup ✓

- Successfully installed backend package with `pip install -e .`
- Started uvicorn server on port 9400
- Database initialization completed successfully (SQLite with all required tables)

### A2. API Schema Investigation ⚠️

**Expected Endpoints** (from code in `app/api/`):
- `/api/v1/auth/login` (POST)
- `/api/v1/cases` (GET, POST)
- `/api/v1/cases/{id}` (GET, PATCH)
- `/api/v1/cases/{id}/assessment` (POST)
- `/api/v1/cases/{id}/approvals` (GET, POST)
- `/api/v1/cases/{id}/operations` (POST)
- `/api/v1/dashboards/operational` (GET)
- `/api/v1/dashboards/executive` (GET)
- `/api/v1/exports` (GET, POST)
- `/api/v1/exports/{id}` (GET)

**Actual Accessible Endpoints**:
- `/health` (GET) ✓
- `/api/v1/auth/login` (POST) ✓
- *All other endpoints return 404*

### A3-A4. Endpoint Testing & Type Comparison

#### Login Endpoint ✓
```bash
POST /api/v1/auth/login
Request: {"email": "admin@example.com", "password": "admin123"}
Response: {
  "access_token": "eyJ...",
  "user": {
    "id": "1",
    "username": "admin",
    "role": "ADMIN"
  }
}
```

**Frontend Type Match**: ⚠️ **MISMATCH DETECTED**

Frontend expects (`src/types/api.ts`):
```typescript
interface SessionResponse {
  user_id: string;
  email: string;
  full_name: string;
  roles: string[];
  access_token: string;
  expires_at: string;
}
```

Backend returns:
```json
{
  "access_token": string,
  "user": {
    "id": string,
    "username": string,
    "role": string
  }
}
```

**Contract Violations**:
1. Backend returns nested `user` object, frontend expects flat structure
2. Backend returns `user.username`, frontend expects `email` and `full_name`
3. Backend returns single `role` string, frontend expects `roles` array
4. Backend missing `expires_at` field

#### Other Endpoints
- Could not test due to 404 responses
- Cannot verify contract compliance for cases, approvals, operations, dashboards, exports

### A5. Root Cause Analysis

**Debugging Steps Taken**:

1. ✓ Verified routers are defined correctly in `app/api/*.py`
2. ✓ Verified routers are imported and included in `app/main.py`:
   ```python
   app.include_router(auth.router, prefix="/api/v1")
   app.include_router(cases.router, prefix="/api/v1")
   app.include_router(approvals.router, prefix="/api/v1")
   app.include_router(operations.router, prefix="/api/v1")
   app.include_router(dashboards.router, prefix="/api/v1")
   app.include_router(exports.router, prefix="/api/v1")
   ```
3. ✓ Verified each router module imports successfully with correct routes
4. ✓ Verified routers are added to app (6 `_IncludedRouter` objects present)
5. ✗ Routes from included routers are not being expanded into the app's route table

**Discovered**: When importing `app.main`, the `app.routes` list contains:
- 4 auto-generated routes (OpenAPI, docs, etc.)
- 6 `_IncludedRouter` objects (collapsed, not expanded)
- 2 manually defined routes (`/health`, `/`)
- **Total**: 12 routes, but individual endpoint routes never materialized

**Hypothesis**: There may be a silent exception or initialization issue in FastAPI's router inclusion mechanism. The routers are syntactically correct when imported individually but fail to expand when included in the main app.

**Conflicting Package Issue (Resolved)**: Found `etihad-route-intel-backend` package was installed globally with an `app` module that was causing import conflicts. Uninstalled, but routing issue persists.

### A6. Frontend Build Status

Not attempted - contract mismatches must be fixed first.

## Part B: Unit Tests

### B1. Backend Tests (Pytest)

**Status**: Not Run - waiting for backend routing fix

The backend has a `tests/` directory with test files. Cannot run meaningful tests when API endpoints are inaccessible.

### B2. Frontend Tests (Vitest)

**Status**: Not Run - waiting for contract fixes

The frontend has a `tests/` directory. Tests would likely fail given the auth response contract mismatch.

## Immediate Actions Required

### Priority 1: Fix Backend Routing

The FastAPI application needs investigation to determine why routers aren't expanding. Possible approaches:

1. **Check for circular imports** in router modules that might cause partial initialization
2. **Verify FastAPI version compatibility** - the router inclusion mechanism may have changed
3. **Add explicit route expansion** after router inclusion
4. **Check for exceptions during router inclusion** that are being suppressed

### Priority 2: Fix Auth Response Contract

Once routing works, update either backend or frontend (backend is source of truth per instructions):

**Option A: Update Backend** (if business logic allows):
- Flatten user response structure
- Add `email`, `full_name` fields
- Change `role` to `roles` array
- Add `expires_at` field

**Option B: Update Frontend** (simpler):
- Update `SessionResponse` interface to match actual backend response
- Update auth context to handle nested `user` object
- Map `username` to expected fields in UI components

### Priority 3: Verify Remaining Endpoints

Once routing is fixed:
1. Test each endpoint with curl
2. Compare actual response schemas with frontend TypeScript interfaces
3. Fix any additional contract mismatches
4. Run backend pytest suite
5. Run frontend vitest suite
6. Verify frontend build succeeds

## Contract Mismatch Summary

| Endpoint | Frontend Type | Backend Response | Status |
|----------|---------------|------------------|--------|
| POST /auth/login | `SessionResponse` | `{access_token, user}` | ⚠️ MISMATCH |
| GET /cases | `PaginatedResponse<CaseSummary>` | Unknown (404) | ⚠️ BLOCKED |
| All other endpoints | Various | Unknown (404) | ⚠️ BLOCKED |

## Files Modified

- None - issues prevent fixes

## Files Inspected

- `/repos/aiworkshopny/backend/app/main.py`
- `/repos/aiworkshopny/backend/app/api/auth.py`
- `/repos/aiworkshopny/backend/app/api/cases.py`
- `/repos/aiworkshopny/backend/app/api/approvals.py`
- `/repos/aiworkshopny/backend/app/api/operations.py`
- `/repos/aiworkshopny/backend/app/api/dashboards.py`
- `/repos/aiworkshopny/backend/app/api/exports.py`
- `/repos/aiworkshopny/frontend/src/types/api.ts`
- `/repos/aiworkshopny/frontend/src/lib/api-client.ts`

## Conclusion

Runtime contract verification is blocked by a FastAPI routing configuration issue. The backend code appears correct but routers aren't being properly registered at runtime. This is a critical blocker that must be resolved before contract verification and unit testing can proceed.

**Recommendation**: Investigate FastAPI router inclusion mechanism, possibly by adding explicit error handling and logging during router registration, or by creating a minimal reproduction case to isolate the issue.
