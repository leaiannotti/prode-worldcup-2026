# Verification Report — editable-prizes-audit PR 1 (Backend PATCH)

## Change
- **Name**: `editable-prizes-audit`
- **Slice**: PR 1 of 4 — Backend PATCH endpoint + schema + auth + per-rank diff + event emission
- **Branch**: `feat/editable-prizes-audit-pr1-backend-patch`
- **Mode**: `openspec` (artifact store)
- **Strict TDD**: Active
- **Date**: 2026-06-13

## Completeness

| Task | Status | Evidence |
|------|--------|----------|
| 1.1 Schema `PatchPrizesRequest` | ✅ Complete | `backend/app/schemas/group.py` lines 46–62 |
| 1.2 Tests (RED) | ✅ Complete | `backend/tests/test_groups.py` `TestPatchPrizes` (9 tests) + schema unit test (1 test) |
| 1.3 PATCH handler | ✅ Complete | `backend/app/blueprints/groups.py` lines 315–405 |
| 1.4 Tests (GREEN) | ✅ Complete | All 10 new tests pass; full suite 154/154 pass |

**Unchecked tasks (out of scope for this PR)**: 1.5–1.8, 2.1–2.7, 3.1–3.6, 4.1–4.5, 5.1–5.3.

## Build / Tests / Coverage

| Command | Result | Details |
|---------|--------|---------|
| `pytest` (full suite) | ✅ 154 passed, 0 failed | 7.41s execution |
| `pytest tests/test_groups.py::TestPatchPrizes` | ✅ 9 passed, 0 failed | 0.53s execution |
| `pytest tests/test_groups.py::TestGroupSchemas::test_patch_prizes_request_schema_trims_and_validates` | ✅ 1 passed, 0 failed | 0.09s execution |

### Coverage — Changed Files

| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `backend/app/schemas/group.py` | 94% | 67% | L29, L58 | ✅ Excellent |
| `backend/app/blueprints/groups.py` | 76% | 18% | L330, L335, L340–341 (PATCH error paths) | ⚠️ Acceptable |
| `backend/tests/test_groups.py` | — | — | — | — |

**Note**: Uncovered lines in `groups.py` are PATCH error paths (404 not-found, 422 empty body, 422 generic exception) not exercised by the current test suite. The happy path and all spec-required error paths (validation, auth) are fully covered.

## Spec Compliance Matrix

### `group-prizes/spec.md`

| Requirement | Scenario | Test File | Test Case | Status |
|-------------|----------|-----------|-----------|--------|
| PATCH endpoint | Member updates one prize | `test_groups.py` | `test_patch_prizes_as_member_returns_200` | ✅ PASS |
| PATCH endpoint | Admin updates without membership | `test_groups.py` | `test_patch_prizes_as_admin_non_member_returns_200` | ✅ PASS |
| Authorization | Non-member non-admin | `test_groups.py` | `test_patch_prizes_as_non_member_returns_403` | ✅ PASS |
| Validation | Prize too long | `test_groups.py` | `test_patch_prizes_too_long_returns_422` | ✅ PASS |
| Validation | Empty after trim | `test_groups.py` | `test_patch_prizes_empty_after_trim_returns_422` | ✅ PASS |
| Validation | Missing key is not an error | `test_groups.py` | `test_patch_prizes_missing_key_ignored` | ✅ PASS |
| No-op detection | All ranks unchanged | `test_groups.py` | `test_patch_prizes_noop_returns_empty_changed` | ✅ PASS |
| Per-rank diff emission | Two prizes change | `test_groups.py` | `test_patch_prizes_two_changes_emits_two_events` | ✅ PASS |
| Per-rank diff emission | Admin payload | `test_groups.py` | `test_patch_prizes_admin_event_payload` | ✅ PASS |
| Atomic persistence | Concurrent edits (last-write-wins) | Code inspection | Single `db.session.commit()` at end of handler | ✅ VERIFIED |

