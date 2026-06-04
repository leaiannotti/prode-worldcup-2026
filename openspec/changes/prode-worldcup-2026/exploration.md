# Exploration: prode-worldcup-2026

> **Phase**: sdd-explore
> **Date**: 2026-06-04
> **Mode**: openspec
> **Status**: greenfield — no existing code

---

## Current State

This is a **greenfield monorepo**. No application code exists yet. The openspec scaffolding is in place via `sdd-init`:

- `openspec/config.yaml` — project config, stack detected
- Stack: Vue 3 + Vite (`frontend/`), Python Flask (`backend/`), PostgreSQL, Google OAuth
- Testing: pytest (backend), vitest (frontend), strict TDD enabled

---

## Domain Model

### Core Entities

```
User
├── id (UUID)
├── google_id (unique)
├── email
├── display_name
├── avatar_url
└── created_at

PredictionGroup            ← "Oficina", "Amigos", etc.
├── id (UUID)
├── name
├── created_by → User
├── invite_code (short unique slug for joining)
├── created_at
└── prizes: PrizeTier[]    ← configurable per group

PrizeTier
├── id
├── group → PredictionGroup
├── rank (1, 2, 3)
├── description (e.g. "$5000", "Una birra")
└── (optional) amount + currency

GroupMembership
├── group → PredictionGroup
├── user → User
├── role (owner | member)
└── joined_at

Team
├── id
├── name (e.g. "Argentina")
├── flag_url
├── group_code (A–L)       ← 12 groups (USA/Canada/Mexico 2026)
└── fifa_code (3-letter)

Match
├── id
├── stage (group | r32 | r16 | qf | sf | final)
├── home_team → Team (nullable for knockout until bracket resolves)
├── away_team → Team (nullable for knockout)
├── group_code (nullable, only for group stage)
├── match_number (1–104 or however many)
├── kickoff_at (UTC timestamp)
├── prediction_deadline_at (= kickoff_at - 24h, pre-computed)
├── home_score (nullable until result ingested)
├── away_score (nullable until result ingested)
├── status (scheduled | live | finished | postponed | cancelled)
└── external_id (from result API, for idempotent ingestion)

Prediction
├── id
├── user → User
├── match → Match
├── group → PredictionGroup  ← prediction is scoped to a group membership
├── home_score_predicted
├── away_score_predicted
├── submitted_at
├── is_locked (bool — set true once deadline passes OR match is live/finished)
└── UNIQUE(user, match, group)

PredictionScore            ← computed after match finishes
├── id
├── prediction → Prediction
├── points_earned (0 | 1 | 3)
├── score_type (exact | outcome | miss)
└── calculated_at

Leaderboard                ← materialized / computed view
├── group → PredictionGroup
├── user → User
├── total_points
├── exact_count
├── outcome_count
├── miss_count
└── last_updated_at
```

### Relationships Summary

```
User ─< GroupMembership >─ PredictionGroup
PredictionGroup ─< PrizeTier
PredictionGroup ─< GroupMembership
User ─< Prediction
Match ─< Prediction
Prediction ─< PredictionScore
PredictionGroup + User → Leaderboard row
```

### Key Design Decisions in the Domain Model

1. **Prediction is scoped to (user, match, group)** — a user who belongs to multiple groups makes separate predictions per group. This allows different prize pools with separate standings.
2. **`prediction_deadline_at` is pre-computed** — avoids runtime subtraction and makes the freeze query trivial (`WHERE kickoff_at > now()`).
3. **`PredictionScore` is a separate table** — immutable record per prediction post-result; enables score history per match, per user, per group.
4. **`Leaderboard` as a computed/materialized table** — avoids expensive aggregation queries on every leaderboard page load. Updated via the result ingestion pipeline.

---

## Affected Areas (greenfield — files to create)

