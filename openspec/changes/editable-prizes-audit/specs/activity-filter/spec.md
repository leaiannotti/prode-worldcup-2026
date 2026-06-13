# Activity Filter Specification

## Purpose

Defines extended query capabilities for the activity feed, including group-scoped filtering, event-type filtering, and membership validation.

## Requirements

### Requirement: Group-scoped queries

The system SHALL support `group_id` as an optional query parameter on `GET /api/activity`. When provided, the endpoint returns events for that group regardless of `user_id`.

#### Scenario: Member queries group audit

- GIVEN user U is a member of group G
- WHEN U sends `GET /api/activity?group_id=G&event_type=prize_changed&limit=10`
- THEN response contains up to 10 `prize_changed` events for G, newest first

#### Scenario: Non-member denied

- GIVEN user U is not a member of group G and is not admin
- WHEN U sends `GET /api/activity?group_id=G`
- THEN response is `403` with `{ error: "forbidden" }`

#### Scenario: Admin queries without membership

- GIVEN admin A is not a member of group G
- WHEN A sends `GET /api/activity?group_id=G`
- THEN the request succeeds

### Requirement: Event type filtering

The system SHALL support `event_type` as an optional query parameter on `GET /api/activity`.

#### Scenario: Filter by prize_changed

- GIVEN a member of group G
- WHEN they send `GET /api/activity?group_id=G&event_type=prize_changed`
- THEN only `prize_changed` events for G are returned

### Requirement: Limit parameter

The system SHALL support `limit` on group-scoped queries. Default SHALL be 10; maximum SHALL be 50.

#### Scenario: Default limit

- GIVEN a member of group G with many prize changes
- WHEN they send `GET /api/activity?group_id=G&event_type=prize_changed`
- THEN exactly 10 events are returned

#### Scenario: Custom limit

- GIVEN a member sends `GET /api/activity?group_id=G&limit=5`
- THEN exactly 5 events are returned

### Requirement: Prize changed payload schema

A `prize_changed` event payload MUST contain `rank` (1–3), `previous_value` (string), `new_value` (string), and `actor_is_admin` (boolean).

#### Scenario: Payload structure

- GIVEN a `prize_changed` event was emitted for rank 1
- WHEN the event is retrieved
- THEN payload is `{ rank: 1, previous_value: "Pizza", new_value: "Asado", actor_is_admin: false }`

#### Scenario: Admin payload flag

- GIVEN a system admin changed a prize
- WHEN the event is retrieved
- THEN payload contains `actor_is_admin: true`
