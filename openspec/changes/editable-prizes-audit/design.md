# Design: Editable Prizes with Inline Audit History

## Technical Approach

Add a new `PATCH /api/groups/:id/prizes` endpoint that accepts partial prize updates, validates membership (or system admin), trims descriptions, compares each rank against the DB, and emits `prize_changed` events only for actual changes. Extend `GET /api/activity` with optional `group_id` and `event_type` filters, gating `group_id` behind membership validation. On the frontend, replace the read-only prize block in `LeagueDetailModal.vue` with an inline edit mode and a collapsible "Ver historial" section that fetches the last 10 `prize_changed` events.

## Architecture Decisions

| Decision | Options | Tradeoff | Chosen |
|----------|---------|----------|--------|
| Validation location | Pydantic schema vs service layer | Pydantic keeps HTTP contract declarative; service layer is imperative. Reuse existing `field_validator` pattern. | Pydantic `PatchPrizeItem` with `mode='after'` trim validator |
| Auth check | New decorator vs inline | Inline avoids decorator indirection; existing helpers (`_is_group_member`, `admin_required`) are already imported. | Inline: `if not _is_group_member(...) and g.current_user.email not in ADMIN_EMAILS: return 403` |
| Update semantics | Pessimistic vs optimistic | Pessimistic matches existing store patterns (`createGroup`, `joinGroup`). Optimistic adds rollback complexity. | Pessimistic (store action → API → update local state on success) |
| Activity limit | API default 20 vs override to 10 | The global feed default should stay 20. The audit section passes `limit=10` explicitly. | API keeps default 20; frontend requests `limit=10` |
| Admin marker source | Payload `actor_is_admin` vs resolve from user | Frontend is admin-blind; payload is self-contained and works offline. | Payload includes `actor_is_admin` (system admin) |
| Race condition | Last-write-wins vs optimistic locking | Locking is overkill for this feature; audit trail shows both edits. | Document last-write-wins explicitly |

## Data Flow

```
LeagueDetailModal.vue
  ├─ isEditing=true ──→ draftPrizes (local copy)
  ├─ Save ──→ groupsStore.patchPrizes(id, draftPrizes)
  │            └─ axios PATCH /api/groups/:id/prizes
  │                 └─ groups.py handler
  │                      ├─ auth check (member OR admin)
  │                      ├─ per-rank diff loop
  │                      │   ├─ update GroupPrize row
  │                      │   └─ emit_event(prize_changed, payload)
  │                      └─ db.session.commit() (single)
  │                 └─ 200 → update currentGroup.prizes
  └─ Ver historial ──→ activityStore.fetchActivity({group_id, event_type: 'prize_changed', limit: 10})
                            └─ GET /api/activity?group_id=...&event_type=...&limit=10
                                 └─ activity.py handler
                                      ├─ membership gate
                                      ├─ query filter + newest-first
                                      └─ return events
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/schemas/group.py` | Modify | Add `PatchPrizeItem` and `PatchPrizesRequest` schemas |
| `backend/app/blueprints/groups.py` | Modify | Add `PATCH /api/groups/<group_id>/prizes` handler |
| `backend/app/blueprints/activity.py` | Modify | Add `group_id`, `event_type` query params + membership gate |
| `frontend/src/stores/groups.ts` | Modify | Remove dead `setPrizes`; add `patchPrizes` action |
| `frontend/src/stores/activity.ts` | Modify | Add query params to `fetchActivity`; add `prize_changed` to union |
| `frontend/src/components/LeagueDetailModal.vue` | Modify | Inline edit mode + collapsible audit history |
| `frontend/src/components/NavBar.vue` | Modify | Add `prize_changed` rendering in `eventText` switch |
| `frontend/src/i18n/es.json` | Modify | Add `leagueDetail.editPrizes`, `leagueDetail.viewHistory`, `leagueDetail.hideHistory`, `activity.prizeChanged` |
| `frontend/src/i18n/en.json` | Modify | Same keys in English |
| `backend/tests/test_groups.py` | Modify | Add `TestPatchPrizes` class |
| `backend/tests/test_activity.py` | Modify | Add `group_id` / `event_type` filter tests |
| `frontend/src/stores/groups.test.ts` | Create | Test `patchPrizes` action |
| `frontend/src/components/LeagueDetailModal.test.ts` | Create | Test edit toggle, save flow, history expand/collapse |

## Interfaces / Contracts

```python
# backend/app/schemas/group.py
class PatchPrizeItem(BaseModel):
    rank: int = Field(..., ge=1, le=3)
    description: str = Field(..., max_length=200)

    @field_validator("description", mode="after")
    @classmethod
    def trim_and_validate(cls, v: str) -> str:
        trimmed = v.strip()
        if len(trimmed) == 0:
            raise ValueError("description cannot be empty after trimming")
        return trimmed

class PatchPrizesRequest(BaseModel):
    prizes: List[PatchPrizeItem] = Field(..., min_length=1, max_length=3)

# backend/app/blueprints/activity.py — query param contract
# group_id (optional, string): if provided, membership gate applies
# event_type (optional, string): filters to exact event type
# limit (optional, int, default 20, max 50): unchanged from existing
```

**Activity payload contract** (emitted by PATCH handler):
```json
{
  "rank": 1,
  "previous_value": "old description",
  "new_value": "new description",
  "actor_is_admin": false
}
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | `PatchPrizeItem` trim/empty validation | Pydantic model direct assertions |
| Integration | PATCH endpoint permission matrix (member, non-member, admin) | `test_groups.py` with `seed_user` + `client` |
| Integration | Per-rank diff: no-op silent, actual change emits event, payload shape | `test_groups.py` with DB assertions on `ActivityEvent` |
| Integration | Activity endpoint `group_id` + `event_type` filters + membership gate | `test_activity.py` |
| Integration | Activity endpoint default behavior preserved (no params) | `test_activity.py` re-run existing cases |
| Component | `LeagueDetailModal`: edit toggle, save, error surface, history expand/collapse | vitest + vue-test-utils |
| Store | `groups.ts`: `patchPrizes` calls correct URL and updates state | vitest with mocked `apiClient` |
| Store | `activity.ts`: `fetchActivity` passes query params | vitest with mocked `apiClient` |

## Migration / Rollout

No migration required. `GroupPrize` table already exists. `ActivityEvent` payload is JSON with no schema constraints. Rollback is code-only.

## Open Questions

- None
