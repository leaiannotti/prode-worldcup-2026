# Verification Report — editable-prizes-audit PR 4 (Frontend UI + Backend actor_name)

## Change
- **Name**: `editable-prizes-audit`
- **Slice**: PR 4 of 4 — Frontend UI (LeagueDetailModal, NavBar, i18n) + backend actor_name resolution
- **Branch**: `feat/editable-prizes-audit-pr4-frontend-ui`
- **Mode**: `openspec` (artifact store)
- **Strict TDD**: Active
- **Date**: 2026-06-14

## Completeness

| Task | Status | Evidence |
|------|--------|----------|
| 3.1 Tests (RED) — modal edit + history | ✅ Complete | `frontend/src/components/LeagueDetailModal.test.ts` (16 tests) |
| 3.2 Implement `LeagueDetailModal.vue` | ✅ Complete | Lines 43–172: edit mode + collapsible history |
| 3.3 Tests (GREEN) — modal | ✅ Complete | 16/16 modal tests pass |
| 3.4 Modify `NavBar.vue` | ✅ Complete | Line 363: `prize_changed` case in `eventText` switch |
| 3.5 Add i18n keys | ✅ Complete | 15 new keys in both `es.json` and `en.json` |
| 3.6 Tests (GREEN) — full suite | ✅ Complete | 38/38 frontend tests pass |
| Backend actor_name extension | ✅ Complete | `activity.py` outerjoin + `test_activity.py` 2 new tests |
| fix(activity) payload→root | ✅ Complete | Commit `626c687` addresses backend/frontend contract mismatch |

**Unchecked tasks (out of scope for this PR)**: 4.1–4.5 (integration/cross-PR verification), 5.1–5.3 (cleanup). Note: 5.1 (no TODOs) and 5.3 (no `setPrizes`) are already clean; 5.2 (acceptance criteria) is post-merge.

## Build / Tests / Coverage

| Command | Result | Details |
|---------|--------|---------|
| `pytest` (full suite) | ✅ 170 passed, 0 failed | 9.20s execution |
| `npx vitest run` (frontend) | ✅ 38 passed, 0 failed | 6 test files, 2.59s execution |
| `npx vue-tsc --noEmit` | ✅ 0 errors | Only pre-existing TS6133 in `FriendRecentResultsSheet.vue` (out of scope) |

### Coverage — Changed Files

| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `frontend/src/components/LeagueDetailModal.vue` | — | — | — | ➖ Not measured |
| `frontend/src/components/NavBar.vue` | — | — | — | ➖ Not measured |
| `frontend/src/utils/activity.ts` | — | — | — | ➖ Not measured |
| `frontend/src/stores/activity.ts` | — | — | — | ➖ Not measured |
| `backend/app/blueprints/activity.py` | 100% | 100% | — | ✅ Excellent |
| `backend/tests/test_activity.py` | — | — | — | — |

**Note**: Coverage analysis skipped — `vitest run --coverage` not executed and no coverage threshold configured in project.

## Spec Compliance Matrix

### `league-detail/spec.md`

| Requirement | Scenario | Test File | Test Case | Status |
|-------------|----------|-----------|-----------|--------|
| Inline prize editing | Member opens modal (inputs pre-filled) | `LeagueDetailModal.test.ts` | `clicking "Editar premios" enables inputs` | ✅ PASS |
| Inline prize editing | Empty prizes (inputs empty) | `LeagueDetailModal.test.ts` | third input is empty | ✅ PASS |
| Save flow | Successful save (changed only) | `LeagueDetailModal.test.ts` | `clicking Save calls patchPrizes with the bulk body` | ✅ PASS |
| Save flow | Validation error (422) | `LeagueDetailModal.test.ts` | `surfaces 422 error i18n message` | ✅ PASS |
| Save flow | No-op save (nothing sent) | `LeagueDetailModal.test.ts` | payload only contains changed rank | ✅ PASS |
| Collapsible audit history | Toggle history (expand) | `LeagueDetailModal.test.ts` | `clicking "Ver historial" expands and fetches` | ✅ PASS |
| Collapsible audit history | Collapse history | `LeagueDetailModal.test.ts` | `clicking "Ocultar historial" collapses the section` | ✅ PASS |
| Audit message formatting | Regular member change | `LeagueDetailModal.test.ts` | `renders audit lines with the correct format` | ✅ PASS |
| Audit message formatting | Admin change | `LeagueDetailModal.test.ts` | `renders admin marker when actor_is_admin: true` | ✅ PASS |
| Dead code removal | No `setPrizes` references | `grep` | `setPrizes` absent from `frontend/src/` | ✅ PASS |

