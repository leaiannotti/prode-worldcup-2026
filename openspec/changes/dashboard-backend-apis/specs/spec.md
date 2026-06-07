# Spec: Dashboard Backend APIs

## 1. match-filtering

### Requirements
- `GET /api/matches` MUST accept an optional `status` query param.
- When `status=upcoming`, the endpoint MUST return only matches with DB status `scheduled`, ordered by `kickoff_utc ASC`.
- `GET /api/matches` MUST accept an optional `limit` query param (positive integer).
- Invalid `limit` values (non-integer, zero, negative) MUST return 400.
- `status` and `limit` MUST combine with existing `group` and `date` filters.
- When no `status` or `limit` is provided, behavior MUST remain unchanged.

### Scenarios

**Scenario: Fetch upcoming matches with limit**
- Given 10 scheduled matches and 5 finished matches exist
- When `GET /api/matches?status=upcoming&limit=4`
- Then response contains exactly 4 matches, all with `status: "scheduled"`, ordered by `kickoff_utc ASC`

**Scenario: Combine status with group filter**
- Given scheduled matches in groups A and B
- When `GET /api/matches?status=upcoming&group=A`
- Then response contains only scheduled matches from group A

**Scenario: Invalid limit**
- When `GET /api/matches?limit=-1`
- Then response is 400 with `{"error": "invalid_limit"}`

**Scenario: No filters (backward compat)**
- When `GET /api/matches`
- Then all matches returned as before (no behavior change)

### Edge Cases
- `limit=0` → 400
- `limit=abc` → 400
- `status=finished` → returns matches with `status == "finished"`
- `status=unknown_value` → 400
- No matches match filters → empty array, 200

### Test Scenarios
- `test_list_matches_upcoming_only`
- `test_list_matches_with_limit`
- `test_list_matches_upcoming_with_limit`
- `test_list_matches_combined_filters`
- `test_list_matches_invalid_limit_returns_400`
- `test_list_matches_invalid_status_returns_400`
- `test_list_matches_no_filters_unchanged`

---

## 2. team-identity

### Requirements
- `Team` model MUST have a `name` column (String 100, NOT NULL).
- `Team` model MUST have a `flag_url` column (String 500, nullable).
- A new Alembic migration MUST add both columns.
- Seed MUST populate `name` from the existing `worldcup.teams.json` (which already has this field).
- Seed MUST populate `flag_url` using `https://flagcdn.com/w80/{iso2}.png` with a hardcoded FIFA→ISO2 mapping.
- `flag_url` MUST be nullable so missing ISO2 mappings don't block seeding.
- Match list and detail endpoints MUST include `name` and `flag_url` in team sub-objects.

### Scenarios

**Scenario: Match response includes team identity**
- Given teams ARG (Argentina) and BRA (Brazil) exist with name and flag_url
- When `GET /api/matches`
- Then each match's `home_team` and `away_team` include `id`, `code`, `name`, `flag_url`

**Scenario: Migration adds columns**
- Given a DB at the initial migration
- When `flask db upgrade` runs
- Then `teams` table has `name` and `flag_url` columns

**Scenario: Seed populates all 48 teams**
- When seed runs
- Then all 48 teams have non-null `name`
- And at least 44 teams have non-null `flag_url` (allowing for edge cases like ENG→gb-eng)

### Edge Cases
- Team with no ISO2 mapping → `flag_url` is null, seed logs a warning
- Migration downgrade → columns are dropped cleanly

### Test Scenarios
- `test_team_has_name_and_flag_url`
- `test_match_response_includes_team_name`
- `test_match_response_includes_flag_url`
- `test_migration_upgrade_downgrade`

---

## 3. my-standing

### Requirements
- `GET /api/scores/my-standing` MUST be a new authenticated endpoint.
- MUST return an array of objects, one per group the user belongs to.
- Each object MUST contain: `group_id`, `group_name`, `rank`, `total_points`, `member_count`.
- `rank` MUST be computed by ordering members by total points DESC with ties receiving the same rank.
- Tie-breaking for rank ordering MUST use `user_id ASC` as secondary sort.
- MUST return 401 if not authenticated.
- MUST return empty array if user belongs to no groups.

### Scenarios

**Scenario: User in 2 groups**
- Given user belongs to "Office Heroes" (rank 3, 150pts, 10 members) and "Family League" (rank 1, 200pts, 5 members)
- When `GET /api/scores/my-standing`
- Then response is `[{group_id, group_name: "Family League", rank: 1, total_points: 200, member_count: 5}, {group_id, group_name: "Office Heroes", rank: 3, total_points: 150, member_count: 10}]`

**Scenario: User in no groups**
- Given user belongs to no groups
- When `GET /api/scores/my-standing`
- Then response is `[]`

**Scenario: Tied points**
- Given user A and user B both have 100pts in a group
- When `GET /api/scores/my-standing` as user A
- Then both have rank 1 (or whichever tie logic produces)

