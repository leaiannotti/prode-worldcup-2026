# Verification Report — editable-prizes-audit PR 3 (Frontend Stores)

## Change
- **Name**: `editable-prizes-audit`
- **Slice**: PR 3 of 4 — Frontend Pinia stores + dead `setPrizes` cleanup
- **Branch**: `feat/editable-prizes-audit-pr3-frontend-stores`
- **Mode**: `openspec` (artifact store)
- **Strict TDD**: Active
- **Date**: 2026-06-13

## Completeness

| Task | Status | Evidence |
|------|--------|----------|
| 2.1 Remove dead `setPrizes` | ✅ Complete | `grep -r setPrizes frontend/src/` returns nothing |
| 2.2 Tests (RED) — groups `patchPrizes` | ✅ Complete | `frontend/src/stores/groups.test.ts` (6 tests) |
| 2.3 Implement `groups.patchPrizes` | ✅ Complete | `frontend/src/stores/groups.ts` lines 101–126 |
| 2.4 Tests (GREEN) — groups | ✅ Complete | 6/6 pass |
| 2.5 Tests (RED) — activity query params | ✅ Complete | `frontend/src/stores/activity.test.ts` (4 tests) |
| 2.6 Implement `activity.fetchActivity` extension | ✅ Complete | `frontend/src/stores/activity.ts` lines 27–48 |
| 2.7 Tests (GREEN) — activity | ✅ Complete | 4/4 pass |

**Unchecked tasks (out of scope for this PR)**: 3.1–3.6 (UI), 4.1–4.5 (integration), 5.1–5.3 (cleanup).

**Note**: The `tasks.md` artifact on the PR-2 branch still shows Phase 2 tasks as unchecked (`[ ]`). The authoritative `apply-progress` Engram artifact confirms they are completed. This discrepancy should be resolved when docs are cherry-picked.

## Build / Tests / Coverage

| Command | Result | Details |
|---------|--------|---------|
| `vitest run` (frontend) | ✅ 17 passed, 0 failed | 4 test files, 496ms execution |
| `npx vue-tsc --noEmit` | ❌ 5 errors | 4 errors in changed consumers + 1 pre-existing |

### Coverage — Changed Files

| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `frontend/src/stores/groups.ts` | — | — | — | ➖ Not measured |
| `frontend/src/stores/activity.ts` | — | — | — | ➖ Not measured |
| `frontend/src/stores/groups.test.ts` | — | — | — | — |
| `frontend/src/stores/activity.test.ts` | — | — | — | — |

**Note**: Coverage analysis skipped — `vitest run --coverage` not executed and no coverage threshold configured in project.

## Spec Compliance Matrix

### `league-detail/spec.md` (store-relevant only)

| Requirement | Scenario | Test File | Test Case | Status |
|-------------|----------|-----------|-----------|--------|
| Save flow | Successful save | `groups.test.ts` | `calls PATCH /api/groups/:id/prizes with bulk body` | ✅ COMPLIANT |
| Save flow | Successful save (state update) | `groups.test.ts` | `updates currentGroup prizes on success` | ✅ COMPLIANT |
| Save flow | Successful save (array update) | `groups.test.ts` | `updates groups array prize on success` | ✅ COMPLIANT |
| Save flow | Validation error | `groups.test.ts` | `throws on 422 validation error` | ✅ COMPLIANT |
| Save flow | No-op save | — | Backend concern (not store layer) | ⏸️ SKIPPED |
| Dead code removal | No dead references | `grep` | `setPrizes` absent from `frontend/src/` | ✅ COMPLIANT |

### `cross-cutting/spec.md` (store-relevant only)

| Requirement | Scenario | Test File | Test Case | Status |
|-------------|----------|-----------|-----------|--------|
| Activity event type registration | Frontend type union | Code inspection | `ActivityEvent` includes `'prize_changed'` | ✅ COMPLIANT |
| Audit ordering | Newest-first | — | Backend concern | ⏸️ SKIPPED |
| Locale and relative time | es-AR | — | UI concern (PR 4) | ⏸️ SKIPPED |
| Observable activity event schema | Read-time name resolution | — | UI concern (PR 4) | ⏸️ SKIPPED |

