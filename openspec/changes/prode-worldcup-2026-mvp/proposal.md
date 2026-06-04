# Proposal: prode-worldcup-2026-mvp

## Intent

Build a group-stage prediction web app for FIFA World Cup 2026. Users join named prediction groups (e.g., "Oficina", "Amigos"), submit score predictions for each of the 72 group-stage matches, and compete on a real-time leaderboard. Match results are ingested automatically via webhook and scores are computed server-side without human intervention.

The project is greenfield — no production code exists yet.

## Scope

### In Scope
- Google OAuth authentication (JWT in httpOnly cookie)
- Prediction groups with configurable prizes for top 3 positions
- Match data seed: 48 teams, 12 groups (A–L), 72 group-stage matches
- Score predictions per (user, match, group) with 24h pre-kickoff freeze
- Scoring rule: 3 pts exact result · 1 pt correct outcome · 0 pts wrong
- Immutable score history per prediction per match
- Automated result ingestion via HMAC-signed webhook → auto score recalculation
- Leaderboard per prediction group (updated on ingestion)
- Alembic migrations + `flask seed` fixture command

### Out of Scope
- Knockout stage predictions (Phase 2)
- Push notifications or real-time WebSocket updates
- Mobile-native app
- Admin dashboard / manual result entry UI
- Match polling fallback (deferred enhancement)

## Capabilities

> Greenfield project — `openspec/specs/` is empty. All capabilities are new.

### New Capabilities
- `auth`: Google OAuth login/logout, JWT session, user identity
- `prediction-groups`: Create/join groups, prize tier configuration, member management
- `matches`: Team/group/match data model, fixture seed, match state
- `predictions`: Submit/update predictions, 24h freeze enforcement, per-group scope
- `scoring`: Score calculation (3/1/0 rule), immutable PredictionScore history
- `leaderboard`: Per-group ranked standings, recomputed on ingestion
- `result-ingestion`: HMAC-verified webhook endpoint, idempotent score recalculation

### Modified Capabilities
None

## Approach

**Backend (Flask):** One blueprint per domain (`/auth`, `/groups`, `/matches`, `/predictions`, `/scores`, `/leaderboard`, `/ingestion`). SQLAlchemy ORM + Alembic. Pydantic v2 for serialization. Prediction deadline (`kickoff_at - 24h`) pre-computed and enforced server-side only (no client trust). Score recalculation triggered synchronously on ingestion (async queue deferred to Phase 2).

**Frontend (Vue 3):** SPA with Vue Router + Pinia stores. One composable per domain. Auth guard on protected routes. Group selection flow before predictions.

**Database:** PostgreSQL. Key tables: `users`, `prediction_groups`, `prize_tiers`, `group_memberships`, `teams`, `matches`, `predictions`, `prediction_scores`, `leaderboard_entries`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/` | New | Flask app, blueprints, models, migrations, seed |
| `frontend/` | New | Vue 3 SPA, Pinia stores, composables, views |
| `openspec/specs/` | New | 7 capability specs created |
| `docker-compose.yml` | New | PostgreSQL + backend + frontend services |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Prediction freeze clock skew (client vs server) | Med | Enforce deadline server-side only; reject late POSTs |
| Concurrent score calculation on same match | Med | DB UNIQUE on `(prediction_id, match_id)`; idempotent recalc |
| Webhook spoofing / replay | Med | HMAC-SHA256 signature + timestamp window validation |
| Fixture count mismatch (72 confirmed by user) | Low | Seed data reviewed; 12 groups × 6 matches = 72 |
| Google OAuth token expiry mid-session | Low | Silent refresh via `/auth/refresh`; fallback to re-login |

## Rollback Plan

Greenfield — no production data to migrate. Rollback = revert git branch. If schema was applied: `alembic downgrade base` drops all tables. No data loss risk in pre-launch state.

## Dependencies

- Google OAuth credentials (Cloud Console project, callback URL configured)
- HMAC secret for webhook ingestion (environment variable)
- PostgreSQL instance (local via Docker, production TBD)
- Match result data source (external provider sends webhook or manual trigger for MVP)

## Success Criteria

- [ ] User can log in with Google and land on the app
- [ ] User can create or join a prediction group with prize tiers
- [ ] User can submit predictions for all 72 matches before the 24h deadline
- [ ] Predictions submitted after the deadline are rejected with a clear error
- [ ] Webhook ingestion updates scores and leaderboard automatically
- [ ] Leaderboard shows correct ranked standings per group after result ingestion
- [ ] Score history is immutable — recalculating the same result produces the same score
- [ ] `pytest` suite passes with ≥80% coverage; `vitest run` suite passes
