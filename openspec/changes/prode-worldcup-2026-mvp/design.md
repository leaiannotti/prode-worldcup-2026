# Design: prode-worldcup-2026-mvp

## Technical Approach

Greenfield monorepo with `backend/` (Flask + PostgreSQL) and `frontend/` (Vue 3 + Vite). Flask app factory pattern with one blueprint per domain. SQLAlchemy ORM + Alembic migrations. Vue 3 SPA with Pinia stores and Vue Router. Google OAuth via `authlib`, JWT in httpOnly cookie. HMAC-signed webhook for result ingestion. Scoring computed synchronously on ingestion.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|-------------|-----------|
| Serialization | Pydantic v2 | Marshmallow | Better type hints, faster validation, Python-native |
| Auth library | Authlib | Flask-Dance, python-social-auth | Supports PKCE natively, well-maintained, minimal config |
| JWT storage | httpOnly cookie | localStorage, Authorization header | XSS-proof; CSRF mitigated via SameSite=Lax |
| Score calculation | Synchronous on webhook | Celery async queue | MVP simplicity; ≤72 matches × N users is fast enough. Async deferred to Phase 2 |
| Prediction scope | (user, match, group) triple | (user, match) pair | Users can be in multiple groups with different strategies |
| Leaderboard | Computed view (query-time) | Materialized table | Avoids stale data; N users per group is small enough for live query |
| Frontend state | Pinia | Vuex 4 | Pinia is Vue 3's official recommendation, simpler API |
| CSS | Tailwind CSS 4 | Bootstrap, plain CSS | Utility-first, fast prototyping, consistent design system |

## Monorepo Directory Tree

```
prode-worldcup-2026/
├── docker-compose.yml
├── .env.example
├── README.md
├── openspec/
├── backend/
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py          # create_app() factory
│   │   ├── config.py            # Config classes (Dev/Test/Prod)
│   │   ├── extensions.py        # db, migrate, jwt init
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── group.py         # PredictionGroup, GroupMembership, GroupPrize
│   │   │   ├── team.py          # Team, WorldCupGroup
│   │   │   ├── match.py
│   │   │   ├── prediction.py
│   │   │   └── score.py         # PredictionScore
│   │   ├── blueprints/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── groups.py
│   │   │   ├── matches.py
│   │   │   ├── predictions.py
│   │   │   ├── scores.py
│   │   │   └── webhook.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── prediction_service.py
│   │   │   ├── scoring_service.py
│   │   │   └── webhook_service.py
│   │   ├── middleware/
│   │   │   └── auth.py          # jwt_required decorator
│   │   ├── schemas/             # Pydantic v2 request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── group.py
│   │   │   ├── match.py
│   │   │   ├── prediction.py
│   │   │   └── score.py
│   │   └── seed.py              # flask seed CLI command
│   └── tests/
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_groups.py
│       ├── test_predictions.py
│       ├── test_scoring.py
│       └── test_webhook.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── index.html
    ├── tailwind.config.ts
    └── src/
        ├── main.ts
        ├── App.vue
        ├── router/
        │   └── index.ts
        ├── stores/
        │   ├── auth.ts
        │   ├── groups.ts
        │   ├── matches.ts
        │   ├── predictions.ts
        │   └── leaderboard.ts
        ├── composables/
        │   ├── useDeadlineGuard.ts
        │   └── useScoreFormatter.ts
        ├── views/
        │   ├── LoginView.vue
        │   ├── DashboardView.vue
        │   ├── GroupDetailView.vue
        │   ├── LeaderboardView.vue
        │   ├── MatchesView.vue
        │   └── HistoryView.vue
        ├── components/
        │   ├── MatchCard.vue
        │   ├── PredictionForm.vue
        │   ├── LeaderboardTable.vue
        │   ├── GroupCard.vue
        │   └── NavBar.vue
        └── lib/
            └── api.ts           # Axios/fetch wrapper
```

## Database Schema