### Edge Cases
- User's only group has 1 member (themselves) → rank 1, member_count 1
- User has predictions scored 0 in all groups → total_points 0, valid rank
- Group with no predictions yet → all members have 0 points

### Test Scenarios
- `test_my_standing_multiple_groups`
- `test_my_standing_no_groups`
- `test_my_standing_rank_calculation`
- `test_my_standing_rank_ties`
- `test_my_standing_unauthenticated_returns_401`

---

## 4. prediction-distribution

### Requirements
- `GET /api/matches/<id>/distribution` MUST be a new authenticated endpoint.
- If `now < match.deadline_utc`, MUST return `{"available": false, "reason": "pre_deadline"}` with status 200.
- If `now >= match.deadline_utc`, MUST return distribution with `available: true`.
- Distribution MUST deduplicate by `(user_id, match_id)` — a user in 3 groups counts as 1 vote.
- Response MUST include: `match_id`, `available`, `home_win_pct`, `draw_pct`, `away_win_pct`, `total_predictions`.
- Percentages MUST be floats rounded to 1 decimal place.
- Percentages MUST sum to 100.0 (within floating point tolerance).
- MUST return 404 if match does not exist.
- MUST return 401 if not authenticated.

### Scenarios

**Scenario: Post-deadline distribution**
- Given match 1 has deadline in the past
- And 10 unique users predicted: 5 home wins, 2 draws, 3 away wins
- When `GET /api/matches/1/distribution`
- Then response is `{available: true, match_id: 1, home_win_pct: 50.0, draw_pct: 20.0, away_win_pct: 30.0, total_predictions: 10}`

**Scenario: Pre-deadline**
- Given match 2 has deadline in the future
- When `GET /api/matches/2/distribution`
- Then response is `{available: false, reason: "pre_deadline"}`

**Scenario: User in multiple groups**
- Given user A predicted match 1 in 3 different groups (same prediction)
- When distribution is calculated
- Then user A counts as 1 prediction, not 3

**Scenario: No predictions**
- Given match 3 has passed deadline but zero predictions
- When `GET /api/matches/3/distribution`
- Then response is `{available: true, match_id: 3, home_win_pct: 0, draw_pct: 0, away_win_pct: 0, total_predictions: 0}`

### Edge Cases
- Match does not exist → 404
- All predictions are draws → `draw_pct: 100.0`
- 1 prediction → percentages are 100/0/0 or similar

### Test Scenarios
- `test_distribution_post_deadline`
- `test_distribution_pre_deadline`
- `test_distribution_deduplication`
- `test_distribution_no_predictions`
- `test_distribution_match_not_found`
- `test_distribution_unauthenticated`

---

## 5. activity-feed

### Requirements
- A new `activity_events` table MUST be created with: `id` (UUID PK), `user_id` (FK), `event_type` (String 50), `group_id` (FK nullable), `match_id` (FK nullable), `payload` (JSON nullable), `occurred_at` (DateTime, indexed).
- Alembic migration MUST be ordered AFTER the team-identity migration.
- `GET /api/activity` MUST be a new authenticated endpoint returning the current user's events.
- MUST support cursor-based pagination: `?cursor=<ISO datetime>&limit=N` (default limit 20, max 50).
- Events MUST be ordered by `occurred_at DESC`.
- Response MUST include `events` array and `next_cursor` (null if no more).
- Event types for V1: `group_joined`, `prediction_submitted`.
- `prediction_scored` is out of scope for V1 (deferred).
- Joining a group MUST emit a `group_joined` event.
- Submitting a prediction MUST emit a `prediction_submitted` event.
- Event writes MUST be wrapped in `try/except` — a failed write MUST NOT break the triggering action.
- MUST return 401 if not authenticated.

### Scenarios

**Scenario: User joins group and event appears**
- Given user joins group "Office Heroes"
- When `GET /api/activity`
- Then response includes event `{event_type: "group_joined", group_id: ..., payload: {group_name: "Office Heroes"}}`

**Scenario: Cursor pagination**
- Given user has 25 events
- When `GET /api/activity?limit=10`
- Then response has 10 events and a non-null `next_cursor`
- When `GET /api/activity?cursor=<next_cursor>&limit=10`
- Then response has 10 events and a non-null `next_cursor`
- When `GET /api/activity?cursor=<next_cursor>&limit=10`
- Then response has 5 events and `next_cursor` is null

**Scenario: Event write failure doesn't break join**
- Given the activity_events table is somehow broken
- When user joins a group
- Then the join succeeds (user is a member)
- And no activity event is created (but no error is returned to user)

### Edge Cases
- User with no events → empty array, `next_cursor` null
- `limit` > 50 → capped to 50
- `limit` <= 0 → 400
- Invalid `cursor` format → 400

### Test Scenarios
- `test_activity_group_joined_event`
- `test_activity_prediction_submitted_event`
- `test_activity_pagination`
- `test_activity_event_write_failure_doesnt_break_action`
- `test_activity_empty_feed`
- `test_activity_unauthenticated`
