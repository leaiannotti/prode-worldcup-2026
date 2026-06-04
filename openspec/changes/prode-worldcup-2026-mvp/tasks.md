# Tasks: prode-worldcup-2026-mvp

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 2,500–3,500 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (scaffold + DB) → PR 2 (auth) → PR 3 (core domains) → PR 4 (derived features + tests) |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Monorepo scaffold + DB models + seed | PR 1 | Base: main; includes Alembic migration + seed command |
| 2 | Auth (backend + frontend) | PR 2 | Base: PR 1 branch; Google OAuth, JWT, route guards |
| 3 | Core domains (groups, matches, predictions, ingestion, scoring) | PR 3 | Base: PR 2 branch; all domain blueprints + Pinia stores + views |
| 4 | Derived features + full test suite | PR 4 | Base: PR 3 branch; leaderboard, history, prizes display, coverage ≥80% |

---

## Phase 0 — Monorepo Scaffolding

- [ ] 0.1 Create root `docker-compose.yml` with `db` (postgres:16) and `backend` services; include `frontend` dev target
- [ ] 0.2 Create `.env.example` with all required env vars (`DATABASE_URL`, `SECRET_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `INGESTION_SECRET`, `JWT_SECRET`, `FRONTEND_URL`)
- [ ] 0.3 Create root `.gitignore` covering `.env`, `__pycache__`, `*.pyc`, `node_modules`, `dist`, `.venv`
- [ ] 0.4 Create root `README.md` with local dev setup instructions (docker-compose up, seed, frontend dev server)
- [ ] 0.5 Create `backend/requirements.txt` — Flask, SQLAlchemy, Alembic, Authlib, PyJWT, Pydantic v2, psycopg2-binary, pytest, pytest-cov, python-dotenv
- [ ] 0.6 Create `backend/app/__init__.py` — `create_app()` factory; register blueprints, extensions, seed CLI
- [ ] 0.7 Create `backend/app/config.py` — `DevelopmentConfig`, `TestingConfig`, `ProductionConfig` classes
- [ ] 0.8 Create `backend/app/extensions.py` — SQLAlchemy `db`, Alembic `migrate`, Authlib `oauth` init (no app binding)
- [ ] 0.9 Create `frontend/package.json` + `vite.config.ts` + `tsconfig.json` + `tailwind.config.ts` — Vue 3 + Vite + Tailwind CSS 4 + Pinia + Vue Router + Axios + vitest
- [ ] 0.10 Create `frontend/src/lib/api.ts` — Axios instance with `withCredentials: true`, base URL from env, 401 interceptor that redirects to `/login`

## Phase 1 — Database Models + Migration + Seed

> Satisfies: matches/Fixture Seed, matches/Match State

- [ ] 1.1 Create `backend/app/models/user.py` — `User` model (UUID PK, `google_sub` UNIQUE, `email` UNIQUE, `name`, `picture_url`, `last_login_at`, `created_at`) ⚠️ multi-model file
- [ ] 1.2 Create `backend/app/models/team.py` — `WorldCupGroup` model (SERIAL PK, `name` UNIQUE A–L) + `Team` model (FK→`world_cup_groups`, `code` 3-char UNIQUE)
- [ ] 1.3 Create `backend/app/models/match.py` — `Match` model (FK→`teams`×2 + `world_cup_groups`, `kickoff_utc`, `deadline_utc` pre-computed, `status` ENUM scheduled/in_progress/finished, `home_score`, `away_score`); index on `kickoff_utc`
- [ ] 1.4 Create `backend/app/models/group.py` — `PredictionGroup` (UUID PK, `invite_code` UNIQUE), `GroupMembership` (composite PK, `role` admin/member), `GroupPrize` (UNIQUE on `group_id+rank`, rank CHECK 1–3) ⚠️ multi-model file
- [ ] 1.5 Create `backend/app/models/prediction.py` — `Prediction` model (UNIQUE on `user_id+match_id+group_id`, score CHECK ≥0, `submitted_at`, `is_frozen`)
- [ ] 1.6 Create `backend/app/models/score.py` — `PredictionScore` model (UNIQUE on `prediction_id`, `points` CHECK IN(0,1,3), `score_type` ENUM exact/outcome/miss, `calculated_at`)
- [ ] 1.7 Create `backend/app/models/__init__.py` — re-export all models so Alembic auto-detects them
- [ ] 1.8 Configure `backend/alembic.ini` + `backend/alembic/env.py` — point to `DATABASE_URL`, import app models for autogenerate
- [ ] 1.9 Run `alembic revision --autogenerate -m "initial schema"` to generate `backend/alembic/versions/001_initial_schema.py`; verify generated DDL matches design schema
- [ ] 1.10 Create `backend/app/seed.py` — `flask seed` CLI command; idempotent upsert of 12 `WorldCupGroup` rows, 48 `Team` rows, 72 `Match` rows with real FIFA 2026 kickoff_utc dates and computed `deadline_utc = kickoff_utc - 24h` ⚠️ multi-file write (seed data + CLI registration in factory)
- [ ] 1.11 **Test (RED→GREEN):** `backend/tests/test_seed.py` — verify fresh seed creates exactly 48 teams, 12 groups, 72 matches; idempotent re-run adds 0 rows; each group has 6 teams; each team appears in 3 matches (satisfies matches/Fixture Seed scenarios 1–3)

## Phase 2 — Auth

> Satisfies: auth/Google OAuth Login, auth/JWT Session Validation, auth/Logout

- [ ] 2.1 Create `backend/app/schemas/auth.py` — Pydantic v2 `UserResponse` schema (`id`, `email`, `name`, `picture`)
- [ ] 2.2 Create `backend/app/services/auth_service.py` — `upsert_user(google_info)` → `User`; `issue_jwt(user_id)` → signed token (7d expiry); `set_jwt_cookie(response, token)` (httpOnly, Secure, SameSite=Lax)
- [ ] 2.3 Create `backend/app/middleware/auth.py` — `jwt_required` decorator; reads cookie, validates signature + expiry; injects `g.current_user`; returns 401 on missing/expired/tampered token
- [ ] 2.4 Create `backend/app/blueprints/auth.py` — `GET /api/auth/login` (Authlib redirect), `GET /api/auth/callback` (code exchange → upsert user → set cookie → 302 frontend), `GET /api/auth/me` (jwt_required), `POST /api/auth/logout` (clear cookie) ⚠️ multi-file (blueprint + service + middleware all wired in factory)
- [ ] 2.5 **Test (RED→GREEN):** `backend/tests/test_auth.py` — valid login upserts user + sets cookie; invalid state returns 400; repeat login updates name/picture; valid JWT resolves current_user; expired JWT returns 401; tampered JWT returns 401; logout clears cookie (satisfies auth scenarios 1–7)
- [ ] 2.6 Create `frontend/src/stores/auth.ts` — Pinia store: `user`, `isAuthenticated`; actions: `fetchMe()`, `logout()`; persists login state
- [ ] 2.7 Create `frontend/src/router/index.ts` — routes for `/login`, `/dashboard`, `/groups/:id`, `/groups/:id/leaderboard`, `/matches`, `/history`; `requiresAuth` meta + `beforeEach` guard that calls `fetchMe()` and redirects to `/login` on 401
- [ ] 2.8 Create `frontend/src/views/LoginView.vue` — Google OAuth button that navigates to `/api/auth/login`; handles redirect back from OAuth callback
- [ ] 2.9 Create `frontend/src/components/NavBar.vue` — shows user avatar, name, logout button; visible on all authenticated routes
- [ ] 2.10 **Test (vitest):** `frontend/src/stores/auth.test.ts` — fetchMe resolves user; unauthenticated state redirects; logout clears store

## Phase 3 — Core Domains

> Satisfies: prediction-groups, matches, predictions, result-ingestion, scoring specs

### 3A — Groups Blueprint

- [ ] 3.1 Create `backend/app/schemas/group.py` — Pydantic v2: `CreateGroupRequest`, `JoinGroupRequest`, `GroupResponse`, `MemberResponse`, `PrizeRequest`
- [ ] 3.2 Create `backend/app/blueprints/groups.py` — `POST /api/groups` (create + generate invite_code), `POST /api/groups/join`, `GET /api/groups`, `GET /api/groups/:id` (includes prizes), `GET /api/groups/:id/members`, `POST /api/groups/:id/prizes` (owner-only) ⚠️ multi-file (blueprint + schemas + membership guard)
- [ ] 3.3 **Test (RED→GREEN):** `backend/tests/test_groups.py` — create group 201 + auto-owner; duplicate name 409; join valid code 200; already member 409; invalid code 404; member lists members 200; non-member 403; owner sets prizes 200; non-owner prizes 403 (satisfies prediction-groups scenarios 1–8 + prizes scenarios 1–3)

### 3B — Matches Blueprint

- [ ] 3.4 Create `backend/app/schemas/match.py` — Pydantic v2 `MatchResponse` with nested `TeamResponse`, `GroupResponse`, `kickoff_at`, `prediction_deadline_at`, `status`, `home_score`, `away_score`
- [ ] 3.5 Create `backend/app/blueprints/matches.py` — `GET /api/matches` (filters: `group`, `date`; ordered by `kickoff_utc` ASC; invalid group → 400), `GET /api/matches/:id`
- [ ] 3.6 **Test (RED→GREEN):** `backend/tests/test_matches.py` — list by group returns 6 matches sorted; list by date filters correctly; invalid group 400; match detail returns correct shape (satisfies matches/List Matches scenarios 1–3)

### 3C — Predictions Blueprint

- [ ] 3.7 Create `backend/app/schemas/prediction.py` — Pydantic v2: `PredictionRequest` (scores ≥0), `PredictionResponse`, `GroupPredictionsResponse` (pre/post deadline masking)
- [ ] 3.8 Create `backend/app/services/prediction_service.py` — `submit_prediction(user, match, group, home, away)`: check deadline (`server NOW() >= match.deadline_utc` → raise 423), upsert prediction
- [ ] 3.9 Create `backend/app/blueprints/predictions.py` — `POST /api/predictions` (submit/update, deadline enforced), `GET /api/predictions?group_id=&match_id=` (caller's predictions), `GET /api/groups/:id/matches/:match_id/predictions` (group view with pre-deadline masking) ⚠️ multi-file (blueprint + service + schema)
- [ ] 3.10 **Test (RED→GREEN):** `backend/tests/test_predictions.py` — first submission 201; update before deadline 200; negative score 422; after deadline 423; at deadline (boundary) 423; pre-deadline masks other users' scores; post-deadline reveals all; non-member 403 (satisfies predictions scenarios 1–8)

### 3D — Result Ingestion + Scoring

- [ ] 3.11 Create `backend/app/services/scoring_service.py` — pure `calculate_score(predicted_home, predicted_away, actual_home, actual_away) -> tuple[int, str]` returning `(points, score_type)`; `score_match(match_id, home, away, db_session)` bulk-calculates + upserts `prediction_scores` (ON CONFLICT DO UPDATE) + upserts `leaderboard_entries` — atomic within caller's transaction ⚠️ multi-file (service + leaderboard upsert logic)
- [ ] 3.12 Create `backend/app/services/webhook_service.py` — `verify_webhook_signature(payload, sig_header, secret, max_age=300) -> bool`; parses `t={ts},v1={hash}` format; rejects stale timestamp
- [ ] 3.13 Create `backend/app/blueprints/webhook.py` — `POST /api/webhook/result`: verify HMAC → 401 on invalid/stale; verify match exists → 404; update match (home_score, away_score, status=finished); call `score_match()`; return 200
- [ ] 3.14 **Test (RED→GREEN):** `backend/tests/test_scoring.py` — `calculate_score` unit tests: exact=3, outcome=1, miss=0; `score_match` inserts prediction_scores; idempotent re-run no duplicates; corrected result updates score; leaderboard updated atomically (satisfies scoring scenarios 1–7)
- [ ] 3.15 **Test (RED→GREEN):** `backend/tests/test_webhook.py` — valid HMAC + fresh timestamp → 200; invalid HMAC → 401; stale timestamp → 401 "request_too_old"; first ingestion sets match FINISHED; idempotent re-ingestion → 200 no extra rows; multiple groups scored; match with no predictions → 200 (satisfies result-ingestion scenarios 1–8)

### 3E — Frontend Core Views

- [ ] 3.16 Create `frontend/src/stores/groups.ts` — Pinia store: `groups`, `currentGroup`; actions: `fetchGroups()`, `fetchGroup(id)`, `createGroup(name)`, `joinGroup(code)`, `setPrizes(id, prizes)`
- [ ] 3.17 Create `frontend/src/stores/matches.ts` — Pinia store: `matches`; actions: `fetchMatches(filters?)`, `fetchMatch(id)`
- [ ] 3.18 Create `frontend/src/stores/predictions.ts` — Pinia store: `predictions`; actions: `fetchGroupPredictions(groupId, matchId)`, `submitPrediction(groupId, matchId, home, away)`, `fetchMyPredictions(groupId)`
- [ ] 3.19 Create `frontend/src/composables/useDeadlineGuard.ts` — `isOpen: ComputedRef<boolean>` (true if `now < deadlineUtc`), `timeLeft: ComputedRef<string>` countdown string
- [ ] 3.20 Create `frontend/src/views/DashboardView.vue` — lists user's groups with `GroupCard.vue`; buttons to create/join group
- [ ] 3.21 Create `frontend/src/views/GroupDetailView.vue` — shows group info, member list, prizes; navigates to leaderboard/matches
- [ ] 3.22 Create `frontend/src/views/MatchesView.vue` — lists matches filtered by group/date with `MatchCard.vue`; each card shows freeze state via `useDeadlineGuard`
- [ ] 3.23 Create `frontend/src/components/PredictionForm.vue` — score inputs (home/away); disabled when `isOpen === false`; calls `submitPrediction`; shows 423 error message
- [ ] 3.24 **Test (vitest):** `frontend/src/composables/useDeadlineGuard.test.ts` — future deadline: isOpen=true; past deadline: isOpen=false; exactly at deadline: isOpen=false
- [ ] 3.25 **Test (vitest):** `frontend/src/stores/groups.test.ts` + `frontend/src/stores/predictions.test.ts` — mock API responses, verify store state transitions and error handling

## Phase 4 — Derived Features

> Satisfies: leaderboard, score-history, prizes display specs

- [ ] 4.1 Create `backend/app/blueprints/scores.py` — `GET /api/scores/leaderboard?group_id=` (member-only; ranked by total_points DESC; ties share rank; includes prize descriptions); `GET /api/scores/history?group_id=` (caller's predictions + scores, ordered by `kickoff_at` ASC, unscored predictions included with `points: null`)
- [ ] 4.2 Create `backend/app/schemas/score.py` — Pydantic v2: `LeaderboardResponse` (standings + prizes), `HistoryEntryResponse`, `HistoryResponse`
- [ ] 4.3 Create `frontend/src/stores/leaderboard.ts` — Pinia store: `standings`, `prizes`; actions: `fetchLeaderboard(groupId)`, `fetchHistory(groupId)`
- [ ] 4.4 Create `frontend/src/composables/useScoreFormatter.ts` — formats `score_type` enum to human label (e.g., "Exact", "Outcome", "Miss") + point badge color
- [ ] 4.5 Create `frontend/src/views/LeaderboardView.vue` — ranked standings table with `LeaderboardTable.vue`; shows prize descriptions for top 3 positions; non-member redirect to dashboard
- [ ] 4.6 Create `frontend/src/views/HistoryView.vue` — user's prediction history list; shows actual result, prediction, points; pending matches show "—" for points
- [ ] 4.7 Create `frontend/src/components/LeaderboardTable.vue` — presentational; renders standings rows with rank, avatar, name, points, prize badge (rank 1–3 only)
- [ ] 4.8 **Test (RED→GREEN):** `backend/tests/test_leaderboard.py` — basic standings with ties (rank shared); empty leaderboard (all 0 pts); non-member 403; leaderboard updated after scoring; idempotent re-ingestion no double-count; prizes shown in leaderboard response (satisfies leaderboard scenarios 1–5 + prizes/Prizes shown on leaderboard)
- [ ] 4.9 **Test (RED→GREEN):** `backend/tests/test_history.py` — mix of scored/unscored predictions; no predictions returns []; non-member 403; corrected result reflected; no write endpoint (405); chronological order (satisfies score-history scenarios 1–6)
- [ ] 4.10 **Test (vitest):** `frontend/src/stores/leaderboard.test.ts` + `frontend/src/composables/useScoreFormatter.test.ts` — verify standings ordering, prize association, formatter output

## Phase 5 — Coverage + Cleanup

- [ ] 5.1 Create `backend/tests/conftest.py` — pytest fixtures: `app` (TestingConfig), `client` (Flask test client), `db_session` (transaction rollback after each test), `seed_user`, `seed_group`, `seed_match`
- [ ] 5.2 Run `pytest --cov=app --cov-report=term-missing` and ensure ≥80% coverage; add targeted unit tests for any uncovered branches in `scoring_service`, `webhook_service`, `auth_service`
- [ ] 5.3 Run `vitest run --coverage` and verify all stores + composables pass; fix any failing tests
- [ ] 5.4 Verify `docker-compose up` starts cleanly, `alembic upgrade head` runs without errors, `flask seed` loads 48/12/72 rows
- [ ] 5.5 Update `README.md` with complete local dev instructions, env var descriptions, seed command, and webhook cURL example
