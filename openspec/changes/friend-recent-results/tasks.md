# Tasks: friend-recent-results

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~370 |
| 400-line budget risk | Medium |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (backend) → PR 2 (frontend) |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Backend endpoint + TDD tests | PR 1 | Tests first; route `GET /api/scores/groups/:groupId/members/:userId/recent-history`; limit default 5, max 10 |
| 2 | Frontend sheet + integration | PR 2 | BottomSheet.vue, FriendRecentResultsSheet.vue, Leaderboard wiring, i18n |

## Phase 1: Backend TDD (RED)

- [x] 1.1 Write failing tests in `backend/tests/test_leaderboard.py` for `GET /api/scores/groups/:groupId/members/:userId/recent-history` — scenarios: happy path (default limit 5), custom limit, max cap 10, 403 requester not in group, 404 target not in group, only finished matches, missing prediction rows (null prediction, 0 points, null score_type) — ~90 lines
- [x] 1.2 Add `MemberRecentHistoryEntry` and `MemberRecentHistoryResponse` schemas to `backend/app/schemas/score.py` — ~20 lines

## Phase 2: Backend Implementation (GREEN)

- [x] 2.1 Implement `get_member_recent_history` in `backend/app/blueprints/scores.py` — verify JWT, check `_is_group_member(current_user_id, group_id)`, validate `limit` (default 5, cap at 10), query last N finished matches (`status='finished'` ordered by `kickoff_utc DESC`), left-join predictions and scores for target user, return JSON with `match`, `actual_result`, `prediction`, `points`, `score_type` — ~50 lines
- [x] 2.2 Run backend tests until all pass; adjust implementation if needed

## Phase 3: Frontend Foundation

- [x] 3.1 Create `frontend/src/components/BottomSheet.vue` — reusable wrapper extracted from `PredictionModal.vue` pattern (Teleport, Transition, backdrop click to close, `rounded-t-2xl`, `bg-surface`, `z-50`) — ~30 lines
- [x] 3.2 Add `friendRecentResults` i18n keys to `frontend/src/i18n/es.json` and `frontend/src/i18n/en.json` — title, noPredictions, exact, outcome, noPoints, match, prediction, noPrediction — ~30 lines
- [x] 3.3 Create `frontend/src/components/FriendRecentResultsSheet.vue` — consume `BottomSheet`, accept `isOpen`, `userName`, `history[]`, `loading`, `error`; render skeleton pulse loader (reuse `PointsDrawer.vue` pattern) when loading; render up to 5 rows showing match teams, prediction or `—`, points badge with color coding (3 green, 1 yellow, 0 red) — ~90 lines

## Phase 4: Frontend Integration

- [x] 4.1 Add `getMemberRecentHistory(groupId, userId, limit = 5)` to `frontend/src/lib/api.ts` — ~5 lines
- [x] 4.2 Add `memberRecentHistory` state and `fetchMemberRecentHistory` action to `frontend/src/stores/leaderboard.ts` — set loading, call API, store history, handle 403 error — ~25 lines
- [x] 4.3 Add `@click` on avatar wrapper in `frontend/src/components/LeaderboardTable.vue` and emit `select-user` with the entry object — ~10 lines
- [x] 4.4 Add `selectedUser`, `isRecentResultsOpen` state, `handleSelectUser` event handler, and `FriendRecentResultsSheet` render in `frontend/src/views/LeaderboardView.vue` — fetch on open, pass props to sheet — ~30 lines
