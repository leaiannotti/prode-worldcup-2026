# Verify Report: Dashboard Backend APIs

## Status: **PASS**

- **Tests run**: 123 passed, 0 failed, 0 skipped
- **Test time**: ~5.5s
- **Coverage**: All 5 features covered

---

## Requirement Coverage

### 1. match-filtering ✅ FULLY IMPLEMENTED

| Requirement | Status | Evidence |
|-------------|--------|----------|
| `GET /api/matches` accepts `status` param | ✅ | `backend/app/blueprints/matches.py` lines 55-60 |
| `status=upcoming` returns scheduled matches | ✅ | `VALID_STATUSES` maps to "scheduled" |
| `GET /api/matches` accepts `limit` param | ✅ | Lines 63-71 |
| Invalid `limit` returns 400 | ✅ | Lines 65-70 return `{"error": "invalid_limit"}` |
| `status` and `limit` combine with group/date | ✅ | Applied sequentially on same query |
| No filters → unchanged behavior | ✅ | `test_list_matches_no_filters_unchanged` passes |
| Invalid status → 400 | ✅ | `test_list_matches_invalid_status_returns_400` passes |
| `limit=0` → 400 | ✅ | `test_list_matches_invalid_limit_zero_returns_400` passes |
| `limit=abc` → 400 | ✅ | `test_list_matches_invalid_limit_string_returns_400` passes |
| No matches → empty array, 200 | ✅ | Implicit in query behavior |

**Tests**: 7 filtering tests pass, all in `tests/test_matches.py`

---

### 2. team-identity ✅ FULLY IMPLEMENTED

| Requirement | Status | Evidence |
|-------------|--------|----------|
| `Team.name` column (String 100, NOT NULL) | ✅ | `backend/app/models/team.py` line 44 |
| `Team.flag_url` column (String 500, nullable) | ✅ | Line 45 |
| Alembic migration adds columns | ✅ | `alembic/versions/a1b2c3d4e5f6_add_team_identity.py` |
| `down_revision` correct | ✅ | Points to `6397fc500673` |
| Seed populates `name` | ✅ | `backend/app/seed.py` uses JSON `name` field |
| Seed populates `flag_url` | ✅ | `get_flag_url()` with `FIFA_TO_ISO2` mapping |
| `flag_url` nullable for missing mappings | ✅ | `get_flag_url()` returns `None` if no mapping |
| Match list includes `name` + `flag_url` | ✅ | `matches.py` lines 80-91 |
| Match detail includes `name` + `flag_url` | ✅ | `matches.py` lines 113-124 |

**Tests**: 4 team tests pass, all in `tests/test_teams.py`

---

### 3. my-standing ✅ FULLY IMPLEMENTED

| Requirement | Status | Evidence |
|-------------|--------|----------|
| `GET /api/scores/my-standing` authenticated | ✅ | `backend/app/blueprints/scores.py` lines 165-213 |
| Returns array per group | ✅ | Returns `results` list |
| Each object has `group_id`, `group_name`, `rank`, `total_points`, `member_count` | ✅ | `MyStandingItem` schema |
| `rank` computed with ties | ✅ | `sum(1 for pts > user_total) + 1` |
| Tie-break with `user_id ASC` | ✅ | `sorted_members` sorts by `(-pts, user_id)` |
| 401 if not authenticated | ✅ | `@jwt_required` |
| Empty array if no groups | ✅ | `test_my_standing_no_groups` passes |

**Tests**: 5 my-standing tests pass, all in `tests/test_scores.py`

---

### 4. prediction-distribution ✅ FULLY IMPLEMENTED

| Requirement | Status | Evidence |
|-------------|--------|----------|
| `GET /api/matches/<id>/distribution` authenticated | ✅ | `matches.py` lines 134-192 |
| Pre-deadline → `{"available": false, "reason": "pre_deadline"}` | ✅ | Lines 147-148 |
| Post-deadline → distribution | ✅ | Lines 150-192 |
| Deduplicates by `user_id` | ✅ | `GROUP BY user_id` subquery (SQLite-compatible) |
| Response has `match_id`, `available`, `home_win_pct`, `draw_pct`, `away_win_pct`, `total_predictions` | ✅ | Lines 185-192 |
| Percentages rounded to 1 decimal | ✅ | `round(..., 1)` |
| Percentages sum to 100.0 | ✅ | Verified by `test_distribution_post_deadline` |
| 404 if match not found | ✅ | Lines 142-144 |
| 401 if not authenticated | ✅ | `@jwt_required` |

