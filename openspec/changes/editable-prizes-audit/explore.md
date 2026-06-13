# Exploration: Editable Prizes with Inline Audit History

## Current State

### Prize Storage
- Prizes live in the `GroupPrize` model (`backend/app/models/group.py`), a separate table with:
  - `group_id` (FK → `prediction_groups`)
  - `rank` (1–3, with `CHECK rank BETWEEN 1 AND 3`)
  - `description` (255 chars)
  - Unique constraint on `(group_id, rank)`
- Prizes are set **only at group creation** via `POST /api/groups` (optional `prizes` array).
- There is an existing `PUT /api/groups/:id/prizes` endpoint that is **owner-only** and performs a **full replacement** (deletes all existing prizes, then inserts new ones).
- The frontend `setPrizes` action in `groups.ts` is **dead code** — it calls `POST` while the backend expects `PUT`, and no component imports or uses `setPrizes`.

### Activity Event System
- `ActivityEvent` model (`backend/app/models/activity.py`): `id`, `user_id`, `event_type`, `group_id`, `match_id`, `payload` (JSON), `occurred_at`.
- `emit_event()` in `activity_service.py` is **best-effort** — uses `flush()`, swallows exceptions, never raises.
- Existing event types: `group_created`, `group_joined`, `prediction_submitted`, `prediction_updated`, `score_calculated`.
- `GET /api/activity` (`backend/app/blueprints/activity.py`) filters **only by `user_id`** (current user). It supports cursor pagination (`limit`, `cursor`) but **has no `group_id` or `event_type` query params**.
- Admin has a separate `GET /api/admin/audit-log` endpoint (unfiltered, admin-only).

### League Detail Modal
- `frontend/src/components/LeagueDetailModal.vue` is a modal (not a page) triggered from the dashboard.
- Displays: header (name + member count), invite code, **read-only prizes**, actions (leave/delete).
- `isAdmin` is computed as `group.creator_id === authStore.user?.id` — this is **group admin**, not system admin.
- No inline editing exists today.

### Groups Blueprint Patterns
- Helpers: `_is_group_member(user_id, group_id)` and `_is_group_owner(user_id, group_id)`.
- Auth: `@jwt_required` sets `g.current_user`. `@admin_required` checks `user.email in ADMIN_EMAILS`.
- Membership checks return `403` when user is not a member.
- Admin endpoints are in a separate `admin.py` blueprint.

### Frontend Auth Store
- `frontend/src/stores/auth.ts` has `User` interface with `id`, `email`, `name`, `picture`. No `isAdmin` flag.
- System admin status is **server-side only** (`ADMIN_EMAILS` in `auth.py`).

---

## Affected Areas

| Path | Why affected |
|------|-------------|
| `backend/app/blueprints/groups.py` | New `PATCH /api/groups/:id/prizes` endpoint; membership validation + admin god-mode |
| `backend/app/blueprints/activity.py` | Add `group_id` and `event_type` optional query params to `GET /api/activity` |
| `backend/app/services/activity_service.py` | New `prize_changed` event emission |
| `backend/app/models/activity.py` | No schema change needed (payload is JSON), but `event_type` enum/taxonomy docs should be updated |
| `backend/app/schemas/group.py` | May need a new `PatchPrizesRequest` schema for partial updates |
| `frontend/src/components/LeagueDetailModal.vue` | Inline editable prize fields + collapsible audit history section |
| `frontend/src/stores/groups.ts` | New `patchPrizes()` action; fix or remove dead `setPrizes()` code |
| `frontend/src/stores/activity.ts` | Add `group_id` and `event_type` params to `fetchActivity()`; add `prize_changed` to `ActivityEvent` union |
| `frontend/src/i18n/*.json` | New strings: "Editar premios", "Ver historial", "prizeChanged" activity copy, etc. |
| `backend/tests/test_groups.py` | Tests for new PATCH endpoint and permission matrix (member, non-member, admin) |
| `backend/tests/test_activity.py` | Tests for `group_id` and `event_type` filtering |
| `frontend/src/components/NavBar.vue` | Add `prize_changed` to activity event rendering switch |

---

## Approaches

### 1. Extend existing PUT endpoint to PATCH semantics + add membership check
- **What**: Reuse the existing `PUT /api/groups/:id/prizes` route, change auth from owner-only to member-or-admin, and switch to partial-update semantics.
- **Pros**: Minimal new endpoint surface; reuses `SetPrizesRequest` schema (or adapts it); less backend code.
- **Cons**: PUT is semantically full replacement — partial updates violate REST conventions; frontend must send all prizes even if only one changed; harder to emit per-rank `prize_changed` events because the old endpoint bulk-deletes.
- **Effort**: Low

### 2. New `PATCH /api/groups/:id/prizes` endpoint (recommended)
- **What**: Create a new `PATCH` endpoint that accepts only the prizes being changed (e.g., `[{rank: 1, description: "new"}]`). For each changed rank, read the old value, update the row, emit `prize_changed` event.
- **Pros**: Semantically correct for partial updates; precise audit trail (only changed ranks emit events); smaller payload; clear separation from the old owner-only PUT endpoint.
- **Cons**: Slightly more new code; need a new Pydantic schema (`PatchPrizesRequest`).
- **Effort**: Medium

