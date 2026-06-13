# Verification Report — editable-prizes-audit PR 2 (Backend Activity Filters)

## Change
- **Name**: `editable-prizes-audit`
- **Slice**: PR 2 of 4 — Backend GET `/api/activity` filter extensions ONLY
- **Branch**: `feat/editable-prizes-audit-pr2-activity-filters`
- **Mode**: `openspec` (artifact store)
- **Strict TDD**: Active
- **Date**: 2026-06-13

## Completeness

| Task | Status | Evidence |
|------|--------|----------|
| 1.5 Tests (RED) | ✅ Complete | `backend/tests/test_activity.py` `TestActivityFilters` (11 tests) |
| 1.6 Implementation | ✅ Complete | `backend/app/blueprints/activity.py` lines 22–91 |
| 1.7 Tests (GREEN) | ✅ Complete | All 11 new tests pass; full suite 155/155 pass |
| 1.8 Refactor | ✅ Complete | No refactor needed; code is clean |

**Unchecked tasks (out of scope for this PR)**: 2.1–2.7, 3.1–3.6, 4.1–4.5, 5.1–5.3.

## Build / Tests / Coverage

| Command | Result | Details |
|---------|--------|----------|
| `pytest` (full suite) | ✅ 155 passed, 0 failed | 7.06s execution |
| `pytest tests/test_activity.py` | ✅ 21 passed, 0 failed | 1.03s execution |

### Coverage — Changed Files

| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `backend/app/blueprints/activity.py` | 100% | 100% | — | ✅ Excellent |
| `backend/tests/test_activity.py` | — | — | — | — |

**Note**: The activity endpoint is fully covered by the new and existing tests. All branches (membership gate, limit validation, cursor parsing, group-scoped vs user-scoped query) are exercised.

## Spec Compliance Matrix

### `activity-filter/spec.md`

| Requirement | Scenario | Test File | Test Case | Status |
|-------------|----------|-----------|-----------|--------|
| Group-scoped queries | Member queries group audit | `test_activity.py` | `test_activity_group_id_filter_as_member` | ✅ PASS |
| Group-scoped queries | Non-member denied | `test_activity.py` | `test_activity_group_id_filter_as_non_member_returns_403` | ✅ PASS |
| Group-scoped queries | Admin queries without membership | `test_activity.py` | `test_activity_group_id_filter_as_admin_non_member_returns_200` | ✅ PASS |
| Event type filtering | Filter by prize_changed | `test_activity.py` | `test_activity_event_type_filter` | ✅ PASS |
| Limit parameter | Default limit | `test_activity.py` | `test_activity_default_limit_group_scoped` | ✅ PASS |
| Limit parameter | Custom limit | `test_activity.py` | `test_activity_custom_limit` | ✅ PASS |
| Limit parameter | Maximum limit | `test_activity.py` | `test_activity_limit_max_50` | ✅ PASS |
| Prize changed payload | Payload structure | — | PR 1 scope | ⏸️ SKIPPED |
| Prize changed payload | Admin payload flag | — | PR 1 scope | ⏸️ SKIPPED |

### `cross-cutting/spec.md` (PR-2-relevant only)

| Requirement | Scenario | Test File | Test Case | Status |
|-------------|----------|-----------|-----------|--------|
| Activity event type registration | Backend taxonomy | Code inspection | `"prize_changed"` is free string; no enum restriction | ✅ VERIFIED |
| Audit ordering | Newest-first | `test_activity.py` | `test_activity_ordering_newest_first` | ✅ PASS |
| Locale and relative time | es-AR | — | Frontend concern | ⏸️ SKIPPED (PR 3+4 scope) |
| Observable activity event schema | Read-time name resolution | — | Frontend concern | ⏸️ SKIPPED (PR 3+4 scope) |

