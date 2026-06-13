# Group Prizes Specification

## Purpose

Defines bulk prize updates via PATCH, including authorization, validation, no-op detection, and per-rank activity event emission.

## Requirements

### Requirement: PATCH endpoint

The system SHALL expose `PATCH /api/groups/:id/prizes` with body `{ first?: string, second?: string, third?: string }`. Only keys present in the body are evaluated for change.

#### Scenario: Member updates one prize

- GIVEN group G has 1st prize "Pizza"
- WHEN member sends `PATCH /api/groups/G/prizes` with `{ first: "Asado" }`
- THEN response is `200` with `{ changed: [{ rank: 1, previous: "Pizza", new: "Asado" }] }`
- AND a `prize_changed` event is emitted for rank 1

#### Scenario: Admin updates without membership

- GIVEN system admin A is not a member of group G
- WHEN A sends `PATCH /api/groups/G/prizes`
- THEN the request succeeds with `200`

### Requirement: Authorization

The system MUST reject with `403` when the caller is neither a group member nor a system admin.

#### Scenario: Non-member non-admin

- GIVEN user U is neither member nor admin
- WHEN U sends `PATCH /api/groups/G/prizes`
- THEN response is `403` with `{ error: "forbidden" }`

### Requirement: Validation

Each provided prize MUST be 1–200 characters after trimming. The entire request MUST be rejected with `422` if any prize fails.

#### Scenario: Prize too long

- GIVEN a member sends `PATCH` with `{ first: "x" * 201 }`
- THEN response is `422` with `{ error: "invalid_request" }`

#### Scenario: Empty after trim

- GIVEN a member sends `PATCH` with `{ first: "   " }`
- THEN response is `422` with `{ error: "invalid_request" }`

#### Scenario: Missing key is not an error

- GIVEN a member sends `PATCH` with `{ first: "Asado" }` (no second or third)
- THEN only the first prize is evaluated; missing ranks are ignored

### Requirement: No-op detection

The system SHALL skip a rank whose trimmed value equals the current stored value. No write and no event SHALL occur for that rank.

#### Scenario: All ranks unchanged

- GIVEN group prizes are ["A", "B", "C"]
- WHEN member sends `PATCH` with `{ first: "A", second: "B", third: "C" }`
- THEN response is `200` with `{ changed: [] }`
- AND no `prize_changed` events are emitted

### Requirement: Per-rank diff emission

For each effectively changed rank, the system SHALL emit one `prize_changed` activity event with payload `{ rank, previous_value, new_value, actor_is_admin }`.

#### Scenario: Two prizes change

- GIVEN group prizes are ["A", "B", "C"]
- WHEN member sends `PATCH` with `{ first: "X", second: "Y" }`
- THEN two `prize_changed` events are emitted: rank 1 and rank 2

### Requirement: Atomic persistence

All valid prize updates for a single request SHALL be processed in one database transaction.

#### Scenario: Concurrent edits

- GIVEN two members edit the same prize simultaneously
- WHEN both PATCH requests are processed
- THEN last-write-wins applies and both changes appear in the audit trail
