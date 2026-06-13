## Exploration: friend-recent-results

### Current State

The app is a Vue 3 + Flask monorepo. Users join prediction groups (leagues) and predict scores for World Cup 2026 group-stage matches. The standings table is rendered in `LeaderboardTable.vue`, and the avatar is currently a non-clickable `<img>` / `<div>` with initials. The closest existing UI pattern to a "bottom sheet" is `PredictionModal.vue`, which is styled as a mobile-first sheet (`items-end sm:items-center`, `rounded-t-2xl`, `translateY` entrance animation). The `PointsDrawer.vue` shows the current user's own scored history, but it is a right-side drawer, not a bottom sheet.

The match model has a `status` enum (`scheduled`, `in_progress`, `finished`) but no `finished_at` timestamp. The last 5 finished matches must be inferred by querying `status = "finished"` ordered by `kickoff_utc` desc. The prediction model stores `home_score`, `away_score` per user per match. Scoring logic (`calculate_score`) lives in `backend/app/services/scoring_service.py` and produces `points` (0, 1, 3) and `score_type` ("exact", "outcome", "miss"). `PredictionScore` stores the computed result.

There is NO existing endpoint that returns another user's predictions. The current `/api/scores/history` returns only the **current** user's full history. The `/api/predictions/matches/:match_id/group/:group_id` returns all members' predictions for a **single** match, but only post-deadline.

### Affected Areas

- `frontend/src/components/LeaderboardTable.vue` — avatar needs click handler, emit event with user_id
- `frontend/src/components/PredictionModal.vue` — UI pattern reference for mobile-first bottom sheet (reusable structure)
- `frontend/src/components/PointsDrawer.vue` — data shape reference for scored history rows (points badge, match info, prediction)
- `frontend/src/views/LeaderboardView.vue` — needs to manage bottom sheet state and handle user selection
- `frontend/src/stores/leaderboard.ts` — may need a new action for fetching "another user's recent results"
- `frontend/src/lib/api.ts` — API client already exists (axios wrapper)
- `backend/app/blueprints/scores.py` — needs new endpoint or extended logic to serve another user's predictions for the last 5 finished matches
- `backend/app/services/scoring_service.py` — scoring logic is already correct and reusable
- `backend/app/models/match.py` — no `finished_at` field; ordering finished matches uses `kickoff_utc` desc
- `backend/tests/test_leaderboard.py`, `backend/tests/test_predictions.py` — new tests needed for the endpoint

### Approaches

1. **Extend existing `/api/scores/history` with optional `user_id`**
   - Add `user_id` query param. If absent, return current user (existing behavior). If present, verify that the requester and target share a group membership, then return the target's history.
   - Filter to last 5 finished matches globally, and include matches where the user did NOT predict (showing `null` prediction + 0 points).
   - Pros: Minimal route surface, reuses existing schema and serialization logic.
   - Cons: Mixes current-user and other-user concerns in one endpoint; permission checks are slightly more complex.
   - Effort: Medium

2. **Create new endpoint `GET /api/scores/users/<user_id>/recent-results?limit=5`**
   - Dedicated endpoint. Returns exactly the last N finished matches joined with the target user's predictions.
   - Must verify that the requesting user and target user share at least one group membership (or are in the same group identified by `group_id` query param).
   - Pros: Clean separation, explicit contract, easier to test in isolation.
   - Cons: Slightly more boilerplate (new route, schema, tests).
   - Effort: Medium

3. **Frontend: Reuse `PredictionModal.vue` pattern as a generic BottomSheet component**
   - Extract the mobile-first sheet layout (Teleport, Transition, `items-end sm:items-center`, `rounded-t-2xl`, backdrop click) into a new `BottomSheet.vue` wrapper.
   - `FriendRecentResultsSheet.vue` would consume it.
   - Pros: Establishes a reusable bottom sheet primitive for future features; consistent with existing mobile-first modals.
   - Cons: One-time extraction cost; if this is the only bottom sheet ever needed, may be overkill.
   - Effort: Medium

4. **Frontend: Inline the sheet inside `LeaderboardView.vue` without extracting a generic BottomSheet**
   - Copy the Teleport/Transition structure from `PredictionModal.vue` directly into a new inline component or into `LeaderboardView.vue`.
   - Pros: Fastest to implement; no abstraction risk.
   - Cons: Duplicated animation/layout code; harder to maintain.
   - Effort: Low

### Recommendation

- **Backend**: Create a new endpoint `GET /api/scores/users/<user_id>/recent-results` (Approach 2). It is cleaner, explicit, and avoids mutating the current user's history contract. The endpoint should:
  1. Verify JWT.
  2. Verify that the requester and target are members of the same group (pass `group_id` as query param for explicit context, or check any shared group).
  3. Query the last 5 finished matches (`status = "finished"`, ordered by `kickoff_utc` desc).
  4. Left-join the target user's predictions and scores.
  5. Return a list where each item includes: match teams, actual result, prediction (or null), and points (or 0 if no prediction).
- **Frontend**: Create a reusable `BottomSheet.vue` wrapper (Approach 3). The project already has strong mobile-first PWA usage, and this pattern will likely be needed again. Then build `FriendRecentResultsSheet.vue` inside it. Add `@click` to the avatar in `LeaderboardTable.vue` and emit a `select-user` event up to `LeaderboardView.vue`.

### Risks

- **Match ordering ambiguity**: Without a `finished_at` timestamp, ordering by `kickoff_utc` desc is the best proxy. If two matches finish on the same day, the order might feel wrong to users. The user should confirm this is acceptable.
- **Permission model**: Currently, there is no explicit privacy rule saying "members can see each other's predictions for finished matches." The existing `get_group_match_predictions` endpoint already exposes post-deadline predictions to all group members. Extending this to finished-match history is consistent, but the user should confirm there are no privacy objections.
- **No prediction = 0 points?**: The requirement says "If the user did not predict a given match, show ARG-ALG — 0". Technically, a user who did not predict gets 0 points. This is a product decision that should be confirmed.
- **TDD enforcement**: The project requires strict TDD. Any new endpoint must be written with failing tests first. This adds effort but is required by the project convention.
- **PWA touch targets**: The avatar in `LeaderboardTable.vue` is currently `w-10 h-10` (40px). This is acceptable for touch, but the hit area should be padded if we wrap it in a button.

### Ready for Proposal

**Yes**, but the orchestrator should ask the user the following clarifying questions before moving to `sdd-propose`:

1. Should the "last 5 finished matches" be global across all World Cup groups, or should they be filtered by the league/group the user is viewing?
2. Is ordering by `kickoff_utc` desc acceptable for "most recent finished"? (There is no `finished_at` timestamp in the DB.)
3. Should we confirm that any group member can see any other member's predictions for finished matches, or is there a privacy restriction?
4. For a match where the user did not predict, should we literally show `0` points (red), or a dash (`—`) to indicate "no prediction"? The requirement says `— 0` but the color-coding rules suggest 0 is red.
5. Should we extract a generic `BottomSheet.vue` component, or inline the sheet for this single use case?