## Correctness Table

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Default behavior preserved | No new params → limit 20, user-scoped | `test_activity_default_behavior_preserved` asserts 20 events | ✅ |
| group_id filter | Returns only events for that group | `test_activity_group_id_filter_as_member` asserts all events have group_id | ✅ |
| group_id returns all users | Member sees events from all group members | `test_activity_group_id_filter_returns_all_users_in_group` asserts 5 events from 2 users | ✅ |
| event_type filter | Returns only matching event type | `test_activity_event_type_filter` asserts all events are `prize_changed` | ✅ |
| Combined filters | AND semantics | `test_activity_combined_filters` asserts group_id + event_type + limit together | ✅ |
| Ordering | Newest-first | `test_activity_ordering_newest_first` asserts seq 2, 1, 0 | ✅ |
| Limit default (group-scoped) | 10 when group_id provided | `test_activity_default_limit_group_scoped` asserts 10 events | ✅ |
| Limit default (user-scoped) | 20 when no group_id | `test_activity_default_behavior_preserved` asserts 20 events | ✅ |
| Limit cap | Max 50 | `test_activity_limit_max_50` asserts 50 events from 60 seed | ✅ |
| Membership gate | Non-member non-admin → 403 | `test_activity_group_id_filter_as_non_member_returns_403` asserts 403 + error | ✅ |
| Membership gate | Admin non-member → 200 | `test_activity_group_id_filter_as_admin_non_member_returns_200` asserts 200 | ✅ |
| Membership gate | Member → 200 | `test_activity_group_id_filter_as_member` asserts 200 | ✅ |

## Design Coherence

| Decision | Design | Implementation | Status |
|----------|--------|----------------|--------|
| Activity limit | API keeps default 20; frontend requests limit=10 | Group_id provided → default 10; no group_id → default 20 | ⚠️ **Deviation** — Spec overrides design |
| Membership gate | Inline check | Inline at lines 31–37 | ✅ |
| Auth check | Member OR admin | `is_member` OR `is_admin` | ✅ |
| Query scope | Group-scoped ignores user_id | `if group_id: query = ...filter_by(group_id=...)` | ✅ |
| Ordering | Newest-first | `order_by(ActivityEvent.occurred_at.desc())` | ✅ |

**Note on deviation**: The design document says "API keeps default 20; frontend requests limit=10". The spec says "Default SHALL be 10" for group-scoped queries. The implementation correctly prioritizes the spec over the design, setting default 10 when `group_id` is provided and preserving default 20 for user-scoped queries. This is the correct behavior and prevents a breaking change for existing clients.

## TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Found in apply-progress artifact |
| All tasks have tests | ✅ | 4/4 PR-2 tasks have test files |
| RED confirmed (tests exist) | ✅ | 11 test methods verified in codebase |
| GREEN confirmed (tests pass) | ✅ | 11/11 pass on execution |
| Triangulation adequate | ✅ | 11 cases covering default, member, all-users, non-member 403, admin 200, event_type, combined, default limit 10, custom limit, max 50, ordering |
| Safety Net for modified files | ✅ | 10/10 existing tests passing before modification; full suite 155/155 |

**TDD Compliance**: 6/6 checks passed

## Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 0 | 0 | — |
| Integration | 11 | 1 | pytest + Flask test client |
| E2E | 0 | 0 | — |
| **Total** | **11** | **1** | |

## Assertion Quality

| File | Line | Assertion | Issue | Severity |
|------|------|-----------|-------|----------|
| — | — | — | No tautologies, no ghost loops, no type-only assertions, no smoke-only tests found | ✅ |

**Assertion quality**: ✅ All assertions verify real behavior

## Quality Metrics

**Linter**: ➖ Not available (flake8 not installed)
**Type Checker**: ➖ Not available (mypy not installed)

## Issues

### CRITICAL (1)
1. **Missing spec files on current branch**
   - The `openspec/changes/editable-prizes-audit/specs/` directory exists but is empty on the current branch (`feat/editable-prizes-audit-pr2-activity-filters`).
   - The spec files (`activity-filter/spec.md`, `cross-cutting/spec.md`, `group-prizes/spec.md`, `league-detail/spec.md`) and other SDD artifacts (`design.md`, `verify-pr1.md`) were added in commit `62ef077` on a different branch but are not present on the current branch.
   - **Impact**: The openspec artifact store is incomplete. Downstream phases (archive, future PRs) cannot reference the spec from the filesystem.
   - **Recommendation**: Cherry-pick or merge commit `62ef077` into the current branch, or create the files from the Engram memory. The spec content is available in git history.

