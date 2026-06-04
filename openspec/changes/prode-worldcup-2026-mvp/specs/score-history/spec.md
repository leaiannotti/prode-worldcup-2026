# Score History Specification

## Purpose

Provides each user with a per-group view of their prediction history: the prediction they made, the actual match result, and the points earned. This is a read-only view built from `predictions` and `prediction_scores`.

## Requirements

### Requirement: Per-User Score History

The system MUST return a list of all scored predictions for a user within a given group. Each entry MUST include the match details, the user's predicted score, the actual result, and the points earned. Unscored predictions (match not yet finished) MUST also be returned, with `points` and `actual_result` as `null`.

#### Scenario: Mix of scored and unscored predictions

- GIVEN user U has 3 predictions in group G: 2 scored (matches finished), 1 pending (match not yet played)
- WHEN U calls `GET /api/groups/{group_id}/me/history`
- THEN all 3 predictions are returned; the 2 finished matches include `points` and `actual_result`, the pending one shows `points: null, actual_result: null`

#### Scenario: No predictions made

- GIVEN user U has joined group G but made no predictions
- WHEN U calls `GET /api/groups/{group_id}/me/history`
- THEN an empty list is returned with HTTP 200

#### Scenario: Non-member access denied

- GIVEN user B is not in group G
- WHEN they call `GET /api/groups/{group_id}/me/history`
- THEN the system returns HTTP 403

---

### Requirement: History Immutability

Score history entries are derived from immutable `prediction_scores` records. The history endpoint MUST reflect recalculated scores when a result is corrected. Historical entries MUST NOT be manually editable via API.

#### Scenario: Corrected result reflected in history

- GIVEN user U earned 1 point for match M (outcome correct, score wrong)
- WHEN the result is corrected and recalculation runs
- THEN `GET .../me/history` for match M now reflects the updated `points` value

#### Scenario: No write endpoint for history

- GIVEN the system is running
- WHEN any client attempts to POST/PUT/DELETE to the history endpoint
- THEN the system returns HTTP 405 Method Not Allowed

---

### Requirement: History Ordering

The system MUST return score history entries ordered by `kickoff_at` ASC by default.

#### Scenario: Chronological order

- GIVEN user U has predictions for matches on different dates
- WHEN the history is retrieved
- THEN entries are returned in ascending `kickoff_at` order

---

## API Contract

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/groups/{group_id}/me/history` | JWT (member) | User's prediction history in group |

### History Response Shape

```json
{
  "group_id": "uuid",
  "user_id": "uuid",
  "history": [
    {
      "match": {
        "id": "uuid",
        "home_team": "Brazil",
        "away_team": "Germany",
        "kickoff_at": "2026-06-11T18:00:00Z",
        "status": "FINISHED"
      },
      "prediction": {"home_score": 2, "away_score": 1},
      "actual_result": {"home_score": 2, "away_score": 1},
      "points": 3
    },
    {
      "match": {"id": "uuid", "status": "SCHEDULED", "...": "..."},
      "prediction": {"home_score": 1, "away_score": 0},
      "actual_result": null,
      "points": null
    }
  ]
}
```

## Data Constraints

- This endpoint is read-only; no writes via API
- Ordered by `matches.kickoff_at ASC`
- Only predictions belonging to the calling user are returned
- `prediction_scores` is the source of truth for `points`; if no `prediction_score` row exists, `points` is `null`
