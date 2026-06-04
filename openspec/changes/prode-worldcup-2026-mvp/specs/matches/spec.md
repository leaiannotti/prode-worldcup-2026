# Matches Specification

## Purpose

Manages the FIFA 2026 group-stage fixture data: 48 teams across 12 groups (A–L), 72 matches. Provides read endpoints for clients to list matches by group or date. Match state drives prediction freeze logic.

## Requirements

### Requirement: Fixture Seed

The system MUST provide a `flask seed` command that idempotently loads all 48 teams, 12 groups, and 72 group-stage matches. Re-running the command MUST NOT create duplicate records.

#### Scenario: Fresh seed

- GIVEN an empty database
- WHEN `flask seed` is executed
- THEN 48 team rows, 12 group rows, and 72 match rows are created

#### Scenario: Idempotent re-run

- GIVEN the seed has already been run
- WHEN `flask seed` is executed again
- THEN no duplicate rows are created and the command exits successfully

#### Scenario: Seed integrity

- GIVEN the seed completes
- WHEN queried
- THEN each group contains exactly 6 teams and each team appears in exactly 3 matches

---

### Requirement: Match State

Each match MUST have a `status` field: `SCHEDULED`, `LIVE`, `FINISHED`. The system MUST expose `kickoff_at` (UTC datetime) and `prediction_deadline_at` = `kickoff_at - 24h`.

#### Scenario: Default match status

- GIVEN a seeded match
- WHEN its status is inspected
- THEN `status` is `SCHEDULED` and `prediction_deadline_at` is 24 hours before `kickoff_at`

#### Scenario: Match transitions to FINISHED

- GIVEN a result ingestion webhook delivers a result for match M
- WHEN the ingestion is processed
- THEN match M status transitions to `FINISHED` and `home_score`/`away_score` are recorded

---

### Requirement: List Matches

The system MUST allow authenticated users to list matches filtered by group or date.

#### Scenario: List by group

- GIVEN matches exist for group "A"
- WHEN a user calls `GET /api/matches?group=A`
- THEN the response contains only the 6 matches in group A, ordered by `kickoff_at` ASC

#### Scenario: List by date

- GIVEN matches are scheduled across multiple dates
- WHEN a user calls `GET /api/matches?date=2026-06-11`
- THEN only matches with `kickoff_at` on that calendar date (UTC) are returned

#### Scenario: Invalid group filter

- GIVEN a user calls `GET /api/matches?group=Z`
- WHEN group Z does not exist
- THEN the system returns HTTP 400 `{"error": "invalid_group"}`

---

## API Contract

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/matches` | JWT | List matches (filters: `group`, `date`) |
| GET | `/api/matches/{id}` | JWT | Match detail |

### Match Response Shape

```json
{
  "id": "uuid",
  "group": "A",
  "home_team": {"id": "uuid", "name": "Brazil", "code": "BRA"},
  "away_team": {"id": "uuid", "name": "Germany", "code": "GER"},
  "kickoff_at": "2026-06-11T18:00:00Z",
  "prediction_deadline_at": "2026-06-10T18:00:00Z",
  "status": "SCHEDULED",
  "home_score": null,
  "away_score": null
}
```

## Data Constraints

- `matches.kickoff_at`: NOT NULL, UTC
- `matches.prediction_deadline_at`: computed as `kickoff_at - interval '24 hours'`, NOT NULL
- `matches.status`: ENUM `SCHEDULED | LIVE | FINISHED`, default `SCHEDULED`
- `teams.code`: NOT NULL, UNIQUE, 3 chars (FIFA code)
- `groups.name`: NOT NULL, UNIQUE, one of A–L