## Correctness Table

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| `patchPrizes` endpoint | `PATCH /api/groups/:id/prizes` | Present at line 106 | ✅ |
| `patchPrizes` body | `{ first?, second?, third? }` | Signature matches exactly | ✅ |
| Partial updates | Only provided keys sent | Payload passed directly to `apiClient.patch` | ✅ |
| State update — `currentGroup` | Updated on success | Lines 108–113 | ✅ |
| State update — `groups` array | Updated on success | Lines 114–120 | ✅ |
| Error surfacing | 403, 422, generic re-thrown | `catch { throw error }` at lines 122–125 | ✅ |
| Error message preserved | Original error not swallowed | Re-throws original `error` | ✅ |
| `fetchActivity` default | No args → `limit=10` | `options?.limit ?? 10` at line 32 | ✅ |
| `fetchActivity` `groupId` | Adds `group_id` param | `params.append('group_id', ...)` at line 35 | ✅ |
| `fetchActivity` `eventType` | Adds `event_type` param | `params.append('event_type', ...)` at line 38 | ✅ |
| `fetchActivity` result shape | Stored in `events.value` | `events.value = response.data.events` at line 41 | ✅ |
| `prize_changed` in union | Added to `ActivityEvent` | Line 10 | ✅ |
| `setPrizes` removed | Gone from store and consumers | Not present in `frontend/src/` | ✅ |

## Design Coherence

| Decision | Design | Implementation | Status |
|----------|--------|----------------|--------|
| Update semantics | Pessimistic (store → API → local state) | `patchPrizes` waits for response before updating state | ✅ |
| Activity limit | API default 20; frontend requests `limit=10` | `const limit = options?.limit ?? 10` | ✅ |
| Query param order | `group_id=...&event_type=...&limit=10` | `URLSearchParams` produces `limit=10&group_id=...&event_type=...` | ⚠️ **Deviation** — functionally identical |
| `prize_changed` union | Added to frontend `ActivityEvent` | Present in `activity.ts` | ✅ |

## TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Found in apply-progress artifact (ID 75) |
| All tasks have tests | ✅ | 2/2 PR-3 tasks have test files |
| RED confirmed (tests exist) | ✅ | `groups.test.ts` (6 tests) and `activity.test.ts` (4 tests) verified in codebase |
| GREEN confirmed (tests pass) | ✅ | 10/10 new tests pass on execution |
| Triangulation adequate | ✅ | 6 cases for `patchPrizes` + 4 cases for `fetchActivity` |
| Safety Net for modified files | ✅ | 4/4 existing auth tests passing; full suite 17/17 pass |

**TDD Compliance**: 6/6 checks passed

## Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 10 | 2 | vitest + Pinia |
| Integration | 0 | 0 | — |
| E2E | 0 | 0 | — |
| **Total** | **10** | **2** | |

## Assertion Quality

| File | Line | Assertion | Issue | Severity |
|------|------|-----------|-------|----------|
| — | — | — | No tautologies, no ghost loops, no type-only assertions found | ✅ |

**Assertion quality**: ✅ All assertions verify real behavior

## Quality Metrics

**Linter**: ➖ Not available (eslint not configured)
**Type Checker**: ❌ 4 errors in changed consumers, 1 pre-existing

```
src/components/ActivityFeedWidget.vue(92,31): error TS2559: Type '10' has no properties in common with type '{ groupId?: string | number | undefined; eventType?: string | undefined; limit?: number | undefined; }'.
src/components/NavBar.vue(311,33): error TS2559: Type '10' has no properties in common with type '{ groupId?: string | number | undefined; eventType?: string | undefined; limit?: number | undefined; }'.
src/views/DashboardView.vue(98,31): error TS2559: Type '10' has no properties in common with type '{ groupId?: string | number | undefined; eventType?: string | undefined; limit?: number | undefined; }'.
src/views/MatchesView.vue(72,82): error TS2559: Type '10' has no properties in common with type '{ groupId?: string | number | undefined; eventType?: string | undefined; limit?: number | undefined; }'.
```

