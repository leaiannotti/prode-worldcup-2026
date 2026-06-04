# Prode: FIFA World Cup 2026 Prediction App

A group-stage prediction web app for FIFA World Cup 2026. Users join prediction groups, submit score predictions, and compete on a real-time leaderboard.

## Stack

- **Backend**: Flask + SQLAlchemy + Alembic + PostgreSQL
- **Frontend**: Vue 3 + Vite + Pinia + Vue Router + Tailwind CSS 4
- **Auth**: Google OAuth + JWT (httpOnly cookie)
- **Database**: PostgreSQL 16

## Local Development Setup

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (optional, for local development)
- Node.js 18+ (optional, for local development)

### Quick Start

1. **Clone and navigate to project:**
   ```bash
   cd prode-worldcup-2026
   ```

2. **Copy environment template:**
   ```bash
   cp .env.example .env
   # Edit .env with your Google OAuth credentials
   ```

3. **Start services:**
   ```bash
   docker-compose up
   ```

4. **In another terminal, seed the database:**
   ```bash
   docker-compose exec backend flask seed
   ```

5. **Start frontend dev server:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://prode:prode@localhost:5432/prode_worldcup` |
| `FLASK_ENV` | Flask environment | `development` |
| `SECRET_KEY` | Flask secret key | Any random string |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | From Google Cloud Console |
| `JWT_SECRET` | JWT signing secret | Any random string |
| `FRONTEND_URL` | Frontend base URL | `http://localhost:5173` |
| `INGESTION_SECRET` | Webhook signature secret | Any random string |

### Database Migrations

Migrations are managed with Alembic:

```bash
# Create initial schema
docker-compose exec backend alembic upgrade head

# Create a new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Seed Data

Load 48 teams, 12 groups, and 72 FIFA 2026 group-stage matches:

```bash
docker-compose exec backend flask seed
```

Seed is idempotent — running it multiple times is safe.

### Testing

**Backend (pytest):**
```bash
cd backend
pytest                          # Run all tests
pytest tests/test_seed.py       # Run specific test file
pytest --cov=app                # With coverage
```

**Frontend (vitest):**
```bash
cd frontend
npm run test                    # Run all tests
npm run test:coverage           # With coverage
```

### API Documentation

- **Base URL**: `http://localhost:5000/api`
- **Auth**: All endpoints require valid JWT in httpOnly cookie
- **Webhook**: `POST /api/webhook/result` (HMAC-SHA256 signed)

See individual domain specs in `openspec/changes/prode-worldcup-2026-mvp/specs/` for endpoint documentation.

## Architecture

See `openspec/changes/prode-worldcup-2026-mvp/design.md` for technical decisions, schema design, and blueprint structure.

## Development Workflow

- **Models**: `backend/app/models/`
- **Blueprints**: `backend/app/blueprints/`
- **Services**: `backend/app/services/`
- **Schemas**: `backend/app/schemas/`
- **Tests**: `backend/tests/`
- **Frontend Views**: `frontend/src/views/`
- **Frontend Stores**: `frontend/src/stores/`
- **Frontend Composables**: `frontend/src/composables/`

## Project Status

MVP Phase: Core domains (groups, matches, predictions, scoring, leaderboard)

See `openspec/changes/prode-worldcup-2026-mvp/tasks.md` for implementation plan.
