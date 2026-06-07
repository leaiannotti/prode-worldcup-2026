# Proposal: Dashboard Backend APIs

## Intent

The new dashboard requires 5 backend capabilities that don't exist yet. Without them the frontend must make N HTTP calls per group (N+1), has no crowd-sentiment data, no activity history, and shows teams without names or flags. This change delivers the backend primitives the dashboard needs in one coordinated migration cycle.

## Scope

### In Scope
- `GET /api/matches` — add `?status=` and `?limit=` query params
- `teams` model — add `name` and `flag_url` columns + Alembic migration + seed update
- `GET /api/scores/my-standing` — cross-group rank summary for authenticated user
- `GET /api/matches/<id>/distribution` — prediction distribution (post-deadline only, deduplicated)
- `activity_events` table + `GET /api/activity` — real-event feed with cursor pagination

### Out of Scope
- Frontend components consuming these APIs (separate change)
- `prediction_scored` and `challenge_received` activity event types (V2)
- Fixing existing N+1 in leaderboard and history endpoints
- Caching layer (future)

## Capabilities

> Read from `openspec/specs/` — no existing specs dir found; all capabilities are new.

### New Capabilities
- `match-filtering`: Query params `?status=` and `?limit=` on `GET /api/matches`
- `team-identity`: `name` + `flag_url` fields on team model and serialization
- `my-standing`: Cross-group rank summary endpoint for current user
- `prediction-distribution`: Per-match outcome distribution with privacy gate
- `activity-feed`: Real-event table + paginated feed endpoint

### Modified Capabilities
None — no existing spec-level behavior changes.

## Approach

Backend-only change. Five incremental deliverables, each independently testable. Migration ordering is strict: team columns first (Feature 2), then activity table (Feature 5) — each Alembic revision depends on the previous. Features 1, 3, 4 require no migrations and can be parallelized after Feature 2 merges.

Key decisions locked in:
- **`upcoming` → `status == "scheduled"`** (webhook manages state; no clock drift risk)
- **Flag URLs**: `flagcdn.com` + hardcoded FIFA→ISO2 mapping in `seed.py`; `flag_url` nullable so missing mappings don't block seeding
- **Distribution deduplication**: `DISTINCT ON (user_id, match_id)` subquery — 1 user = 1 vote regardless of group count
- **Distribution privacy gate**: return `{"available": false, "reason": "pre_deadline"}` before `match.deadline_utc`; no 403 (avoids auth confusion)
- **Activity**: real `activity_events` table (not derived) — future event types like `challenge_received` have no source table to derive from
- **Activity instrumentation**: `try/except` around event writes — a failed write MUST NOT break the triggering action

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/app/blueprints/matches.py` | Modified | Add `?status`, `?limit` params; add `/distribution` route |
| `backend/app/models/team.py` | Modified | Add `name`, `flag_url` columns |
| `backend/alembic/versions/<new>_team_identity.py` | New | Add `name`, `flag_url` to `teams` |
| `backend/app/seed.py` | Modified | Populate `name` and `flag_url` from JSON + FIFA→ISO2 map |
| `backend/app/json_loader.py` | Modified | Return `name` from team JSON |
| `backend/app/blueprints/scores.py` | Modified | Add `/my-standing` route |
| `backend/app/schemas/score.py` | Modified | Add `MyStandingItem` schema |
| `backend/app/models/activity.py` | New | `ActivityEvent` model |
| `backend/app/blueprints/activity.py` | New | `GET /api/activity` blueprint |
| `backend/alembic/versions/<new>_activity_events.py` | New | `activity_events` table (after team migration) |
| `backend/app/__init__.py` | Modified | Register activity blueprint |
| `backend/app/models/__init__.py` | Modified | Import `ActivityEvent` |
| `backend/app/blueprints/groups.py` | Modified | Emit `group_joined` on join |
| `backend/app/blueprints/predictions.py` | Modified | Emit `prediction_submitted` on submit |
| `backend/tests/` | New | Test files for all 5 features |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| FIFA→ISO2 mapping gaps (48 teams, non-obvious codes) | Med | `flag_url` nullable; seed logs missing codes; flagcdn fallback |
| Activity instrumentation breaks join/predict | Med | `try/except` around writes; tests verify main action succeeds even if event fails |
| Distribution double-count if DISTINCT query is wrong | Low | Unit test with user in 2 groups predicting same match |
| Migration ordering error (activity before team) | Low | Alembic `down_revision` chain enforced; CI runs `flask db upgrade` |
| My-standing rank ties (same points, different order) | Low | Deterministic tie-break: `user_id ASC` as secondary sort |

## Rollback Plan

- **Features 1, 3, 4** (no migration): revert blueprint files; no DB change needed.
- **Feature 2** (team columns): `flask db downgrade` runs `op.drop_column("teams", "name")` + `op.drop_column("teams", "flag_url")`. Team serialization reverts to code-only.
- **Feature 5** (activity table): `flask db downgrade` drops `activity_events`. Instrumentation reverts are independent. No existing data is mutated.
- Order: downgrade Feature 5 first, then Feature 2 (reverse of upgrade order).

## Dependencies

- `flagcdn.com` CDN must be accessible at seed time (no runtime dependency — URL is stored in DB)
- Docker Compose `db` service must be running for migrations

## Success Criteria

- [ ] `GET /api/matches?status=upcoming&limit=5` returns ≤5 scheduled matches
- [ ] Team JSON in any match response includes `name` and `flag_url` (non-null for all 48 teams)
- [ ] `GET /api/scores/my-standing` returns one entry per group with correct rank and points
- [ ] `GET /api/matches/<id>/distribution` returns 403-equivalent before deadline, correct percentages after
- [ ] `GET /api/activity` returns paginated events; joining a group or submitting a prediction produces a new event
- [ ] All new endpoints return 401 when called without auth
- [ ] `pytest` passes with ≥80% coverage on new files
- [ ] `flask db upgrade` and `flask db downgrade` run cleanly in CI
