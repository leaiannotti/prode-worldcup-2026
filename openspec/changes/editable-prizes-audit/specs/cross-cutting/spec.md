# Cross-cutting Concerns Specification

## Purpose

Defines shared behavior across the editable prizes and audit history feature.

## Requirements

### Requirement: Activity event type registration

The `prize_changed` event type SHALL be valid in both backend taxonomy and frontend `ActivityEvent` union.

#### Scenario: Backend taxonomy

- GIVEN the backend event type taxonomy
- THEN `prize_changed` is a recognized event type

#### Scenario: Frontend type union

- GIVEN the frontend `ActivityEvent` interface
- THEN `event_type` includes `'prize_changed'`

### Requirement: Audit ordering

Group-scoped activity events SHALL be ordered by `occurred_at` descending (newest first).

#### Scenario: Multiple changes

- GIVEN three `prize_changed` events at T1 < T2 < T3
- WHEN `GET /api/activity?group_id=G&event_type=prize_changed` is called
- THEN the response order is T3, T2, T1

### Requirement: Locale and relative time

The frontend SHALL render relative timestamps in Argentine Spanish (es-AR).

#### Scenario: Recent change

- GIVEN a `prize_changed` event occurred 2 days ago
- WHEN the audit line is rendered
- THEN the timestamp reads "hace 2 días"

#### Scenario: Very recent change

- GIVEN a `prize_changed` event occurred 5 minutes ago
- WHEN the audit line is rendered
- THEN the timestamp reads "hace 5 minutos"

### Requirement: Observable activity event schema

The activity event JSON representation visible to consumers SHALL contain `id`, `event_type`, `group_id`, `payload`, `occurred_at`, and the actor's display name resolved at read time.

#### Scenario: Read-time name resolution

- GIVEN a `prize_changed` event stored with `user_id` only
- WHEN the frontend renders the audit line
- THEN the actor's current display name is shown (not stored in payload)