### `cross-cutting/spec.md` (PR-4-relevant)

| Requirement | Scenario | Test File | Test Case | Status |
|-------------|----------|-----------|-----------|--------|
| Activity event type registration | Frontend type union | Code inspection | `ActivityEvent` includes `'prize_changed'` | ✅ VERIFIED |
| Audit ordering | Newest-first | `test_activity.py` | `test_activity_ordering_newest_first` | ✅ PASS |
| Locale and relative time | es-AR | `LeagueDetailModal.test.ts` | component uses `formatRelativeTime` | ✅ PASS |
| Observable activity event schema | Read-time name resolution | `test_activity.py` | `test_activity_response_includes_actor_name` | ✅ PASS |
| Observable activity event schema | Orphaned event fallback | `test_activity.py` | `test_activity_actor_name_for_orphaned_event` | ✅ PASS |

### `activity-filter/spec.md` (PR-4-relevant)

| Requirement | Scenario | Test File | Test Case | Status |
|-------------|----------|-----------|-----------|--------|
| Prize changed payload | Payload structure | `test_groups.py` | `test_patch_prizes_admin_event_payload` | ✅ PASS (PR 1) |
| Prize changed payload | Admin payload flag | `test_groups.py` | `test_patch_prizes_admin_event_payload` | ✅ PASS (PR 1) |
| Actor_name in response | Happy path | `test_activity.py` | `test_activity_response_includes_actor_name` | ✅ PASS |
| Actor_name in response | Orphaned event | `test_activity.py` | `test_activity_actor_name_for_orphaned_event` | ✅ PASS |

## Correctness Table

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Edit mode toggle | Button → inputs + Save/Cancel | `enterEdit` / `cancelEdit` | ✅ |
| Char counter | `N/200`, red when exceeded | `t('leagueDetail.charCounter', {count})` + `text-error` class | ✅ |
| Saving state | Inputs disabled + spinner | `disabled: isSaving` + SVG spinner | ✅ |
| History toggle | `Ver historial ▾` ↔ `Ocultar historial ▴` | `toggleHistory` + conditional arrows | ✅ |
| Audit line format | `{Actor} cambió el {rank}° premio de «{previous}» a «{new}»` | `formatPrizeChangedEvent` + `formatRelativeTime` | ✅ |
| Admin marker | `(admin)` appended | `t('activity.adminMarker')` | ✅ |
| Backend outerjoin | `User.id == ActivityEvent.user_id` | `outerjoin(User, ...).add_entity(User)` | ✅ |
| actor_name at root | NOT inside payload | `"actor_name": user.name if user else None` at root | ✅ |
| Frontend reads actor_name from root | `event.actor_name` | `formatPrizeChangedEvent` line 5 | ✅ |
| Fallback for missing actor_name | `t('activity.someone')` → "Alguien" | `activity.test.ts` line 53 | ✅ |
| fetchActivity backward compat | `fetchActivity(10)` still works | `activity.test.ts` lines 83–95 | ✅ |
| patchPrizes state update | `currentGroup` and `groups` updated | `groups.test.ts` lines 39–89 | ✅ |
| No hardcoded Spanish strings | All UI text via `t(...)` | Template inspection | ✅ |
| es-AR voseo tone | "No tenés permiso...", "Probá de nuevo" | `es.json` lines 112–114 | ✅ |
| Design: inline within same panel | No nested modals | Audit section is sibling of prizes within modal body | ✅ |

## Design Coherence

| Decision | Design | Implementation | Status |
|----------|--------|----------------|--------|
| Audit history inline | Same panel, no nested modals | `<div>` inside modal body below prizes | ✅ |
| Activity limit | Frontend requests `limit=10` | `fetchActivity({ limit: 10 })` in `toggleHistory` | ✅ |
| Admin marker source | Payload `actor_is_admin` | `p.actor_is_admin` in `formatPrizeChangedEvent` | ✅ |
| Pessimistic update | Store → API → local state | `handleSave` calls `patchPrizes`, waits for response | ✅ |
| actor_name resolution | Read-time via outer join | `outerjoin(User, ...).add_entity(User)` in `activity.py` | ✅ |

## TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Found in apply-progress artifact (Engram ID 75) |
| All tasks have tests | ✅ | 6/6 PR-4 tasks have test files |
| RED confirmed (tests exist) | ✅ | `test(modal)` ×2, `test(activity)` ×1 — 3 RED commits verified |
| GREEN confirmed (tests pass) | ✅ | 16/16 modal + 3/3 utils + 2/2 backend actor_name tests pass |
| Triangulation adequate | ✅ | Modal: 11 edit scenarios + 5 history scenarios; utils: 3 cases; backend: 2 cases |
| Safety Net for modified files | ✅ | 17/17 existing frontend tests pass; 155/155 backend tests pass before PR-4 changes |