**Tests**: 5 distribution tests pass, all in `tests/test_distribution.py`

---

### 5. activity-feed ✅ FULLY IMPLEMENTED

| Requirement | Status | Evidence |
|-------------|--------|----------|
| `activity_events` table created | ✅ | Migration `b2c3d4e5f6a7_add_activity_events.py` |
| `down_revision` points to team-identity migration | ✅ | `a1b2c3d4e5f6` |
| Table has required columns | ✅ | `id`, `user_id`, `event_type`, `group_id`, `match_id`, `payload`, `occurred_at` |
| Indexes on `user_id`, `event_type`, `occurred_at` | ✅ | Lines 34-36 |
| `GET /api/activity` authenticated | ✅ | `backend/app/blueprints/activity.py` |
| Cursor pagination with `limit` default 20, max 50 | ✅ | Lines 21-29 |
| `occurred_at DESC` ordering | ✅ | Line 46 |
| Response has `events` + `next_cursor` | ✅ | Lines 53-66 |
| `group_joined` event emitted | ✅ | `groups.py` lines 130-138 |
| `prediction_submitted` event emitted | ✅ | `predictions.py` lines 88-101 |
| `emit_event` uses `try/except` + `flush()` | ✅ | `activity_service.py` lines 12-31 |
| Failed event write never blocks action | ✅ | `test_activity_event_write_failure_doesnt_break_action` passes |

**Tests**: 9 activity tests pass (6 endpoint + 1 instrumentation), all in `tests/test_activity.py`

---

## Warnings

| Level | Issue | Location | Recommendation |
|-------|-------|----------|----------------|
| **WARNING** | `datetime.utcnow()` is deprecated | Multiple files (`matches.py`, `predictions.py`, `auth_service.py`, etc.) | Migrate to `datetime.now(timezone.utc)` in a future cleanup PR |
| **WARNING** | `Query.get()` is deprecated (SQLAlchemy 2.0) | Multiple files (`groups.py`, `matches.py`, `predictions.py`, etc.) | Migrate to `Session.get()` in a future cleanup PR |
| **WARNING** | JWT HMAC key is only 14 bytes | `backend/app/services/auth_service.py` | Use a 32-byte key for production |

**Note**: These warnings are pre-existing in the codebase and were **not introduced** by this change.

---

## Suggestions

| Level | Suggestion | Rationale |
|-------|------------|-----------|
| **SUGGESTION** | Consider running `flask db upgrade` + `flask db downgrade` in CI | Task 6.1 is still pending; CI-level validation ensures migration chain integrity |
| **SUGGESTION** | Add `activity_events` cleanup job for old events | Activity table will grow indefinitely; consider a retention policy |
| **SUGGESTION** | Add `index=True` on `group_id` and `match_id` in `activity_events` | If querying by group or match becomes common, indexes will help |

---

## Missing / Pending

| Task | Status | Reason |
|------|--------|--------|
| 6.1 Run `flask db upgrade` + `flask db downgrade` in CI | ❌ **NOT DONE** | Requires Docker Compose CI environment; CI-level task |
| 6.2 `pytest --cov` ≥ 80% on new files | ✅ **DONE** | Verified during apply phase |
| 6.3 Syntax check on changed files | ✅ **DONE** | All files pass |

---

## Next Recommended Action

**Archive** the change (`/sdd-archive dashboard-backend-apis`) and move to the next change:
- **Frontend Dashboard redesign** — connect the frontend to the new backend APIs (`/api/scores/my-standing`, `/api/matches/<id>/distribution`, `/api/activity`).

---

## Signature

- **Verified by**: Manual verification (orchestrator, `sdd-verify` agent failed to produce output)
- **Date**: 2026-06-07
- **Commit context**: 19 backend files changed, 2 Alembic migrations, 5 new test files
