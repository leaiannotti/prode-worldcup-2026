# Result Ingestion Specification

## Purpose

Receives match results via an HMAC-SHA256 signed webhook. Validates authenticity, records the result, triggers scoring for all predictions on that match, and updates leaderboards. The entire pipeline MUST be idempotent.

## Requirements

### Requirement: HMAC Signature Verification

The system MUST verify the webhook payload signature before processing. The signature MUST be an HMAC-SHA256 of the raw request body using a shared secret. The request MUST include a timestamp header; requests older than 5 minutes MUST be rejected to prevent replay attacks.

#### Scenario: Valid signature and fresh timestamp

- GIVEN a POST to `/api/ingestion/result` with a valid HMAC-SHA256 `X-Signature` header and `X-Timestamp` within 5 minutes
- WHEN the system verifies the signature
- THEN the payload is accepted and processing continues

#### Scenario: Invalid signature

- GIVEN the `X-Signature` header does not match the expected HMAC
- WHEN the system verifies
- THEN HTTP 401 is returned and NO score processing occurs

#### Scenario: Stale timestamp (replay attack)

- GIVEN the `X-Timestamp` header is more than 5 minutes in the past
- WHEN the system checks the timestamp
- THEN HTTP 401 `{"error": "request_too_old"}` is returned

---

### Requirement: Result Recording

The system MUST update the match record with `home_score`, `away_score`, and transition `status` to `FINISHED`. Re-ingestion of the same match with the same scores MUST be idempotent.

#### Scenario: First result ingestion

- GIVEN match M is in `SCHEDULED` or `LIVE` state
- WHEN the webhook delivers `{"match_id": M, "home_score": 2, "away_score": 1}`
- THEN `matches.home_score = 2`, `away_score = 1`, `status = FINISHED`

#### Scenario: Idempotent re-ingestion (same result)

- GIVEN match M already has `home_score = 2, away_score = 1, status = FINISHED`
- WHEN the same payload is received again
- THEN no database changes occur and HTTP 200 is returned

#### Scenario: Corrected result

- GIVEN match M has `home_score = 2, away_score = 1`
- WHEN the webhook delivers `{"match_id": M, "home_score": 2, "away_score": 2}` (correction)
- THEN `matches` is updated and scoring is recalculated for all affected predictions

---

### Requirement: Score Recalculation Trigger

After recording the result, the system MUST trigger the scoring pipeline for all predictions on that match across all groups. This MUST occur synchronously within the same request lifecycle.

#### Scenario: Multiple groups scored

- GIVEN match M has predictions in groups G1 and G2
- WHEN the result is ingested
- THEN scoring runs for all predictions in both groups and all leaderboards are updated

#### Scenario: Match with no predictions

- GIVEN match M has no predictions from any user
- WHEN the result is ingested
- THEN no scoring or leaderboard update occurs; HTTP 200 is returned

---

## API Contract

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/ingestion/result` | HMAC | Ingest match result |

### Request Headers

```
X-Signature: sha256=<hex>
X-Timestamp: <unix_seconds>
Content-Type: application/json
```

### Request Body

```json
{
  "match_id": "uuid",
  "home_score": 2,
  "away_score": 1
}
```

### Response

- `200`: Accepted and processed (or idempotent no-op)
- `401`: Invalid signature or stale timestamp
- `404`: Match not found
- `422`: Invalid payload

## Data Constraints

- HMAC secret stored as environment variable `INGESTION_SECRET`; MUST NOT be in source code
- Timestamp window: ±5 minutes from server clock
- `match_id` MUST reference an existing match; non-existent IDs return HTTP 404