### WARNING (2)
1. **Edge case coverage gaps**
   - **Negative limit**: The docstring for `test_activity_invalid_limit_returns_400` says "limit=0 or negative → 400" but only tests `limit=0`. The code correctly handles negative values (line 44: `if limit <= 0`), but this path is not exercised by a test.
   - **Non-existent group_id**: The code returns 403 for non-existent groups (membership check fails), but no test explicitly verifies this.
   - **Unknown event_type**: The code returns an empty array for unknown event types, but no test explicitly verifies this.
   - **Impact**: Minor coverage gaps; code handles them correctly. Risk is low.
   - **Recommendation**: Add tests for `limit=-1`, `group_id=99999` (non-existent), and `event_type=unknown_type` to close the gaps.

2. **Design deviation — limit default**
   - The implementation sets default limit=10 when `group_id` is provided, overriding the design document's recommendation of "API keeps default 20; frontend requests limit=10".
   - **Impact**: None. The spec correctly takes precedence over the design. The deviation is documented and justified.
   - **Recommendation**: Update `design.md` to reflect the actual implementation (spec wins).

### SUGGESTION (3)
1. **Non-numeric group_id handling**
   - The code treats `group_id` as a raw string and passes it to the DB query. A non-numeric `group_id` (e.g., `abc`) will result in a SQL query that finds no membership and returns 403. This is correct behavior, but a more explicit validation could return 400 instead of 403.
   - **Recommendation**: Consider adding a validation check for non-numeric `group_id` to return 400 with `error: "invalid_group_id"` for better API ergonomics.

2. **Missing `next_cursor` test for group-scoped queries**
   - The existing tests verify pagination and cursor for user-scoped queries, but no new test verifies that `next_cursor` works correctly with group-scoped filters.
   - **Recommendation**: Add a test for group-scoped pagination (e.g., 15 events with limit=10 → 10 events + non-null cursor).

3. **Commit hygiene — docs commit is third**
   - The commit sequence is RED → GREEN → docs. The docs commit updates the task file. This is acceptable, but the ideal TDD cycle is RED → GREEN → REFACTOR (if needed) with the docs commit as a separate chore.
   - **Recommendation**: No action needed; the commit sequence is clean and conventional.

## Final Verdict

**PASS WITH WARNINGS**

All spec requirements for PR 2 are implemented and tested. The 155-test suite passes with zero regressions. The endpoint contract, filter semantics, membership gate, limit behavior, and ordering are all correct. The RED+GREEN commit separation is present and clean, demonstrating TDD discipline.

The single CRITICAL is an artifact store issue (missing spec files on the current branch), not a behavioral issue. The implementation matches the spec available in git history.

The two WARNINGS are minor:
- Edge case coverage gaps (negative limit, non-existent group, unknown event type) that are handled correctly by the code but not explicitly tested.
- A design deviation that correctly prioritizes the spec over the design document.

**Recommendation**: Address CRITICAL #1 by ensuring spec files are present on the branch (cherry-pick `62ef077` or re-create files). Address WARNING #1 by adding the three edge-case tests. Then push PR 2 and open against `main`. PR 2 is ready to merge from a behavioral standpoint.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Missing spec files break downstream SDD phases | Medium | Medium | Cherry-pick or re-create spec files from git history / Engram |
| Edge case gaps allow regressions | Low | Low | Add the three missing edge-case tests |

## Next Recommended

1. **Fix CRITICAL #1** — Ensure `openspec/changes/editable-prizes-audit/specs/` and `design.md` are present on the branch.
2. **Fix WARNING #1** — Add tests for `limit=-1`, non-existent `group_id`, and unknown `event_type`.
3. **Push PR 2** and open against `main`.
4. **Begin PR 3** (frontend stores) — tasks 2.1–2.7.

## Skill Resolution

- `sdd-verify` (executor) — loaded, executed, verified.
- `strict-tdd-verify` — loaded, checked TDD compliance, assertion quality, test layers.

---
*Report persisted to openspec and Engram.*