### 3. Separate `prize_history` table instead of activity events
- **What**: Store previous prize values in a dedicated `prize_history` table (or JSON column on `GroupPrize`).
- **Pros**: No need to modify the activity endpoint; history is tightly coupled to prizes.
- **Cons**: Violates the explicit requirement to use the existing activity endpoint; introduces a new persistence pattern not used elsewhere; more schema complexity.
- **Effort**: High

---

## Recommendation

**Approach 2** — new `PATCH /api/groups/:id/prizes` endpoint.

Rationale:
- The requirement explicitly names `PATCH /api/groups/:id/prizes`.
- Partial updates are the right semantic fit (members may edit only one prize at a time).
- The existing `PUT` endpoint is owner-only and does bulk replacement — it cannot cleanly emit per-rank `prize_changed` events without significant refactoring.
- The old `PUT` endpoint can be left in place for backward compatibility (or marked deprecated later) since it has no frontend callers.

For the audit trail:
- Modify `GET /api/activity` to accept optional `group_id` and `event_type` query params.
- When `group_id` is provided, the endpoint must check membership (or admin) and return events for that group regardless of `user_id`. When `group_id` is absent, keep existing behavior (current user's own events).
- This satisfies the requirement "served from existing activity endpoint" without adding a new route.

For the frontend:
- Add inline editing to `LeagueDetailModal.vue` — small text inputs or a pencil-icon toggle that switches prize display to editable fields.
- Add a collapsible "Ver historial" section below prizes that fetches `/api/activity?group_id={id}&event_type=prize_changed&limit=10`.
- No nested modals — everything stays inline in the existing modal.

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Activity endpoint currently has no `group_id` or `event_type` filter** | Medium — requires modifying the existing query logic and adding membership validation | Add query params with fallback to existing `user_id` filter; add tests for both filtered and unfiltered modes |
| **Admin god-mode requires backend check only** | Low — frontend does not need to know system admin status | Backend `PATCH` endpoint checks `_is_group_member() OR admin_required`; frontend shows edit UI for all members |
| **No `prize_changed` event type in frontend union** | Low — TypeScript will flag it | Add `prize_changed` to `ActivityEvent` union in `activity.ts` and add case in `NavBar.vue` switch |
| **Frontend `setPrizes` calls POST but backend expects PUT** | Low — dead code, but could confuse future devs | Either fix the method or remove `setPrizes` entirely during this change |
| **Audit history shows all `prize_changed` events for the group** | Medium — privacy: members see who changed what | This is **by design** (social transparency), but we should ensure the endpoint rejects non-members |
| **Race condition: two members edit same prize simultaneously** | Low — last write wins, audit trail shows both changes | Acceptable for this iteration; no locking needed per requirements |
| **PATCH payload schema needs to support partial updates** | Low — new schema required | Create `PatchPrizesRequest` with `prizes: List[PrizeRequest]` (min 1, max 3) |

---

## Reusable Pieces vs Net-New

### Reusable (no changes needed)
- `GroupPrize` model and table
- `emit_event()` service
- `ActivityEvent` model
- `_is_group_member()` helper
- `PrizeRequest` / `PrizeResponse` schemas
- `apiClient` and `useAuthStore` patterns

### Net-New (must be created)
- `PATCH /api/groups/:id/prizes` route handler
- `PatchPrizesRequest` schema (or reuse `SetPrizesRequest` with partial semantics)
- Per-rank diff logic in PATCH handler (read old value, write new, emit event)
- `group_id` + `event_type` query param handling in `GET /api/activity`
- Membership validation when `group_id` is provided on activity endpoint
- Inline editing UI in `LeagueDetailModal.vue`
- Collapsible audit history UI in `LeagueDetailModal.vue`
- `prize_changed` i18n strings and activity rendering

### Modified (existing code changes)
- `backend/app/blueprints/activity.py` — add query param filters
- `frontend/src/stores/activity.ts` — add query params to `fetchActivity`
- `frontend/src/stores/groups.ts` — add `patchPrizes` action, fix/remove `setPrizes`
- `frontend/src/components/NavBar.vue` — add `prize_changed` to activity event switch

---

## Ready for Proposal

**Yes** — sufficient information exists to write the proposal.

The orchestrator should tell the user:
- The existing `PUT /api/groups/:id/prizes` is owner-only and unused by the frontend; the cleanest path is a new `PATCH` endpoint.
- The activity endpoint needs `group_id` and `event_type` query params — this is the biggest backend change beyond the PATCH itself.
- All members will see edit controls (backend enforces permissions); no frontend admin flag needed.
- The audit history will show the last 10 changes inline in the modal, toggled by a button.
- No voting, approval, notifications, or pagination are required per the confirmed scope.
