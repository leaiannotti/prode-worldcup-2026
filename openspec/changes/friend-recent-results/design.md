# Design: friend-recent-results

## Technical Approach

Add a dedicated backend endpoint that returns the last 5 finished matches globally, left-joined with a target user's predictions and scores. Reuse the existing `calculate_score` logic. On the frontend, extract a generic `BottomSheet.vue` from the `PredictionModal.vue` pattern and build `FriendRecentResultsSheet.vue` inside it. Wire avatar clicks in `LeaderboardTable.vue` through `LeaderboardView.vue` to fetch and display the sheet.

## Architecture Decisions

| Decision | Options | Tradeoffs | Selected |
|----------|---------|-----------|----------|
| Blueprint placement | `groups.py` (`/api/groups/...`) vs `scores.py` (`/api/scores/...`) | `groups.py` matches the `/api/groups` prefix; `scores.py` groups score-related logic | `scores.py` with route `/api/scores/groups/<group_id>/members/<user_id>/recent-history` — keeps score logic together and avoids mixing group-management routes with score history |
| Permission check | Query `group_id` param and check shared membership | Simplest; group context is already known from the leaderboard view | Shared membership via `_is_group_member(current_user_id, group_id)` — same helper already in `scores.py` |
| Match ordering | `kickoff_utc DESC` (no `finished_at` column) | Acceptable for MVP; no schema change required | `kickoff_utc DESC` with explicit `status = 'finished'` |
| BottomSheet extraction | Extract generic wrapper vs inline in new component | Extraction costs ~20 lines but creates reusable primitive for future mobile features | Extract generic `BottomSheet.vue`; project is mobile-first PWA and this pattern will likely be reused |
| No-prediction display | Show `—` (dash) with 0 points vs show nothing | `—` is clearer for "no prediction"; requirement explicitly says `— 0` | Show `—` with 0 points in red |

## Data Flow

```
User taps avatar in LeaderboardTable.vue
  └── emit('select-user', { user_id, name, picture })
      └── LeaderboardView.vue captures → sets selectedUserId + isSheetOpen
          └── Calls leaderboardStore.fetchMemberRecentHistory(groupId, userId)
              └── GET /api/scores/groups/:groupId/members/:userId/recent-history?limit=5
                  └── Backend: verify JWT → verify shared group → query last 5 finished matches
                      └── LEFT JOIN predictions + scores for target user
                          └── Return JSON → Pinia store → FriendRecentResultsSheet.vue renders
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/blueprints/scores.py` | Modify | Add `GET /api/scores/groups/<group_id>/members/<user_id>/recent-history` endpoint |
| `backend/app/schemas/score.py` | Modify | Add `MemberRecentHistoryEntry` and `MemberRecentHistoryResponse` schemas |
| `backend/tests/test_leaderboard.py` | Modify | Add TDD test cases for new endpoint and permissions |
| `frontend/src/components/BottomSheet.vue` | Create | Reusable wrapper extracted from `PredictionModal.vue` (Teleport, Transition, backdrop, `rounded-t-2xl`) |
| `frontend/src/components/FriendRecentResultsSheet.vue` | Create | Content component consuming `BottomSheet`; displays 5 rows with match, prediction, points |
| `frontend/src/components/LeaderboardTable.vue` | Modify | Add `@click` on avatar wrapper; emit `select-user` with user object |
| `frontend/src/views/LeaderboardView.vue` | Modify | Add `selectedUserId`, `isSheetOpen`; handle `select-user` event; fetch and render sheet |
| `frontend/src/lib/api.ts` | Modify | Add `getMemberRecentHistory(groupId, userId, limit=5)` method |
| `frontend/src/stores/leaderboard.ts` | Modify | Add `fetchMemberRecentHistory` action; add `memberRecentHistory` state |
| `frontend/src/i18n/es.json` | Modify | Add `friendRecentResults` keys (title, noPredictions, exact, outcome, noPoints) |
| `frontend/src/i18n/en.json` | Modify | Add `friendRecentResults` keys (title, noPredictions, exact, outcome, noPoints) |

## Interfaces / Contracts

### Backend Route

```python
@scores_bp.route("/groups/<group_id>/members/<user_id>/recent-history", methods=["GET"])
@jwt_required
def get_member_recent_history(group_id, user_id):
    """GET /api/scores/groups/<group_id>/members/<user_id>/recent-history?limit=5
    
    Returns last N finished matches globally, left-joined with target user's predictions.
    403 if requester and target do not share the group.
    """
```

### Response JSON Shape

```json
{
  "user_id": "uuid",
  "group_id": "uuid",
  "history": [
    {
      "match": {
        "id": 1,
        "home_team_code": "ARG",
        "away_team_code": "ALG",
        "kickoff_utc": "2026-06-14T20:00:00Z",
        "status": "finished"
      },
      "actual_result": {
        "home_score": 2,
        "away_score": 1
      },
      "prediction": {
        "home_score": 2,
        "away_score": 1
      },
      "points": 3,
      "score_type": "exact"
    }
  ]
}
```

For no prediction: `prediction` is `null`, `points` is `0`, `score_type` is `null`.

### SQL/ORM Query Strategy