```
backend/
├── app/
│   ├── auth/            — Google OAuth flow, session/JWT handling
│   ├── groups/          — PredictionGroup CRUD, invite codes, membership
│   ├── matches/         — Match listing, fixture seeding
│   ├── predictions/     — Prediction CRUD, deadline enforcement
│   ├── scores/          — Score calculation engine
│   ├── leaderboard/     — Aggregated standings queries
│   ├── ingestion/       — Webhook/API endpoint for result ingestion
│   └── models/          — SQLAlchemy ORM models
├── migrations/          — Alembic migrations
├── seeds/               — FIFA 2026 fixtures seed data
└── tests/

frontend/
├── src/
│   ├── features/
│   │   ├── auth/        — Google login, session state
│   │   ├── groups/      — Group creation/join UI
│   │   ├── predictions/ — Match prediction form, lock indicator
│   │   ├── leaderboard/ — Standings view per group
│   │   └── history/     — Score breakdown per match
│   ├── composables/     — Reusable logic (useAuth, usePredictions, etc.)
│   └── router/          — Vue Router
```

---

## Approaches

### Approach 1: Flask Blueprints + SQLAlchemy + REST API (Recommended)

Organize the backend as Flask Blueprints, one per domain. SQLAlchemy ORM for models, Alembic for migrations. REST API consumed by Vue SPA.

- **Pros**: Clean separation of concerns; well-established pattern; Flask-Login or Flask-JWT for session; easy to test each Blueprint independently.
- **Cons**: Manual serialization (use Marshmallow or Pydantic for schemas); no auto-generated API docs unless you add Flask-RESTX.
- **Effort**: Medium

### Approach 2: Flask + Flask-SQLAlchemy + OpenAPI (swagger)

Same as above but add Flask-RESTX or apiflask for auto-generated OpenAPI docs and request validation.

- **Pros**: API documentation for free; integrated validation reduces boilerplate.
- **Cons**: Tighter coupling to extension; slightly steeper initial setup.
- **Effort**: Medium-High

### Approach 3: FastAPI instead of Flask

Replace Flask with FastAPI; async by default; first-class Pydantic models.

- **Pros**: Automatic OpenAPI, async score calculation, better type safety.
- **Cons**: User explicitly requested Flask — not the scope of this exploration.
- **Effort**: N/A (out of scope)

**Recommendation**: Approach 1 — Flask Blueprints + SQLAlchemy + Marshmallow (or Pydantic v2). Straightforward, testable, meets the stated stack.

---

## External Dependencies

### 1. Google OAuth

- **Provider**: Google Identity Platform (OAuth 2.0 / OIDC)
- **Library**: `authlib` (Flask-compatible, handles PKCE/CSRF) or `google-auth-oauthlib`
- **Flow**: Authorization Code Flow with PKCE. Backend issues a JWT session token after OAuth callback; frontend stores token in `localStorage` or `httpOnly` cookie.
- **Risk**: Google credential rotation; test accounts needed in dev.

### 2. Match Result Ingestion

Two viable options:

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **Webhook** (inbound) | Admin POSTs result to `/api/ingestion/result` | Full control, no polling, cheap | Requires authenticated caller (shared secret); needs manual trigger or external webhook source |
| **API Polling** | Backend cron polls a football API (e.g. api-football.com, football-data.org) | Fully automated | Paid tier for live data; rate limits; API schema changes break ingestion |
| **Hybrid** | Polling for automatic detection + webhook as manual override | Best reliability | Most complexity |

**Recommendation**: Start with **webhook** (simple, admin-controlled). Add polling later if automation is needed. Key endpoint: `POST /api/ingestion/result` with HMAC-signed payload.

### 3. FIFA 2026 Fixture Data

- Must seed 48 group-stage matches + 32 knockout placeholders at launch.
- Source: FIFA official schedule or trusted football data API for bootstrap seed.
- Groups A–L (12 groups × 4 teams = 48 teams; 6 matches per group = 72 group matches — not 48. Correction below).

> **Data correction**: With 48 teams in 12 groups of 4, each group has C(4,2) = 6 matches → 12 × 6 = **72 group-stage matches** total (not 48). The requirement description says "6 matches per group = 48 total" — that's 8 groups × 6 = 48. FIFA 2026 has **12 groups** → 72 group matches. This needs clarification. The scoring and prediction logic is the same either way; only the seed data count differs.