### `cross-cutting/spec.md` (PR-1-relevant only)

| Requirement | Scenario | Test File | Test Case | Status |
|-------------|----------|-----------|-----------|--------|
| Activity event type registration | Backend taxonomy | Code inspection | `event_type` is free string; `"prize_changed"` used in handler | ✅ VERIFIED |
| Audit ordering | Newest-first | Code inspection | `ActivityEvent` has `occurred_at` index; ordering handled in PR 2 | ⏸️ SKIPPED (PR 2 scope) |
| Locale and relative time | es-AR | — | Frontend concern | ⏸️ SKIPPED (PR 3+4 scope) |
| Observable activity event schema | Read-time name resolution | — | Frontend concern | ⏸️ SKIPPED (PR 3+4 scope) |

## Correctness Table

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Endpoint exists | `PATCH /api/groups/:id/prizes` | Present at line 315 | ✅ |
| Body schema | `{ first?, second?, third? }` flat format | `PatchPrizesRequest` with three optional fields | ✅ |
| Partial updates allowed | Only keys present evaluated | `if value is None: continue` | ✅ |
| Validation rules | 1–200 chars, trim, non-empty after trim | `max_length=200` + `mode='after'` validator | ✅ |
| Existing PUT untouched | `PUT /api/groups/:id/prizes` (owner-only) | Unchanged at lines 273–312 | ✅ |
| Auth: member | Member returns 200 | Test passes | ✅ |
| Auth: admin non-member | Admin returns 200 | Test passes | ✅ |
| Auth: non-member non-admin | Returns 403 | Test passes | ✅ |
| No-op: equal value after trim | No write, no event | `if current_prize.description != trimmed:` skips; no events emitted | ✅ |
| No-op: all unchanged | `{ changed: [] }` | Test asserts empty array + zero events | ✅ |
| Per-rank diff | Only changed ranks emit events | `changed` list built only on diff; loop emits per item | ✅ |
| Event payload | `{ rank, previous_value, new_value, actor_is_admin }` | Payload matches exactly | ✅ |
| `actor_is_admin` | True only when admin acted as non-member | `is_admin` flag from `ADMIN_EMAILS` check | ✅ |
| Atomic transaction | Single commit per request | `db.session.commit()` once after all updates + events | ✅ |

## Design Coherence

| Decision | Design | Implementation | Status |
|----------|--------|----------------|--------|
| Validation location | Pydantic `PatchPrizeItem` with `mode='after'` | `PatchPrizesRequest` with `field_validator` on `first`/`second`/`third` | ✅ |
| Auth check | Inline `if not _is_group_member(...) and ...` | Inline at lines 323–326 | ✅ |
| Schema format | Design showed list-based `PatchPrizeItem` | Flat `{ first, second, third }` per spec/task | ✅ **Deviation accepted** — spec wins over design |
| Activity payload | `actor_is_admin` in payload | Present in emitted payload | ✅ |
| Race condition | Last-write-wins documented | Single commit; no optimistic locking | ✅ |

## TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Found in apply-progress artifact |
| All tasks have tests | ✅ | 4/4 PR-1 tasks have test files |
| RED confirmed (tests exist) | ✅ | 10 test methods verified in codebase |
| GREEN confirmed (tests pass) | ✅ | 10/10 pass on execution |
| Triangulation adequate | ⚠️ | 1.1 reported 4 cases but code has 5 (valid, partial, trim, empty, too long). Minor discrepancy. |
| Safety Net for modified files | ✅ | 30/30 existing tests passing before modification; full suite 154/154 |

**TDD Compliance**: 5/6 checks passed

## Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 1 | 1 | pytest |
| Integration | 9 | 1 | pytest + Flask test client |
| E2E | 0 | 0 | — |
| **Total** | **10** | **1** | |

## Assertion Quality

