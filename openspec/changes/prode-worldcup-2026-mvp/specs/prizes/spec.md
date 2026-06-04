# Prizes Specification

## Purpose

Manages configurable prize descriptions for rank 1, 2, and 3 within each prediction group. Prizes are informational and do not affect scoring logic.

## Requirements

### Requirement: Prize Configuration

The group owner MUST be able to set or update prize descriptions for ranks 1, 2, and 3. Descriptions are free-form text limited to 255 characters. Non-owners MUST NOT be allowed to modify prizes.

#### Scenario: Owner sets all three prizes

- GIVEN user U is the owner of group G
- WHEN they call `PUT /api/groups/{group_id}/prizes` with descriptions for ranks 1, 2, and 3
- THEN all three `prize_tiers` records are upserted and HTTP 200 is returned

#### Scenario: Owner updates a single prize

- GIVEN prizes are already configured
- WHEN the owner submits only rank 1 with a new description
- THEN rank 1 is updated; ranks 2 and 3 remain unchanged

#### Scenario: Non-owner attempt

- GIVEN user V is a member (not owner) of group G
- WHEN they call `PUT /api/groups/{group_id}/prizes`
- THEN the system returns HTTP 403 `{"error": "forbidden"}`

---

### Requirement: Prize Display

The system MUST include configured prizes in the group detail response. If no prizes are configured, the prizes field MUST be returned as an empty list.

#### Scenario: Prizes visible in group detail

- GIVEN group G has prizes configured for all three ranks
- WHEN any member calls `GET /api/groups/{group_id}`
- THEN the response includes `"prizes": [{"rank": 1, "description": "..."}, ...]`

#### Scenario: No prizes configured

- GIVEN group G has no prize_tier records
- WHEN `GET /api/groups/{group_id}` is called
- THEN the response includes `"prizes": []`

#### Scenario: Prizes shown on leaderboard

- GIVEN group G has prizes configured
- WHEN the leaderboard is fetched
- THEN the response includes the prize descriptions alongside rank 1, 2, and 3 standings

---

## API Contract

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| PUT | `/api/groups/{group_id}/prizes` | JWT (owner) | Set/update prize tiers |
| GET | `/api/groups/{group_id}` | JWT (member) | Includes prizes in response |

### Prize Request Body

```json
{
  "prizes": [
    {"rank": 1, "description": "Amazon gift card $50"},
    {"rank": 2, "description": "Coffee mug"},
    {"rank": 3, "description": "Honorary mention"}
  ]
}
```

## Data Constraints

- `prize_tiers.rank`: INTEGER, CHECK IN (1, 2, 3), NOT NULL
- `prize_tiers.description`: VARCHAR(255), NOT NULL
- `prize_tiers`: UNIQUE on `(group_id, rank)`
- Partial updates (subset of ranks) are allowed; omitted ranks are unchanged