```sql
-- Users (Google OAuth)
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    google_sub    VARCHAR(255) UNIQUE NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    name          VARCHAR(255) NOT NULL,
    picture_url   TEXT,
    last_login_at TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- World Cup Groups (A–L)
CREATE TABLE world_cup_groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(10) UNIQUE NOT NULL  -- "Group A" .. "Group L"
);

-- Teams (48)
CREATE TABLE teams (
    id                 SERIAL PRIMARY KEY,
    name               VARCHAR(100) NOT NULL,
    flag_url           TEXT,
    world_cup_group_id INTEGER NOT NULL REFERENCES world_cup_groups(id)
);

-- Matches (72 group-stage)
CREATE TABLE matches (
    id                 SERIAL PRIMARY KEY,
    home_team_id       INTEGER NOT NULL REFERENCES teams(id),
    away_team_id       INTEGER NOT NULL REFERENCES teams(id),
    world_cup_group_id INTEGER NOT NULL REFERENCES world_cup_groups(id),
    stage              VARCHAR(20) NOT NULL DEFAULT 'group',
    kickoff_utc        TIMESTAMPTZ NOT NULL,
    deadline_utc       TIMESTAMPTZ NOT NULL,  -- kickoff_utc - 24h, pre-computed
    status             VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    home_score         INTEGER,
    away_score         INTEGER,
    result_locked_at   TIMESTAMPTZ,
    CONSTRAINT chk_status CHECK (status IN ('scheduled','in_progress','finished'))
);
CREATE INDEX idx_matches_kickoff ON matches(kickoff_utc);

-- Prediction Groups
CREATE TABLE prediction_groups (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL,
    invite_code VARCHAR(20) UNIQUE NOT NULL,
    created_by  UUID NOT NULL REFERENCES users(id),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Group Memberships
CREATE TABLE group_memberships (
    user_id   UUID NOT NULL REFERENCES users(id),
    group_id  UUID NOT NULL REFERENCES prediction_groups(id),
    role      VARCHAR(10) NOT NULL DEFAULT 'member',
    joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, group_id),
    CONSTRAINT chk_role CHECK (role IN ('admin','member'))
);

-- Group Prizes (top 3 per group)
CREATE TABLE group_prizes (
    id          SERIAL PRIMARY KEY,
    group_id    UUID NOT NULL REFERENCES prediction_groups(id),
    rank        INTEGER NOT NULL,
    description VARCHAR(255) NOT NULL,
    UNIQUE (group_id, rank),
    CONSTRAINT chk_rank CHECK (rank BETWEEN 1 AND 3)
);

-- Predictions (per user, match, group)
CREATE TABLE predictions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id),
    match_id     INTEGER NOT NULL REFERENCES matches(id),
    group_id     UUID NOT NULL REFERENCES prediction_groups(id),
    home_score   INTEGER NOT NULL CHECK (home_score >= 0),
    away_score   INTEGER NOT NULL CHECK (away_score >= 0),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_frozen    BOOLEAN NOT NULL DEFAULT false,
    UNIQUE (user_id, match_id, group_id)
);

-- Prediction Scores (immutable, one per prediction per result)
CREATE TABLE prediction_scores (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_id UUID NOT NULL REFERENCES predictions(id),
    points        INTEGER NOT NULL,
    score_type    VARCHAR(10) NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (prediction_id),
    CONSTRAINT chk_score_type CHECK (score_type IN ('exact','outcome','miss'))
);
```

## Blueprint / Route Table

| Blueprint | Method | Path | Auth | Description |
|-----------|--------|------|------|-------------|
| auth | GET | `/api/auth/login` | — | Redirect to Google OAuth |
| auth | GET | `/api/auth/callback` | — | Handle OAuth callback, set JWT cookie |
| auth | GET | `/api/auth/me` | JWT | Return current user profile |
| auth | POST | `/api/auth/logout` | JWT | Clear JWT cookie |
| groups | GET | `/api/groups` | JWT | List user's groups |
| groups | POST | `/api/groups` | JWT | Create group (caller = admin) |
| groups | GET | `/api/groups/:id` | JWT | Group detail + members |
| groups | POST | `/api/groups/join` | JWT | Join via invite_code |
| groups | POST | `/api/groups/:id/prizes` | JWT | Set prize tiers (admin) |
| matches | GET | `/api/matches` | JWT | List all matches (filterable by group/date) |
| matches | GET | `/api/matches/:id` | JWT | Match detail |
| predictions | GET | `/api/predictions?group_id=&match_id=` | JWT | Get user predictions |
| predictions | POST | `/api/predictions` | JWT | Submit/update prediction (deadline enforced) |
| scores | GET | `/api/scores/leaderboard?group_id=` | JWT | Group leaderboard |
| scores | GET | `/api/scores/history?group_id=` | JWT | User score history |
| webhook | POST | `/api/webhook/result` | HMAC | Ingest match result, trigger scoring |

