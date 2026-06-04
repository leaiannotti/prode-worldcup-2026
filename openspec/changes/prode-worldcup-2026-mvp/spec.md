# Specs: prode-worldcup-2026-mvp

All domains are **new** (no existing specs). Each spec is a full specification.

## Domain Index

| Domain | File | Type | Requirements | Scenarios |
|--------|------|------|-------------|-----------|
| auth | specs/auth/spec.md | New | 3 | 9 |
| prediction-groups | specs/prediction-groups/spec.md | New | 4 | 12 |
| matches | specs/matches/spec.md | New | 3 | 9 |
| predictions | specs/predictions/spec.md | New | 3 | 9 |
| scoring | specs/scoring/spec.md | New | 3 | 9 |
| leaderboard | specs/leaderboard/spec.md | New | 2 | 6 |
| result-ingestion | specs/result-ingestion/spec.md | New | 3 | 9 |
| prizes | specs/prizes/spec.md | New | 2 | 6 |
| score-history | specs/score-history/spec.md | New | 3 | 9 |

**Total**: 9 domains · 26 requirements · 78 scenarios

## Coverage

- Happy paths: covered (all domains)
- Edge cases: covered (freeze, idempotency, duplicate membership, tie-breaking, replay attacks, corrected results)
- Error states: covered (401, 403, 404, 405, 409, 422, 423 per domain)

## Key Cross-Domain Constraints

1. **Prediction freeze** enforced by `matches.prediction_deadline_at` = `kickoff_at - 24h`; server clock only.
2. **Scoring** is triggered exclusively by `result-ingestion`; never manually.
3. **Leaderboard** is updated atomically within the ingestion transaction.
4. **Score history** is a read-only derived view from `prediction_scores` (immutable source).
5. **Prizes** are informational; they do NOT affect scoring or ranking logic.
6. **HMAC secret** (`INGESTION_SECRET`) MUST be injected via environment variable only.

## Next Step

Ready for design phase (`sdd-design`).
