# Leaderboard Specification

## Purpose

Provides ranked standings per prediction group. Rankings are based on total points accumulated from scored predictions. The leaderboard is updated automatically after each result ingestion.

## Requirements

### Requirement: Per-Group Ranked Standings

The system MUST return a ranked list of group members ordered by total points descending. Members with equal points MUST share the same rank. The system MUST include each member's current total points and rank.

#### Scenario: Basic leaderboard retrieval

- GIVEN group G has members U1 (10pts), U2 (7pts), U3 (10pts)
- WHEN a member calls `GET /api/groups/{group_id}/leaderboard`
- THEN the response returns rank 1 for both U1 and U3, rank 3 for U2

#### Scenario: Empty leaderboard (no scored matches yet)

- GIVEN group G has members but no matches have been scored
- WHEN the leaderboard is requested
- THEN all members are returned with `total_points = 0`

#### Scenario: Non-member access denied

- GIVEN user B is not in group G
- WHEN they call `GET /api/groups/{group_id}/leaderboard`
- THEN the system returns HTTP 403

---

### Requirement: Leaderboard Updated on Score Calculation

The system MUST update `leaderboard_entries` rows for the affected `(user_id, group_id)` pairs immediately after scoring completes for a match. The update MUST be atomic within the same ingestion transaction.

#### Scenario: Leaderboard reflects new score

- GIVEN user U had 6 total points in group G before match M was ingested
- WHEN match M result is ingested and U earns 3 points
- THEN `leaderboard_entries` for `(U, G)` shows `total_points = 9`

#### Scenario: Recalculation does not double-count

- GIVEN the same result is ingested twice
- WHEN the second ingestion triggers scoring (idempotent)
- THEN `leaderboard_entries.total_points` remains the same after the second run

---

## API Contract

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/groups/{group_id}/leaderboard` | JWT (member) | Ranked standings |

### Leaderboard Response Shape

```json
{
  "group_id": "uuid",
  "updated_at": "2026-06-12T20:30:00Z",
  "standings": [
    {"rank": 1, "user_id": "uuid", "name": "Ana", "picture": "url", "total_points": 10},
    {"rank": 1, "user_id": "uuid", "name": "Carlos", "picture": "url", "total_points": 10},
    {"rank": 3, "user_id": "uuid", "name": "Bob", "picture": "url", "total_points": 7}
  ]
}
```

## Data Constraints

- `leaderboard_entries`: UNIQUE on `(group_id, user_id)`
- `leaderboard_entries.total_points`: INTEGER, NOT NULL, DEFAULT 0, CHECK >= 0
- Rank is computed at query time (not stored); ties share the same rank
- `leaderboard_entries.updated_at`: server UTC, set on each upsert
