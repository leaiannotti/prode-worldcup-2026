# Prode: FIFA World Cup 2026 Prediction App

A group-stage prediction web app for FIFA World Cup 2026. Users join prediction groups, submit score predictions, and compete on a real-time leaderboard.

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask + SQLAlchemy + Alembic + PostgreSQL |
| Frontend | Vue 3 + Vite + Pinia + Vue Router + Tailwind CSS 4 |
| Auth | Google OAuth 2.0 + JWT (httpOnly cookie) |
| Database | PostgreSQL 16 |

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.11+
- Node.js 20+
- A Google Cloud project with OAuth 2.0 credentials ([setup guide](#google-oauth-setup))

---

## Local Development Setup

### 1. Clone the repo

```bash
git clone git@github.com:leaiannotti/prode-worldcup-2026.git
cd prode-worldcup-2026
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in all values:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/prode2026
SECRET_KEY=change-this-to-a-long-random-string
JWT_SECRET=another-long-random-secret
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
INGESTION_SECRET=secret-for-webhook-hmac
FRONTEND_URL=http://localhost:5173
FLASK_ENV=development
```

### 3. Start the database

```bash
docker-compose up db -d
```

Wait a few seconds for PostgreSQL to be ready.

### 4. Set up the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Generate and apply database migrations:

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

Seed FIFA 2026 fixture data (12 groups, 48 teams, 72 matches):

```bash
flask seed
# ✅ Seed complete: 12 groups, 48 teams, 72 matches
```

Start the Flask development server:

```bash
flask run
# Running on http://localhost:5000
```

### 5. Set up the frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
# Running on http://localhost:5173
```

### 6. Open the app

Go to **http://localhost:5173** — you should see the Prode 2026 login screen.

---

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or use an existing one)
3. Enable the **Google+ API** or **People API**
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
5. Choose **Web application**
6. Add the following **Authorized redirect URI**:
   ```
   http://localhost:5000/api/auth/callback
   ```
7. Copy the **Client ID** and **Client Secret** into your `.env` file

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/prode2026` |
| `SECRET_KEY` | Flask session secret key | Any long random string |
| `JWT_SECRET` | JWT signing secret | Any long random string |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | From Google Cloud Console |
| `INGESTION_SECRET` | Webhook HMAC secret | Any random string |
| `FRONTEND_URL` | Frontend base URL (for OAuth redirect) | `http://localhost:5173` |
| `FLASK_ENV` | Flask environment | `development` |

---

## Database Migrations

```bash
cd backend
source .venv/bin/activate

# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "description of change"
```

---

## Seed Data

Load the official FIFA 2026 group-stage fixtures:

```bash
cd backend
source .venv/bin/activate
flask seed
```

The seed is **idempotent** — safe to run multiple times without creating duplicates.

Data source: `jsons/worldcup.json` + `jsons/worldcup.teams.json`

---

## Simulating Match Results (Manual Webhook)

Until an automatic results provider is configured, you can push match results manually:

```bash
SECRET="your-ingestion-secret"
PAYLOAD='{"match_id": 1, "home_score": 2, "away_score": 1}'
TS=$(date +%s)
SIG=$(echo -n "${TS}.${PAYLOAD}" | openssl dgst -sha256 -hmac "$SECRET" | awk '{print $2}')

curl -X POST http://localhost:5000/api/webhook/result \
  -H "Content-Type: application/json" \
  -H "X-Signature: t=${TS},v1=${SIG}" \
  -d "$PAYLOAD"

# Expected response: {"status": "accepted"}
```

This will:
1. Update the match status to `finished`
2. Store the final score
3. Automatically calculate points for all predictions on that match

---

## Running Tests

**Backend (pytest):**

```bash
cd backend
source .venv/bin/activate
pytest                          # Run all 86 tests
pytest tests/test_scoring.py    # Run a specific suite
pytest --cov=app --cov-report=term-missing  # With coverage report
```

**Frontend (vitest):**

```bash
cd frontend
npm run test                    # Run all tests
npm run test:coverage           # With coverage report
```

---

## API Reference

Base URL: `http://localhost:5000/api`

All endpoints (except `/api/auth/*`) require a valid JWT in an httpOnly cookie set during login.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/login` | Redirect to Google OAuth |
| GET | `/api/auth/callback` | OAuth callback — sets JWT cookie |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/logout` | Clear JWT cookie |
| POST | `/api/groups` | Create a prediction group |
| POST | `/api/groups/join` | Join a group via invite code |
| GET | `/api/groups` | List user's groups |
| GET | `/api/groups/:id` | Group detail with prizes |
| GET | `/api/groups/:id/members` | Group member list |
| POST | `/api/groups/:id/prizes` | Configure prizes (owner only) |
| GET | `/api/matches` | List matches (filter: `?group=A&date=2026-06-11`) |
| GET | `/api/matches/:id` | Match detail |
| POST | `/api/predictions` | Submit or update a prediction |
| GET | `/api/predictions` | Get user's predictions |
| GET | `/api/scores/leaderboard` | Group leaderboard (`?group_id=`) |
| GET | `/api/scores/history` | User score history (`?group_id=`) |
| POST | `/api/webhook/result` | Ingest match result (HMAC-signed) |

---

## Architecture

```
prode-worldcup-2026/
├── backend/
│   ├── app/
│   │   ├── blueprints/     # Flask route handlers per domain
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic v2 request/response schemas
│   │   ├── services/       # Business logic (scoring, auth, webhook)
│   │   └── middleware/     # JWT auth decorator
│   ├── tests/              # pytest test suite (86 tests)
│   └── alembic/            # Database migrations
├── frontend/
│   ├── src/
│   │   ├── views/          # Page-level Vue components
│   │   ├── components/     # Reusable UI components
│   │   ├── stores/         # Pinia state stores
│   │   ├── composables/    # Vue composables (useDeadlineGuard, etc.)
│   │   └── router/         # Vue Router configuration
│   └── tailwind.config.ts  # Design tokens (Stitch Pitch Precision)
├── jsons/                  # FIFA 2026 fixture source data
├── openspec/               # SDD artifacts (specs, design, tasks)
├── docker-compose.yml
└── .env.example
```

For detailed technical decisions, schema design, and blueprint structure see:
`openspec/changes/prode-worldcup-2026-mvp/design.md`

---

## Project Status

**MVP complete.** Group-stage predictions fully implemented.

| Phase | Status |
|-------|--------|
| PR1 — Scaffold + DB + Seed | ✅ Merged |
| PR2 — Auth (Google OAuth + JWT) | ✅ Merged |
| PR3 — Core domains (groups, matches, predictions, scoring, webhook) | ✅ Merged |
| PR4 — Leaderboard, history, prizes | ✅ Merged |
| Knockout stage predictions | 🔲 Planned (Phase 2) |
| Automatic results provider | 🔲 Planned |
