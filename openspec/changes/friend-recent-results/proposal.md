# Proposal: friend-recent-results

## Intent

Closes leaiannotti/prode-worldcup-2026#100. Users currently cannot see what another group member predicted on recent matches without asking externally. We will add a bottom sheet that shows a member's last 5 finished-match predictions when tapping their avatar in the standings table.

## Scope

### In Scope
- New backend endpoint `GET /api/groups/<group_id>/members/<user_id>/recent-history?limit=5`
- Reusable `BottomSheet.vue` extracted from `PredictionModal.vue` pattern
- `FriendRecentResultsSheet.vue` consuming the bottom sheet
- Avatar click handler in `LeaderboardTable.vue` emitting `select-user`
- `LeaderboardView.vue` state management for sheet open/close
- Color-coded points: green +3, yellow +1, red +0 (or `—` for no prediction)
- Tests for the new endpoint (TDD required)

### Out of Scope
- Adding `finished_at` column to matches
- Extending existing `/api/scores/history`
- Tooltip, modal, or inline panel variants
- Cross-group visibility
- Header inside the bottom sheet (name/points already visible in standings)

## Capabilities

### New Capabilities
- `friend-recent-results`: backend endpoint and frontend bottom sheet for viewing another group member's predictions on the last N finished matches with scored points

### Modified Capabilities
- None (no existing spec-level behavior changes)

## Approach

**Backend**: dedicated endpoint returns the last 5 finished matches globally (`status = 'finished'`, `kickoff_utc DESC`) left-joined with the target user's predictions and scores. Permission check: requester and target must share the requested group. Return shape: `[{match_teams, prediction, points, score_type}]`.

**Frontend**: extract a generic `BottomSheet.vue` from the existing `PredictionModal.vue` mobile-first pattern (Teleport, Transition, `rounded-t-2xl`, backdrop click). Build `FriendRecentResultsSheet.vue` inside it. Add `@click` on `LeaderboardTable.vue` avatar and emit `select-user` to `LeaderboardView.vue`, which fetches via `api.ts` and controls sheet visibility.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/app/blueprints/scores.py` | New | `GET /api/groups/<group_id>/members/<user_id>/recent-history` endpoint |
| `backend/app/services/scoring_service.py` | Modified | Reuse `calculate_score` for joined predictions |
| `backend/tests/test_leaderboard.py` | New | TDD tests for endpoint and permissions |
| `frontend/src/components/LeaderboardTable.vue` | Modified | Avatar click handler, emit event |
| `frontend/src/components/BottomSheet.vue` | New | Reusable wrapper extracted from `PredictionModal.vue` |
| `frontend/src/components/FriendRecentResultsSheet.vue` | New | Bottom sheet content for recent results |
| `frontend/src/views/LeaderboardView.vue` | Modified | Sheet state + fetch orchestration |
| `frontend/src/lib/api.ts` | Modified | New API client method |
| `frontend/src/stores/leaderboard.ts` | Modified | New action for fetching member recent history |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Same-day match ordering feels wrong without `finished_at` | Low | Use `kickoff_utc DESC`; acceptable for MVP |
| Permission leakage across groups | Low | Explicit group membership check in endpoint |
| BottomSheet extraction breaks existing `PredictionModal.vue` | Low | Keep existing modal untouched; extract only shared layout |
| TDD effort adds time | Med | Budgeted; tests written before implementation |

## Rollback Plan
- Revert the backend blueprint registration (one route)
- Remove the two new Vue components and the avatar click handler
- No database changes; zero-downtime rollback

## Dependencies
- None

## Success Criteria
- [ ] Tapping a member's avatar opens the bottom sheet with 5 rows
- [ ] Each row shows match teams, the member's prediction, and points with correct color
- [ ] No prediction shows `—` with 0 points in red
- [ ] Endpoint returns 403 if requester and target are not in the same group
- [ ] Only finished matches are included
- [ ] All new code covered by tests (backend)
