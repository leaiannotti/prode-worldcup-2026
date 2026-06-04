# Scoring Specification

## Purpose

Calculates points for each prediction after a match result is ingested. Stores an immutable `PredictionScore` record per prediction. Supports idempotent recalculation.

## Requirements

### Requirement: Score Calculation Rule

The system MUST apply the following rule when a match result is available:

| Condition | Points |
|-----------|--------|
| Predicted score exactly matches actual score | 3 |
| Predicted outcome (win/draw/loss) matches but score differs | 1 |
| Neither score nor outcome matches | 0 |

The system MUST compute this for every prediction across every group that has a prediction for the match.

#### Scenario: Exact score match

- GIVEN match M ended 2–1, and user U predicted 2–1 in group G
- WHEN the scoring function runs for match M
- THEN U's `PredictionScore` for `(U, M, G)` is created with `points = 3`

#### Scenario: Correct outcome, wrong score

- GIVEN match M ended 2–1 (home win), and user U predicted 3–0 (home win) in group G
- WHEN scoring runs
- THEN `PredictionScore.points = 1`

#### Scenario: Wrong outcome

- GIVEN match M ended 2–1 (home win), and user U predicted 0–1 (away win) in group G
- WHEN scoring runs
- THEN `PredictionScore.points = 0`

---

### Requirement: Immutable Score Records

The system MUST store each scoring result in a `prediction_scores` table. Score records are immutable once created. Recalculation MUST overwrite (upsert) with the same value — not create a duplicate row.

#### Scenario: Score created on first ingestion

- GIVEN no `PredictionScore` exists for `(prediction_id, match_id)`
- WHEN scoring runs
- THEN a new row is inserted

#### Scenario: Idempotent recalculation

- GIVEN a `PredictionScore` already exists for `(prediction_id, match_id)` with `points = 3`
- WHEN the same result is ingested again
- THEN no new row is created and the existing row remains unchanged (upsert on UNIQUE key)

#### Scenario: Result correction (different score)

- GIVEN a `PredictionScore` exists with `points = 1` (from original result)
- WHEN the webhook delivers a corrected result that changes the outcome
- THEN the `PredictionScore` row is updated to reflect the new points value

---

### Requirement: Group Leaderboard Aggregation

After scoring, the system MUST update `leaderboard_entries` for the affected group by summing `prediction_scores.points` per `(user_id, group_id)`.

#### Scenario: Leaderboard updated after scoring

- GIVEN 5 users in group G have predictions scored for match M
- WHEN scoring completes for match M in group G
- THEN each user's `leaderboard_entries.total_points` in group G reflects the new cumulative total

---

## Data Constraints

- `prediction_scores`: UNIQUE on `(prediction_id)`
- `prediction_scores.points`: INTEGER, NOT NULL, CHECK IN (0, 1, 3)
- `prediction_scores.calculated_at`: server UTC, NOT NULL
- Scoring MUST be triggered server-side on result ingestion only
- Score modification outside of ingestion pipeline is PROHIBITED
