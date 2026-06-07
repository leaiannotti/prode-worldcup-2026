# Archive Report: Dashboard Backend APIs

## Change Summary

**Status**: ✅ COMPLETED & VERIFIED

**Scope**: 5 new backend API features for the dashboard frontend.

**Date**: 2026-06-07

---

## What Was Implemented

### 1. match-filtering
- `GET /api/matches` now accepts `status` and `limit` query params
- `status=upcoming` maps to DB `scheduled` status
- `limit` validates positive integers only
- Combines with existing `group` and `date` filters
- Backward compatible when no filters provided

### 2. team-identity
- Added `name` (String 100, NOT NULL) and `flag_url` (String 500, nullable) to `Team` model
- Alembic migration: `a1b2c3d4e5f6_add_team_identity.py`
- Seed populates `name` from JSON and `flag_url` from FIFA→ISO2 mapping
- Match list/detail endpoints include `name` and `flag_url` in team sub-objects

### 3. my-standing
- `GET /api/scores/my-standing` — authenticated cross-group rank summary
- Returns array of `{group_id, group_name, rank, total_points, member_count}`
- Rank computed with tie-breaking by `user_id ASC`

### 4. prediction-distribution
- `GET /api/matches/<id>/distribution` — post-deadline prediction outcome distribution
- Pre-deadline returns `{"available": false, "reason": "pre_deadline"}`
- Deduplicates by `user_id` using GROUP BY (SQLite-compatible)
- Percentages rounded to 1 decimal, sum to 100.0

### 5. activity-feed
- `activity_events` table with UUID PK, user FK, event type, group FK, match FK, payload JSON, occurred_at
- Alembic migration: `b2c3d4e5f6a7_add_activity_events.py` (depends on team-identity migration)
- `GET /api/activity` with cursor pagination (default limit 20, max 50)
- `emit_event()` helper with `try/except` + `flush()` — never blocks parent action
- Instrumented: `group_joined` on join, `prediction_submitted` on prediction submit

---

## Files Changed

| File | Change |
|------|--------|
| `backend/app/models/team.py` | Added `name` and `flag_url` columns |
| `backend/app/models/activity.py` | New `ActivityEvent` model |
| `backend/app/models/__init__.py` | Import `ActivityEvent` |
| `backend/app/blueprints/matches.py` | Added status/limit filters + distribution endpoint |
| `backend/app/blueprints/scores.py` | Added `my_standing()` route |
| `backend/app/blueprints/activity.py` | New activity blueprint |
| `backend/app/blueprints/groups.py` | Instrumented `group_joined` event emission |
| `backend/app/blueprints/predictions.py` | Instrumented `prediction_submitted` event emission |
| `backend/app/services/activity_service.py` | New `emit_event()` helper |
| `backend/app/schemas/score.py` | Added `MyStandingItem` schema |
| `backend/app/seed.py` | FIFA→ISO2 mapping + flag URL generation |
| `backend/app/json_loader.py` | Returns `name` field from JSON |
| `backend/app/__init__.py` | Registered activity blueprint |
| `backend/alembic/versions/a1b2c3d4e5f6_add_team_identity.py` | Migration 1 |
| `backend/alembic/versions/b2c3d4e5f6a7_add_activity_events.py` | Migration 2 |
| `backend/tests/test_matches.py` | 7 match-filtering tests |
| `backend/tests/test_teams.py` | 4 team-identity tests |
| `backend/tests/test_scores.py` | 5 my-standing tests |
| `backend/tests/test_distribution.py` | 5 prediction-distribution tests |
| `backend/tests/test_activity.py` | 9 activity-feed tests |

---

## Verification Results

| Metric | Value |
|--------|-------|
| Tests run | 123 |
| Passed | 123 |
| Failed | 0 |
| Skipped | 0 |

**Critical issues**: None
**Warnings**: 3 pre-existing (utcnow deprecation, Query.get deprecation, JWT key length)
**Suggestions**: 3 (CI migration testing, activity retention policy, additional indexes)

Full report: `openspec/changes/dashboard-backend-apis/verify-report.md`

---

## What Remains

- **Task 6.1**: Run `flask db upgrade` + `flask db downgrade` in CI (Docker Compose environment)
- **Frontend dashboard redesign**: Connect to new APIs (`/api/scores/my-standing`, `/api/matches/<id>/distribution`, `/api/activity`)

---

## Architecture Decisions

1. **SQLite-compatible GROUP BY**: Used instead of `DISTINCT ON` for deduplication because SQLite doesn't support `DISTINCT ON`.
2. **flush() not commit()**: Activity events participate in the parent transaction. If parent rolls back, event rolls back. If event fails, parent action is unaffected.
3. **Pre-deadline distribution returns 200 with `available: false`**: Not a 403 — avoids auth confusion.
4. **Custom spacing tokens removed from Tailwind v4**: They collided with Tailwind v4 defaults (e.g., `max-w-md` became 16px).

---

## Signature

- **Archived by**: Manual (sdd-archive agent failed to produce output)
- **Date**: 2026-06-07
- **Verified**: Yes
- **Next change**: Frontend dashboard redesign