## Issues

### CRITICAL (1)
1. **TypeScript compilation failure — backward-compat break in `fetchActivity` signature**
   - `fetchActivity` was changed from `fetchActivity(limit?: number)` to `fetchActivity(options?: { groupId?, eventType?, limit? })`.
   - Four existing consumers call `fetchActivity(10)` with a positional number:
     - `src/components/ActivityFeedWidget.vue:92`
     - `src/components/NavBar.vue:311`
     - `src/views/DashboardView.vue:98`
     - `src/views/MatchesView.vue:72`
   - `vue-tsc --noEmit` rejects these with `TS2559`.
   - **Impact**: The build is broken. This is a regression.
   - **Fix**: Make the signature backward-compatible. Accept `number | { groupId?, eventType?, limit? }` and branch on `typeof options === 'number'`. Or update the 4 callers in this PR (but that exceeds the stated scope of "stores ONLY").

### WARNING (2)
1. **Stale tasks artifact**
   - `tasks.md` on the PR-2 branch still shows Phase 2 tasks (`2.1–2.7`) as unchecked.
   - The `apply-progress` Engram artifact confirms they are done.
   - **Recommendation**: Update `tasks.md` when cherry-picking docs so downstream phases see correct state.

2. **Dead code in build artifact**
   - `grep -r setPrizes` found `frontend/dist/assets/groups-CLflGQLs.js` still containing the old `setPrizes` action.
   - This is a stale build output; the source is clean.
   - **Recommendation**: Remove `frontend/dist/` from version control or rebuild before final merge.

### SUGGESTION (1)
1. **Query param order**
   - `URLSearchParams` appends `limit` first, producing `limit=10&group_id=5&event_type=prize_changed` instead of the design's preferred `group_id=5&event_type=prize_changed&limit=10`.
   - Functionally identical; no behavioral impact.
   - **Recommendation**: Minor — reorder `params.append` calls to match design if desired.

## Final Verdict

**FAIL**

All 10 new store tests pass and the stores implement the correct contracts. However, the signature change to `fetchActivity` is **not backward-compatible** and breaks TypeScript compilation in 4 existing consumers. The build is red (`vue-tsc --noEmit` exits with 4 errors). Until this is fixed, PR 3 cannot be safely merged.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Build fails on CI | High | High | Fix CRITICAL #1 before merge |
| Runtime misbehavior after fix | Very Low | Low | If changing signature to union, add test for `fetchActivity(10)` to ensure runtime behavior identical |
| Stale `dist/` artifact causes confusion | Low | Low | Rebuild or remove from repo |

## Next Recommended

1. **Fix CRITICAL #1** — make `fetchActivity` signature backward-compatible:
   ```ts
   async function fetchActivity(
     options?: number | { groupId?: string | number; eventType?: string; limit?: number }
   ): Promise<void> {
     let limit = 10
     let groupId: string | number | undefined
     let eventType: string | undefined
     if (typeof options === 'number') {
       limit = options
     } else if (options) {
       limit = options.limit ?? 10
       groupId = options.groupId
       eventType = options.eventType
     }
     // ... rest of implementation
   }
   ```
   Add a unit test `fetchActivity(10) preserves legacy positional limit`.
2. **Update callers** (optional, if the store's scope is strictly stores-only): the 4 callers are out of scope for PR 3, so the store must be the one that adapts.
3. **Re-run `vitest run`** and **`npx vue-tsc --noEmit`** — confirm zero errors.
4. **Rebuild `frontend/dist/`** or remove it from version control to eliminate stale `setPrizes`.
5. **Write updated report** and save to Engram.
6. **If zero CRITICAL**, recommend: ready to cherry-pick docs and push PR 3.

## Skill Resolution

- `sdd-verify` (executor) — loaded, executed, verified.
- `strict-tdd-verify` — loaded, checked TDD compliance, assertion quality, test layers.

---
*Report persisted to `openspec/changes/editable-prizes-audit/verify-pr3.md` and Engram `sdd/editable-prizes-audit/verify-report`.*