---

## Data Seeding Needs

```
teams.json / teams.sql
├── 48 teams (confirmed FIFA 2026 participants)
├── Each with: name, fifa_code, group_code (A–L), flag_url

matches_group_stage.json
├── 72 group-stage matches (12 groups × 6 matches each)
├── Each with: home_team, away_team, group_code, kickoff_at (UTC), match_number
├── Source: FIFA official calendar (published ~6 months before)
├── Note: kickoff_at → prediction_deadline_at = kickoff_at - 24h (auto-computed on insert)

matches_knockout.json (placeholders)
├── 16 × R32 slots (TBD teams)
├── 8 × R16 slots
├── 4 × QF slots
├── 2 × SF slots
├── 1 × Final slot
├── home_team / away_team = NULL until bracket resolves
```

**Seeding strategy**: Alembic data migration or a management command (`flask seed`). Production seed is idempotent (skip if already seeded, keyed by `external_id`).

---

## Risk Areas

### R1 — Prediction Freeze Logic (HIGH)

The 24-hour deadline freeze is the most user-visible correctness concern.

- **Risk**: A user submits a prediction after the deadline but before the UI reflects the lock. Clock skew between frontend and backend.
- **Mitigation**: Enforce deadline server-side ONLY. Backend checks `match.prediction_deadline_at < now()` on every `POST /predictions`. Frontend shows lock indicator as UX hint only.
- **Edge case**: Postponed matches — `prediction_deadline_at` must be recalculated if `kickoff_at` changes. Add an `update_match_schedule` endpoint that re-computes deadlines.

### R2 — Concurrent Score Calculation (MEDIUM)

When a match result is ingested, the system must calculate scores for potentially hundreds of predictions simultaneously.

- **Risk**: Race condition if two ingestion requests arrive for the same match. Duplicate score rows.
- **Mitigation**: 
  - `UNIQUE(prediction_id)` constraint on `PredictionScore` — database-level deduplication.
  - Idempotent ingestion: check `match.status == 'finished'` before re-calculating.
  - Consider a Celery task queue for async calculation if user count grows; start synchronous and add async if needed.
- **Leaderboard update**: Batch-update leaderboard rows after score calculation. Use `UPDATE ... WHERE group_id IN (...)` rather than per-row updates.

### R3 — API Availability (LOW-MEDIUM if using polling)

If a football API is used for result polling:

- **Risk**: API downtime during match window → delayed score calculation.
- **Mitigation**: Webhook fallback. Cache last-known state. Alert admin on ingestion failure.

### R4 — Knockout Stage Bracket Complexity (MEDIUM)

Bracket progression (which teams advance) must be reflected before knockout predictions open.

- **Risk**: Predicting a match before teams are known.
- **Mitigation**: Knockout matches open for predictions only once both teams are confirmed (match `status = 'scheduled'` AND `home_team != NULL AND away_team != NULL`). This is a business rule enforced in the `Prediction` write endpoint.

### R5 — Multi-Group Prediction UX (LOW)

A user in 3 groups must make predictions 3× for the same match (once per group). This is intentional but could confuse users.

- **Mitigation**: UI shows "You have N groups — predict for each" with a summary view. Not a technical risk, a UX risk.

### R6 — Group Invite Code Security (LOW)

Invite codes must not be guessable.

- **Mitigation**: Use UUID4 or a short random token (e.g. 8-char base62). Codes can optionally have expiry.

---

## Recommended Architecture

```
┌─────────────────────────────────┐
│  Vue 3 + Vite SPA (frontend/)   │
│  ┌──────────┐  ┌─────────────┐  │
│  │  Pinia   │  │ Vue Router  │  │
│  │  stores  │  │ (client)    │  │
│  └──────────┘  └─────────────┘  │
└────────────┬────────────────────┘
             │  REST / JSON
             ▼
┌─────────────────────────────────┐
│  Flask REST API (backend/)      │
│  Blueprints per domain:         │
│  /api/auth  /api/groups         │
│  /api/matches /api/predictions  │
│  /api/scores /api/leaderboard   │
│  /api/ingestion (webhook)       │
└────────────┬────────────────────┘
             │  SQLAlchemy ORM
             ▼
┌─────────────────────────────────┐
│  PostgreSQL                     │
│  Alembic migrations             │
└─────────────────────────────────┘
```

