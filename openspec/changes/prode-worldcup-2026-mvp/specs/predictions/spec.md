# Predictions Specification

## Purpose

Allows group members to submit and update score predictions per match. Predictions are scoped to a `(user, match, group)` triple. Submission is blocked server-side after the match's `prediction_deadline_at`.

## Requirements

### Requirement: Submit Prediction

The system MUST allow a group member to submit a predicted home and away score for a match. If the user already has a prediction for that `(user, match, group)` triple, the system MUST update it (upsert). Both scores MUST be non-negative integers.

#### Scenario: First-time submission

- GIVEN user U is a member of group G and match M is SCHEDULED with deadline in the future
- WHEN they call `POST /api/groups/{group_id}/predictions` with `{"match_id": M, "home_score": 2, "away_score": 1}`
- THEN a prediction record is created and HTTP 201 is returned

#### Scenario: Update existing prediction

- GIVEN user U already has a prediction for `(U, M, G)` and the deadline has not passed
- WHEN they call `POST /api/groups/{group_id}/predictions` with new scores
- THEN the existing prediction is updated and HTTP 200 is returned

#### Scenario: Negative score rejected

- GIVEN a user submits `{"match_id": M, "home_score": -1, "away_score": 0}`
- WHEN the request is validated
- THEN the system returns HTTP 422 `{"errors": {"home_score": "must be >= 0"}}`

---

### Requirement: Prediction Freeze

The system MUST reject prediction submissions received after the match's `prediction_deadline_at` (server clock). The client SHOULD NOT be trusted to enforce this.

#### Scenario: Submission after deadline

- GIVEN match M has `prediction_deadline_at` in the past (server time)
- WHEN a user attempts to submit or update a prediction for M
- THEN the system returns HTTP 423 `{"error": "prediction_locked", "deadline": "<ISO datetime>"}`

#### Scenario: Submission exactly at deadline

- GIVEN the server clock equals `prediction_deadline_at` to the second
- WHEN a submission arrives
- THEN the system treats this as expired and returns HTTP 423

---

### Requirement: View Group Predictions

The system MUST allow group members to view all predictions for a given match within their group. Predictions for matches that have not yet reached deadline MUST NOT reveal other members' predictions (scores hidden until deadline).

#### Scenario: Pre-deadline — own prediction visible, others hidden

- GIVEN match M's deadline has not passed
- WHEN user U calls `GET /api/groups/{group_id}/matches/{match_id}/predictions`
- THEN U's own prediction is returned in full; other members' predictions show only `{user_id, name}` with scores as `null`

#### Scenario: Post-deadline — all predictions revealed

- GIVEN match M's `prediction_deadline_at` has passed
- WHEN any member calls the predictions endpoint
- THEN all members' predictions are returned with actual scores visible

#### Scenario: Non-member access denied

- GIVEN user B is not in group G
- WHEN they call `GET /api/groups/{group_id}/matches/{match_id}/predictions`
- THEN the system returns HTTP 403

---

## API Contract

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/groups/{group_id}/predictions` | JWT (member) | Submit or update prediction |
| GET | `/api/groups/{group_id}/matches/{match_id}/predictions` | JWT (member) | List group predictions for match |
| GET | `/api/groups/{group_id}/predictions` | JWT (member) | List caller's predictions in group |

### Prediction Request Body

```json
{
  "match_id": "uuid",
  "home_score": 2,
  "away_score": 1
}
```

## Data Constraints

- `predictions`: UNIQUE on `(user_id, match_id, group_id)`
- `predictions.home_score`: INTEGER, NOT NULL, CHECK >= 0
- `predictions.away_score`: INTEGER, NOT NULL, CHECK >= 0
- `predictions.submitted_at`: server UTC timestamp, NOT NULL
- Freeze check MUST use server-side `NOW()`, never client-provided time