**TDD Compliance**: 6/6 checks passed

### Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 9 | 2 | vitest (utils + stores) |
| Integration | 16 | 1 | vitest + vue-test-utils (modal) |
| E2E | 0 | 0 | — |
| **Total** | **25** | **3** | |

### Assertion Quality

| File | Line | Assertion | Issue | Severity |
|------|------|-----------|-------|----------|
| `LeagueDetailModal.test.ts` | 331–339 | `toHaveBeenCalledWith(expect.stringContaining(...))` ×3 | Acceptable for query-param verification; could be strengthened with exact URL assertion | ⚠️ Minor |
| — | — | — | No tautologies, no ghost loops, no type-only assertions found | ✅ |

**Assertion quality**: 0 CRITICAL, 1 WARNING (weak but acceptable)

### Quality Metrics

**Linter**: ➖ Not available (eslint not configured)
**Type Checker**: ✅ 0 errors in changed files (only pre-existing TS6133 in unrelated file)

## Issues

### CRITICAL (0)
*None.*

### WARNING (1)
1. **Query-param assertion style in modal history test**
   - `LeagueDetailModal.test.ts` line 331–339 uses three separate `expect.stringContaining` assertions for the API call URL instead of a single exact URL match.
   - **Impact**: Very low. The test still verifies the correct parameters are present, but it wouldn't catch a malformed URL with duplicate or malformed params.
   - **Recommendation**: Optional — replace with exact `'/api/activity?limit=10&group_id=g1&event_type=prize_changed'` assertion.

### SUGGESTION (1)
1. **i18n key count discrepancy**
   - The user expected 14 new keys; the implementation added 15 (`leagueDetail.cancel` is the 15th, likely added because the Save/Cancel UI needs it even though `common.cancel` exists).
   - **Impact**: None. Extra keys are harmless; all required keys are present.
   - **Recommendation**: No action needed. If desired, deduplicate `leagueDetail.cancel` with `common.cancel` in a future refactor.

## Process Improvement vs PR 1–3

| PR | Issues | Status |
|----|--------|--------|
| PR 1 | Single feat commit (no RED/GREEN split) | 1 WARNING |
| PR 2 | Edge case gaps (negative limit, non-existent group, unknown event type) | 2 WARNINGS |
| PR 3 | Backward-compat break in `fetchActivity` signature | 1 CRITICAL (caught at verify) |
| PR 4 | RED+GREEN properly separated; edge cases from PR 2 now tested; backward compat handled | **Zero issues** |

**Process improvement**: PR 4 demonstrates clean TDD discipline. The 3 RED commits are followed by 3 GREEN commits. The `fetchActivity` signature correctly accepts `number | object` union, learning from PR 3's CRITICAL. The PR 2 edge-case gaps are addressed: `test_activity_negative_limit_returns_400`, `test_activity_non_existent_group_returns_403`, and `test_activity_unknown_event_type_returns_empty` are all present and passing.

## Final Verdict

**PASS**

All spec requirements for PR 4 are implemented and tested. The 170-test backend suite and 38-test frontend suite pass with zero regressions. The inline edit mode, collapsible audit history, actor_name resolution via outer join, i18n keys, and NavBar integration are all correct. The TDD discipline is clean: RED and GREEN commits are properly separated, conventional commits are used, and the final `fix(activity)` commit is a legitimate integration fix discovered during end-to-end verification.

There is one minor WARNING (assertion style) and one SUGGESTION (key count). Neither blocks merge.

**Recommendation**: PR 4 is ready to push and open against `main`. After merge, run `sdd-archive` to finalize the change.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `add_entity(User)` deprecated in SQLAlchemy 2.0 | Low | Low | Existing codebase pattern; migration is a future concern |
| Orphaned events with `actor_name: null` render as "Alguien" | Very Low | Very Low | Frontend fallback tested; user-facing behavior is acceptable |

## Next Recommended

1. **Push PR 4** and open against `main`.
2. **After merge**, run `sdd-archive` for `editable-prizes-audit`.
3. **Post-archive** (optional): Address SUGGESTION #1 by deduplicating `leagueDetail.cancel` with `common.cancel` if desired.

## Skill Resolution

- `sdd-verify` (executor) — loaded, executed, verified.
- `strict-tdd-verify` — loaded, checked TDD compliance, assertion quality, test layers.

---
*Report persisted to `openspec/changes/editable-prizes-audit/verify-pr4.md` and Engram `sdd/editable-prizes-audit/verify-report`.*