### Auth Flow

```
Browser → Google OAuth → /api/auth/callback
       → Flask issues JWT (httpOnly cookie OR Bearer token)
       → Vue stores auth state in Pinia
       → Protected routes check auth state client-side
       → API validates JWT on every request (Flask middleware)
```

### Score Calculation Pipeline

```
POST /api/ingestion/result
  └─ validate HMAC signature
  └─ update Match(home_score, away_score, status='finished')
  └─ SELECT predictions WHERE match_id = X AND is_locked = TRUE
  └─ FOR EACH prediction:
       points = calc_points(predicted, actual)
       INSERT PredictionScore(...) ON CONFLICT DO NOTHING
  └─ batch UPDATE Leaderboard WHERE affected groups
  └─ return 200 OK
```

### Prediction Lock Flow

```
POST /api/predictions
  └─ authenticate user
  └─ SELECT match WHERE id = X
  └─ IF now() >= match.prediction_deadline_at → 409 Deadline passed
  └─ IF match.status IN ('live', 'finished') → 409 Match already started
  └─ UPSERT Prediction (user, match, group) ON CONFLICT UPDATE
  └─ return 200 OK
```

---

## Key Technical Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auth mechanism | JWT in httpOnly cookie | Stateless, no server-side session store needed; CSRF-safe with SameSite |
| ORM | SQLAlchemy (Flask-SQLAlchemy) | Standard Flask ORM; declarative models; Alembic for migrations |
| Serialization | Marshmallow or Pydantic v2 | Input validation + output serialization in one place |
| Score calculation | Synchronous on ingestion webhook | Simple; add Celery later if scale demands async |
| Leaderboard | Materialized table updated on ingestion | Avoid expensive GROUP BY on every page load |
| Invite codes | Short UUID/random token | Security without complexity |
| Prediction scope | Per (user, match, group) | Each group is a separate competition |
| Fixture seeding | Alembic data migration + `flask seed` | Reproducible, version-controlled |
| Deadline enforcement | Server-side only | Never trust client clock |
| Frontend state | Pinia stores | Official Vue 3 state management |

---

## Recommendation

**Start with group-stage only** (72 matches, 12 groups). The knockout stage is architecturally the same but depends on group-stage results, so it's naturally phase 2.

**MVP scope**:
1. Google OAuth + user session
2. Create/join groups with invite codes
3. Seed teams & group-stage fixtures
4. Prediction CRUD with deadline enforcement
5. Webhook for result ingestion + score calculation
6. Leaderboard per group

**Phase 2**:
- Knockout stage bracket + predictions
- Score history detailed view
- Group prizes UI
- Optional: result polling cron

---

## Risks Summary

| ID | Risk | Severity | Mitigation |
|----|------|----------|------------|
| R1 | Prediction freeze clock skew | HIGH | Server-side enforcement only |
| R2 | Concurrent score calculation | MEDIUM | DB UNIQUE constraint + idempotent ingestion |
| R3 | Football API availability | LOW-MEDIUM | Webhook-first; polling as enhancement |
| R4 | Knockout bracket TBD teams | MEDIUM | Lock predictions until teams confirmed |
| R5 | Multi-group UX confusion | LOW | Clear UI labeling per group |
| R6 | Invite code guessability | LOW | Use UUID4/base62 random tokens |
| R7 | Fixture data count | LOW | FIFA 2026 = 72 group matches (not 48); verify requirement |

---

## Ready for Proposal

**Yes.** The domain is well-defined. Recommend proceeding to `sdd-propose` with MVP scope (group stage only). Knockout stage as phase 2.

**What the orchestrator should tell the user**: The domain model is solid. The main clarification needed is the exact match count (72 group matches for 12 groups, not 48). Recommend starting with Google Auth + Groups + Group-stage predictions as MVP, then layering knockout on top.
