# Proposal: Editable Prizes with Inline Audit History

## Intent

League prizes are set only at creation and editable only by the owner via an unused PUT endpoint. Members need to adjust prizes as the tournament evolves, but they cannot. This change makes prizes editable by any league member with full transparency through an inline audit history.

## Scope

### In Scope
- New `PATCH /api/groups/:id/prizes` (member or admin)
- Extend `GET /api/activity` with `group_id` and `event_type` filters
- `prize_changed` activity events with per-rank diffs
- Inline editable prizes + collapsible audit history in `LeagueDetailModal.vue`
- Remove dead `setPrizes` frontend code

### Out of Scope
- Voting / approval flows
- Push notifications
- Automatic revert
- Pagination beyond 10 events
- Migrating the existing owner-only PUT endpoint

## Capabilities

### New Capabilities
- `group-prizes`: Bulk PATCH endpoint for prizes with member/admin auth and per-rank diff emission
- `activity-filter`: Query params `group_id` and `event_type` on activity list with membership validation

### Modified Capabilities
- None

## Approach

Add a new `PATCH` route in `groups.py` that validates membership or admin status, trims and compares each rank against the database, updates only changed rows, and emits `prize_changed` events. Extend the activity endpoint to filter by `group_id` (with membership check) and `event_type`. On the frontend, replace read-only prize display with inline inputs and add a collapsible "Ver historial" section that fetches the filtered activity endpoint.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/app/blueprints/groups.py` | New | `PATCH /api/groups/:id/prizes` handler |
| `backend/app/blueprints/activity.py` | Modified | Add `group_id` + `event_type` query params |
| `backend/app/services/activity_service.py` | New | `prize_changed` emission logic |
| `frontend/src/components/LeagueDetailModal.vue` | Modified | Inline editing + collapsible audit history |
| `frontend/src/stores/groups.ts` | Modified | Add `patchPrizes`, remove dead `setPrizes` |
| `frontend/src/stores/activity.ts` | Modified | Add query params to `fetchActivity` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Activity endpoint query changes break existing user feed | Low | Keep existing `user_id` filter as default; add tests |
| Admin status is backend-only | Low | Frontend shows edit UI for all members; backend enforces auth |
| Race condition on concurrent edits | Low | Last-write-wins acceptable; audit trail shows both |

## Rollback Plan

- Revert the `PATCH` route and activity query changes
- Restore the dead `setPrizes` code if needed
- No schema changes required; rollback is code-only

## Dependencies

- None

## Success Criteria

- [ ] Any member can PATCH prizes and see changes immediately
- [ ] `prize_changed` events appear in the collapsible audit history
- [ ] Non-members receive 403 on both PATCH and activity filtered by group
- [ ] All dead `setPrizes` code removed
- [ ] Backend and frontend tests pass with strict TDD
