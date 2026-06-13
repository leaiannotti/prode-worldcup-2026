# Backend Specification

## Purpose
API contract and permission rules for retrieving a group member's recent finished-match predictions.

## Requirements

### Requirement: Endpoint Contract

The backend MUST expose `GET /api/groups/<group_id>/members/<user_id>/recent-history` with an optional `limit` query parameter defaulting to `5` and capped at `5`. The response MUST be a JSON array where each item contains `match_teams`, `actual_result`, `prediction`, `points`, and `score_type`.

#### Scenario: Happy path with default limit

- GIVEN a group with at least 5 finished matches and a member with predictions for all
- WHEN the requester (another group member) calls the endpoint without a limit
- THEN the response MUST contain exactly 5 items
- AND each item MUST include the required fields with correct values

#### Scenario: Custom limit within cap

- GIVEN at least 3 finished matches exist
- WHEN the requester calls `?limit=3`
- THEN the response MUST contain exactly 3 items

### Requirement: Permission Check

The endpoint MUST verify that the requester and target user are both members of the requested group. If the requester is not in the group, the endpoint MUST return `403 Forbidden`. If the target user is not in the group, the endpoint MUST return `404 Not Found`.

#### Scenario: Requester not in same group

- GIVEN the requester is NOT a member of the requested group
- WHEN the requester calls the endpoint
- THEN the response MUST return `403 Forbidden`

#### Scenario: Requester is the same as target

- GIVEN the requester is the target user and both are group members
- WHEN the requester calls the endpoint
- THEN the response MUST return `200 OK` with the user's recent history

### Requirement: Match Filtering

The endpoint MUST include only matches with `status = "finished"`, ordered by `kickoff_utc` descending globally. Matches with any other status MUST be excluded.

#### Scenario: Only finished matches included

- GIVEN a group with 3 finished matches and 2 scheduled matches
- WHEN the requester calls the endpoint
- THEN the response MUST contain only the 3 finished matches
- AND the scheduled matches MUST NOT appear

#### Scenario: Fewer than 5 finished matches exist

- GIVEN only 2 finished matches exist globally
- WHEN the requester calls the endpoint with the default limit
- THEN the response MUST contain exactly 2 items

### Requirement: Missing Prediction Handling

For finished matches where the target user has no prediction, the endpoint MUST include the match with `prediction: null`, `points: 0`, and `score_type: null`.

#### Scenario: User did not predict a match

- GIVEN a finished match exists in the group
- AND the target user has no prediction for that match
- WHEN the requester calls the endpoint
- THEN the response MUST include the match
- AND the `prediction` field MUST be `null`
- AND the `points` field MUST be `0`
- AND the `score_type` field MUST be `null`
