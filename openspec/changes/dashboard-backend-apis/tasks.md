# Tasks: Dashboard Backend APIs

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 550–700 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (team-identity + match-filtering) → PR 2 (my-standing + prediction-distribution) → PR 3 (activity-feed) |
| Delivery strategy | size:exception (maintainer approved single PR) |
| Chain strategy | single PR |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: size:exception approved by maintainer
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | team-identity migration + model + serialization + match-filtering | PR 1 | Base: main; includes migration + tests |
| 2 | my-standing + prediction-distribution | PR 2 | Base: PR 1 branch or main after merge; no migrations |
| 3 | activity-feed model + migration + blueprint + instrumentation | PR 3 | Base: PR 2 branch or main after merge; migration 2 depends on PR 1 |

---

## Phase 1: team-identity — Migration & Model

- [x] 1.1 Write failing tests for `Team.name` and `Team.flag_url` fields in `backend/tests/test_teams.py` (RED)
- [x] 1.2 Add `name` (String 100, NOT NULL, server_default='') and `flag_url` (String 500, nullable) columns to `backend/app/models/team.py` (GREEN)
- [x] 1.3 Generate Alembic migration `backend/migrations/versions/<timestamp>_add_team_identity.py` with correct `upgrade()` / `downgrade()` ops
- [x] 1.4 Update `backend/app/json_loader.py` to return `name` field from team JSON
- [x] 1.5 Add `FIFA_TO_ISO2` mapping and `get_flag_url()` helper to `backend/app/seed.py`; populate `name` and `flag_url` on upsert
- [x] 1.6 Write failing tests for match list/detail serialization including `name` and `flag_url` in `backend/tests/test_teams.py` (RED)
- [x] 1.7 Update team sub-object in `list_matches()` and `get_match()` in `backend/app/blueprints/matches.py` to include `name` and `flag_url` (GREEN)
- [x] 1.8 Verify `test_team_has_name_and_flag_url`, `test_match_response_includes_team_name`, `test_match_response_includes_flag_url` all pass

## Phase 2: match-filtering

- [x] 2.1 Write failing tests `test_list_matches_upcoming_only`, `test_list_matches_with_limit`, `test_list_matches_upcoming_with_limit`, `test_list_matches_combined_filters`, `test_list_matches_invalid_limit_returns_400`, `test_list_matches_invalid_status_returns_400`, `test_list_matches_no_filters_unchanged` in `backend/tests/test_matches.py` (RED)
- [x] 2.2 Add `VALID_STATUSES` map, `status` filter, and `limit` filter to `list_matches()` in `backend/app/blueprints/matches.py` (GREEN)
- [x] 2.3 Verify all 7+ match-filtering test scenarios pass; confirm backward-compat scenario returns same results as before

## Phase 3: my-standing

- [x] 3.1 Write failing tests `test_my_standing_multiple_groups`, `test_my_standing_no_groups`, `test_my_standing_rank_calculation`, `test_my_standing_rank_ties`, `test_my_standing_unauthenticated_returns_401` in `backend/tests/test_scores.py` (RED)
- [x] 3.2 Add `MyStandingItem` Pydantic model to `backend/app/schemas/score.py` (GREEN)
- [x] 3.3 Add `my_standing()` route to `backend/app/blueprints/scores.py` with membership loop, points aggregation, and tie-breaking rank logic (GREEN)
- [x] 3.4 Verify all 5+ my-standing test scenarios pass including ties and empty-groups case

## Phase 4: prediction-distribution

- [x] 4.1 Write failing tests `test_distribution_post_deadline`, `test_distribution_pre_deadline`, `test_distribution_deduplication`, `test_distribution_no_predictions`, `test_distribution_match_not_found`, `test_distribution_unauthenticated` in `backend/tests/test_distribution.py` (RED)
- [x] 4.2 Add `get_distribution()` route to `backend/app/blueprints/matches.py` with privacy gate, GROUP BY subquery for dedup, and percentage calculation (GREEN)
- [x] 4.3 Verify deduplication test with user-in-3-groups scenario; confirm percentages sum to 100.0

## Phase 5: activity-feed — Model, Migration & Blueprint

- [x] 5.1 Write failing tests `test_activity_group_joined_event`, `test_activity_prediction_submitted_event`, `test_activity_pagination`, `test_activity_event_write_failure_doesnt_break_action`, `test_activity_empty_feed`, `test_activity_unauthenticated` in `backend/tests/test_activity.py` (RED)
- [x] 5.2 Create `backend/app/models/activity.py` with `ActivityEvent` model (UUID PK, user_id FK, event_type, group_id FK nullable, match_id FK nullable, payload JSON, occurred_at indexed) (GREEN)
- [x] 5.3 Add `from .activity import ActivityEvent` import to `backend/app/models/__init__.py`
- [x] 5.4 Generate Alembic migration `backend/alembic/versions/b2c3d4e5f6a7_add_activity_events.py` with `down_revision` pointing to team-identity migration; includes indexes on `user_id`, `event_type`, `occurred_at`
- [x] 5.5 Create `backend/app/services/activity_service.py` with `emit_event()` helper using `flush()` inside `try/except`
- [x] 5.6 Create `backend/app/blueprints/activity.py` with `list_activity()` — cursor pagination, limit cap at 50, `occurred_at DESC` ordering
- [x] 5.7 Register activity blueprint in `backend/app/__init__.py`
- [x] 5.8 Instrument `backend/app/blueprints/groups.py` — call `emit_event(..., "group_joined", ...)` after `db.session.commit()` in `join_group()`
- [x] 5.9 Instrument `backend/app/blueprints/predictions.py` — call `emit_event(..., "prediction_submitted", ...)` after `db.session.commit()` in `submit_prediction()`
- [x] 5.10 Verify all 10 activity-feed tests pass; confirm write-failure test shows emit_event never raises

## Phase 6: Integration & Coverage

- [ ] 6.1 Run `flask db upgrade` + `flask db downgrade` in CI (Docker Compose `db` service) — verify both migration chains apply and roll back cleanly
- [x] 6.2 Run `pytest --cov` in `backend/`; confirm ≥80% coverage on all new files
- [x] 6.3 Syntax check on changed files — all clean