| File | Line | Assertion | Issue | Severity |
|------|------|-----------|-------|----------|
| `test_groups.py` | ~681 | `assert response.status_code == 200` only | `test_patch_prizes_as_admin_non_member_returns_200` does not assert response body or DB state for newly created prize | WARNING |
| — | — | — | No tautologies, no ghost loops, no type-only assertions found | ✅ |

**Assertion quality**: 0 CRITICAL, 1 WARNING (weak assertion on admin test)

## Quality Metrics

**Linter**: ➖ Not available (flake8 not installed)
**Type Checker**: ➖ Not available (mypy not installed)

## Issues

### CRITICAL (0)
*None.*

### WARNING (2)
1. **TDD process gap — single commit instead of RED+GREEN cycle**
   - The applier produced one feat commit (`e1fa32b`) rather than separate RED and GREEN commits per task.
   - **Impact**: Minor process gap; not a behavioral blocker. The tests were written and pass, but the commit history does not demonstrate the TDD cycle.
   - **Recommendation**: Flag for future PRs; enforce `test` + `feat` commit split in PR 2.

2. **Weak assertion in admin test**
   - `test_patch_prizes_as_admin_non_member_returns_200` only asserts status code 200.
   - It exercises the "create new prize when rank does not exist" code path but does not verify the `changed` array or that the prize was actually persisted.
   - **Recommendation**: Add assertions for `data["changed"]` and `GroupPrize.query.filter_by(...)` before merge.

### SUGGESTION (3)
1. **Redundant `.strip()` in PATCH handler**
   - `patch_group_prizes` calls `trimmed = value.strip()` even though the Pydantic `mode='after'` validator already returns a trimmed string.
   - **Recommendation**: Remove the redundant `.strip()` or add a comment explaining the defensive choice.

2. **Missing coverage for PATCH 404 and empty-body 422**
   - Lines 330 (group not found → 404) and 335/340–341 (empty body / generic exception → 422) are uncovered.
   - **Recommendation**: Add tests for `PATCH` on non-existent group and `PATCH` with empty JSON body `{}`.

3. **`emit_event` rollback behavior**
   - `activity_service.py` catches flush exceptions and calls `db.session.rollback()`, which rolls back the caller's pending prize changes too.
   - This is pre-existing behavior, not introduced by PR 1, but the docstring is misleading about "parent transaction is not affected."
   - **Recommendation**: In a future refactor, change `emit_event` to use `savepoint` instead of `rollback()` to protect the parent transaction.

## Final Verdict

**PASS WITH WARNINGS**

All spec requirements for PR 1 are implemented and tested. The 154-test suite passes with zero regressions. The endpoint contract, authorization, validation, no-op detection, per-rank diff emission, and atomic commit are all correct. The flat `{ first, second, third }` schema correctly prioritizes the spec over the design document.

The two WARNINGS are minor:
- A process gap (single commit) that does not affect behavior.
- A weak assertion that should be strengthened before merge.

**Recommendation**: Address WARNING #2 (add assertions to admin test) and optionally SUGGESTION #2 (add 404/empty-body tests), then push PR 1 and open against `main`. PR 1 is ready to merge from a behavioral standpoint.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `emit_event` flush failure rolls back prize changes | Very Low | Medium | Pre-existing; `emit_event` is a simple INSERT that rarely fails. Mitigated by single commit pattern. |
| PATCH 404/empty-body paths untested | Low | Low | Add tests (SUGGESTION #2). |

## Next Recommended

1. **Fix WARNING #2** — strengthen `test_patch_prizes_as_admin_non_member_returns_200` assertions.
2. **Fix SUGGESTION #2** (optional) — add PATCH 404 and empty-body tests.
3. **Push PR 1** and open against `main`.
4. **Begin PR 2** (backend activity filters) — tasks 1.5–1.8.

## Skill Resolution

- `sdd-verify` (executor) — loaded, executed, verified.
- `strict-tdd-verify` — loaded, checked TDD compliance, assertion quality, test layers.

---
*Report persisted to openspec and Engram.*