```python
from sqlalchemy import desc

matches = (
    Match.query
    .filter_by(status="finished")
    .order_by(desc(Match.kickoff_utc))
    .limit(limit)
    .all()
)

results = []
for match in matches:
    pred = Prediction.query.filter_by(user_id=target_user_id, match_id=match.id).first()
    score = None
    if pred:
        score = PredictionScore.query.filter_by(prediction_id=pred.id).first()
    
    entry = {
        "match": { ... },
        "actual_result": {
            "home_score": match.home_score,
            "away_score": match.away_score,
        } if match.home_score is not None else None,
        "prediction": {
            "home_score": pred.home_score,
            "away_score": pred.away_score,
        } if pred else None,
        "points": score.points if score else 0,
        "score_type": score.score_type if score else None,
    }
    results.append(entry)
```

Note: `calculate_score` is NOT called at query time; `PredictionScore` rows are already persisted by `score_match` in `scoring_service.py`. We reuse the stored score.

### Frontend Components

**BottomSheet.vue** (generic wrapper)
```vue
<template>
  <Teleport to="body">
    <Transition name="bottom-sheet">
      <div v-if="isOpen" class="fixed inset-0 bg-black/60 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4" @click.self="emit('close')">
        <div class="bg-surface w-full sm:max-w-md sm:rounded-xl rounded-t-2xl p-6 shadow-xl">
          <slot />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps<{ isOpen: boolean }>()
defineEmits<{ (e: 'close'): void }>()
</script>
```

**FriendRecentResultsSheet.vue**
```vue
<template>
  <BottomSheet :isOpen="isOpen" @close="emit('close')">
    <!-- Content: 5 rows -->
  </BottomSheet>
</template>

<script setup>
interface Props {
  isOpen: boolean
  userId: string
  userName: string
  userPicture?: string
  history: MemberHistoryEntry[]
  loading: boolean
  error: string | null
}
defineProps<Props>()
defineEmits<{ (e: 'close'): void }>()
</script>
```

**LeaderboardTable.vue** — Avatar click:
```vue
<div class="flex items-center gap-3 cursor-pointer" @click="emit('select-user', entry)">
```

**LeaderboardView.vue** — Event handler:
```typescript
const selectedUser = ref<LeaderboardEntry | null>(null)
const isRecentResultsOpen = ref(false)

function handleSelectUser(entry: LeaderboardEntry) {
  selectedUser.value = entry
  isRecentResultsOpen.value = true
  leaderboardStore.fetchMemberRecentHistory(groupId.value, entry.user_id)
}
```

### Pinia Store Action

```typescript
async function fetchMemberRecentHistory(groupId: string, userId: string, limit = 5) {
  loading.value = true
  error.value = null
  try {
    const response = await api.get(
      `/api/scores/groups/${groupId}/members/${userId}/recent-history?limit=${limit}`
    )
    memberRecentHistory.value = response.data.history || []
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to fetch member history'
    if (err.response?.status === 403) {
      error.value = 'not_member'
    }
  } finally {
    loading.value = false
  }
}
```

### API Client Method

```typescript
// In lib/api.ts (or add to store directly using apiClient)
// No new method needed if using apiClient.get directly in the store
// If preferring abstraction:
export const getMemberRecentHistory = (groupId: string, userId: string, limit = 5) =>
  apiClient.get(`/api/scores/groups/${groupId}/members/${userId}/recent-history?limit=${limit}`)
```

### Color Mapping

Reusing existing token classes from `PointsDrawer.vue`:

| Points | Badge Class | Label Class |
|--------|-------------|-------------|
| 3 | `bg-tertiary text-on-tertiary` | `text-tertiary` |
| 1 | `bg-secondary text-on-secondary` | `text-secondary` |
| 0 | `bg-surface-container text-on-surface-variant` | `text-on-surface-variant` |

### i18n Keys

```json
{
  "friendRecentResults": {
    "title": "Últimas predicciones de {name}",
    "noPredictions": "Todavía no hay predicciones finalizadas",
    "exact": "¡Exacto!",
    "outcome": "Resultado",
    "noPoints": "Sin puntos",
    "match": "{home} vs {away}",
    "prediction": "Pred: {home}-{away}",
    "noPrediction": "Sin predicción"
  }
}
```

English equivalents follow the same structure.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | `get_member_recent_history` endpoint | TDD: write tests first in `test_leaderboard.py`. Test: 200 with 5 finished matches, 403 for non-shared group, 404 for nonexistent group, correct shape for no-prediction rows |
| Unit | `BottomSheet.vue` | Verify slot content renders; verify `close` emits on backdrop click |
| Unit | `FriendRecentResultsSheet.vue` | Verify row count, correct color classes, `—` for missing prediction |
| Integration | Avatar click → sheet open → fetch | Test in `LeaderboardView.vue` or Cypress/Playwright if available |
| E2E | Full flow | Tap avatar → sheet appears → 5 rows → correct points colors |

## Migration / Rollout

No database migration required. `PredictionScore` rows already exist for finished matches. Zero-downtime deployment: new endpoint is additive; frontend feature is behind user interaction (avatar click). Rollback: remove blueprint route, delete 2 Vue components, remove avatar click handler.

## Open Questions

- [ ] Should the `limit` parameter have a max cap (e.g., 10) to prevent abuse? (suggested: yes, cap at 10)
- [ ] Should the sheet show a skeleton loader or a spinner? (suggested: reuse `PointsDrawer.vue` pulse skeleton pattern)

