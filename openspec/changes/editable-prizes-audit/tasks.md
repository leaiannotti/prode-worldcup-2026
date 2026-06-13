# Tasks: Editable Prizes with Inline Audit History

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~630 (backend ~350 + frontend ~280) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 → PR 4 |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Backend PATCH endpoint + schema + per-rank diff + tests | PR 1 | base: main; includes TDD for auth, validation, no-op, emission |
| 2 | Backend activity filters + membership gate + tests | PR 2 | base: main; can be reviewed independently; merges after or parallel to PR 1 |
| 3 | Frontend stores (patchPrizes, fetchActivity params) + dead code removal + tests | PR 3 | base: main; depends on PR 1 + 2 for e2e, but unit tests are standalone |
| 4 | Frontend UI (LeagueDetailModal, NavBar, i18n) + tests | PR 4 | base: PR 3 branch; consumes stores and backend endpoints |

## Phase 1: Backend Foundation

- [x] 1.1 Create `backend/app/schemas/group.py` — add `PatchPrizesRequest` with `mode='after'` trim validator
- [x] 1.2 Write backend tests (RED) — `test_groups.py`: `TestPatchPrizes` class covering auth 403, admin 200, validation 422, empty trim, missing key, no-op, per-rank diff emission
- [x] 1.3 Implement `backend/app/blueprints/groups.py` — `PATCH /api/groups/<group_id>/prizes` handler with auth check, per-rank diff loop, `prize_changed` event emission, atomic commit
- [x] 1.4 Run backend tests (GREEN) — verify all `TestPatchPrizes` scenarios pass
- [x] 1.5 Write backend tests (RED) — `test_activity.py`: add `group_id` filter membership gate, `event_type` filter, default limit 10, custom limit, admin bypass
- [x] 1.6 Implement `backend/app/blueprints/activity.py` — add `group_id`, `event_type` query params, membership gate, newest-first ordering
- [x] 1.7 Run backend tests (GREEN) — verify activity filter scenarios pass
- [x] 1.8 Refactor — extract reusable emission helper or inline cleanup if needed

## Phase 2: Frontend Foundation

- [x] 2.1 Remove dead `setPrizes` from `frontend/src/stores/groups.ts` and all references
- [x] 2.2 Write frontend tests (RED) — `frontend/src/stores/groups.test.ts`: `patchPrizes` calls correct URL, updates state, handles error
- [x] 2.3 Implement `frontend/src/stores/groups.ts` — add `patchPrizes` action
- [x] 2.4 Run frontend tests (GREEN) — stores pass
- [x] 2.5 Write frontend tests (RED) — `frontend/src/stores/activity.test.ts`: `fetchActivity` passes `group_id`, `event_type`, `limit` query params
- [x] 2.6 Implement `frontend/src/stores/activity.ts` — add query params to `fetchActivity`, add `'prize_changed'` to union
- [x] 2.7 Run frontend tests (GREEN) — activity store passes

## Phase 3: Frontend UI

- [x] 3.1 Write frontend tests (RED) — `frontend/src/components/LeagueDetailModal.test.ts`: edit toggle, save flow, validation error, history expand/collapse, audit line rendering
- [x] 3.2 Implement `frontend/src/components/LeagueDetailModal.vue` — inline editable inputs for prizes, collapsible "Ver historial" section, fetch filtered activity
- [x] 3.3 Run frontend tests (GREEN) — component tests pass
- [x] 3.4 Modify `frontend/src/components/NavBar.vue` — add `prize_changed` rendering in `eventText` switch with admin marker
- [x] 3.5 Add i18n keys to `frontend/src/i18n/es.json` and `frontend/src/i18n/en.json`: `leagueDetail.editPrizes`, `leagueDetail.viewHistory`, `leagueDetail.hideHistory`, `activity.prizeChanged`
- [x] 3.6 Run frontend tests (GREEN) — full suite passes

## Phase 4: Integration & Verification

- [ ] 4.1 End-to-end manual check: open LeagueDetailModal, edit prizes, save, expand history, verify audit line format
- [ ] 4.2 Verify non-member receives 403 on PATCH and filtered activity
- [ ] 4.3 Verify no-op save produces no `prize_changed` events
- [ ] 4.4 Run full backend test suite (`pytest`) and frontend test suite (`vitest`) — all pass
- [ ] 4.5 Update CHANGELOG or release notes if required

## Phase 5: Cleanup

- [ ] 5.1 Remove any temporary TODOs or debug code
- [ ] 5.2 Verify all acceptance criteria from proposal are met
- [ ] 5.3 Confirm no `setPrizes` references remain in codebase (`grep -r setPrizes`)