## Frontend Route + Store Map

| Route | View | Stores Used | Auth |
|-------|------|-------------|------|
| `/login` | LoginView | auth | — |
| `/dashboard` | DashboardView | auth, groups | JWT |
| `/groups/:id` | GroupDetailView | groups, matches, predictions | JWT |
| `/groups/:id/leaderboard` | LeaderboardView | leaderboard | JWT |
| `/matches` | MatchesView | matches | JWT |
| `/history` | HistoryView | predictions, leaderboard | JWT |

## Data Flow

### Auth Flow

```
Browser                    Flask                   Google
  │                          │                       │
  ├─ GET /api/auth/login ──→ │                       │
  │                          ├─ 302 → Google ──────→ │
  │  ← ─ redirect ─ ─ ─ ─ ─ │                       │
  ├─ consent ──────────────────────────────────────→ │
  │  ← ─ ─ callback + code ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┤
  ├─ GET /api/auth/callback?code=X ───────────────→ │
  │                          ├─ exchange code ─────→ │
  │                          │ ← ─ tokens ─ ─ ─ ─ ─ ┤
  │                          ├─ upsert user          │
  │                          ├─ sign JWT             │
  │  ← ─ 302 + Set-Cookie ─ ┤                       │
  ├─ GET /dashboard ───────→ │                       │
```

### Webhook → Score Calculation

```
External Provider           Flask (webhook bp)         DB
  │                            │                        │
  ├─ POST /api/webhook/result ─→                        │
  │   (HMAC-SHA256 signed)     │                        │
  │                            ├─ verify HMAC           │
  │                            ├─ verify timestamp      │
  │                            ├─ UPDATE match ────────→│
  │                            │   (home_score,         │
  │                            │    away_score,         │
  │                            │    status=finished)    │
  │                            ├─ SELECT predictions ──→│
  │                            │   WHERE match_id = X   │
  │                            │←─ prediction rows ─────┤
  │                            ├─ calculate scores      │
  │                            │   3=exact, 1=outcome,  │
  │                            │   0=miss               │
  │                            ├─ INSERT prediction_ ──→│
  │                            │   scores (ON CONFLICT  │
  │                            │   DO NOTHING)          │
  │  ← ─ 200 OK ─ ─ ─ ─ ─ ─ ─┤                        │
```

## Interfaces / Contracts

```python
# Scoring service — pure function, no DB dependency
def calculate_score(
    predicted_home: int, predicted_away: int,
    actual_home: int, actual_away: int
) -> tuple[int, str]:
    """Returns (points, score_type).
    3 / 'exact'   — exact scoreline match
    1 / 'outcome' — correct winner or draw
    0 / 'miss'    — wrong outcome
    """
```

```python
# Webhook HMAC verification
def verify_webhook_signature(
    payload: bytes, signature: str, secret: str, max_age_seconds: int = 300
) -> bool:
    """HMAC-SHA256 of payload. Signature header: 't={timestamp},v1={hash}'.
    Rejects if timestamp older than max_age_seconds."""
```

```typescript
// Frontend deadline guard composable
function useDeadlineGuard(deadlineUtc: string): {
  isOpen: ComputedRef<boolean>   // true if now < deadline
  timeLeft: ComputedRef<string>  // human-readable countdown
}
```

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit (backend) | scoring_service, webhook_service, auth middleware | pytest, mock DB |
| Unit (frontend) | stores, composables (useDeadlineGuard) | vitest |
| Integration (backend) | blueprint routes, DB operations, OAuth flow | pytest + test client + test DB |
| Integration (frontend) | views with mocked API | vitest + vue-test-utils |

Target: ≥80% backend coverage, vitest passing. TDD enforced per `openspec/config.yaml`.

## Migration / Rollout

Greenfield — no existing data. Alembic `upgrade head` creates all tables. `flask seed` populates 12 groups, 48 teams, 72 matches. Rollback: `alembic downgrade base`.

## Open Questions

- [ ] Which external provider sends match results to the webhook? (API-Football, manual trigger, or custom script for MVP?)
- [ ] Domain/hosting decision for OAuth redirect URI configuration
