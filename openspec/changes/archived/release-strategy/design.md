# Design: Release Strategy

## Technical Approach

GitHub Actions orchestrates CI (PRs) and releases (tag push). A root `VERSION` file is the single source of truth. `git-cliff` generates the changelog. Husky + commitlint enforce conventional commits at the root. Coolify deploys via webhook. Backend CORS becomes env-driven. Secrets are rotated and `.env` is kept out of git.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|-------------|-----------|
| Version source | Root `VERSION` file (no `v` prefix) | `package.json`, tag-only | Language-agnostic; tags add `v` for GitHub compatibility |
| Changelog tool | `git-cliff` | `conventional-changelog` | Single static binary, no Node runtime, TOML config, Docker-friendly |
| Commit enforcement | Husky + commitlint at repo root | `pre-commit` (Python) | Aligns with frontend Node toolchain; acceptable for single-dev monorepo |
| Coolify trigger | Webhook (`curl` in workflow) | Auto-detect on tag | Explicit, faster, no polling; token stored in GitHub secret |
| CORS unset behavior | Fail fast in production | Fallback to localhost | Prevents accidental open CORS in prod |
| Secrets history | Rotate only; no `git filter-repo` | Scrub history | Solo dev, likely private repo; rotated secrets neutralize risk |
| Version alignment | Build script reads `VERSION` | Pre-commit sync | Simpler; no extra automation needed |

## Data Flow

```
Developer pushes tag v1.1.0
         │
         ▼
┌─────────────────┐
│  GitHub Actions │  1. Validate tag matches VERSION
│   release.yml   │  2. Run pytest + vitest run
│                 │  3. git-cliff → changelog
│                 │  4. Create GitHub Release
│                 │  5. POST Coolify webhook
└─────────────────┘
         │
         ▼
    Coolify VPS
    (pulls tag,
   builds Docker,
   runs migration)
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `VERSION` | Create | Semver string (e.g., `1.1.0`) |
| `.github/workflows/ci.yml` | Create | PR test gate (backend + frontend, path-filtered) |
| `.github/workflows/release.yml` | Create | Tag-triggered release pipeline |
| `cliff.toml` | Create | `git-cliff` config: groups feat/fix/chore/docs/BREAKING |
| `package.json` (root) | Create | Husky + commitlint deps; `prepare` script |
| `commitlint.config.js` (root) | Create | Extends `@commitlint/config-conventional` |
| `.husky/commit-msg` | Create | Runs `commitlint` on commit message |
| `scripts/release.sh` | Create | Bumps `VERSION`, commits, tags atomically |
| `backend/app/__init__.py` | Modify | CORS reads `FRONTEND_URL` env; removes hardcoded domain |
| `.env.example` | Modify | Add `FRONTEND_URL` docs; ensure all values are placeholders |
| `docs/RELEASE.md` | Create | Full release runbook |
| `CHANGELOG.md` | Create | Initial hand-curated entry for `v1.0.0` → `v1.1.0` |
| `.gitignore` | Modify | Ensure `.env` and `.env.*` are ignored (already present) |

## Interfaces / Contracts

### VERSION Format
Plain text, one line, no `v` prefix: `1.1.0`.

### Validation Contract
Workflow reads `VERSION` content and compares to tag name with `v` stripped. Mismatch → fail fast.

### CORS Contract
```python
# backend/app/__init__.py (sketch)
import os
from flask import Flask

frontend_url = os.getenv("FRONTEND_URL")
if not frontend_url and os.getenv("FLASK_ENV") == "production":
    raise RuntimeError("FRONTEND_URL is required in production")
origin = frontend_url or "http://localhost:5173"
```

### Allowed Commit Types
`build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `test`.

### Webhook Contract
GitHub Actions secret: `COOLIFY_WEBHOOK_URL`. Optional: `COOLIFY_WEBHOOK_TOKEN` if Coolify requires a bearer token.
`curl` step masks the URL/token via `::add-mask::`.

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit | CI workflow syntax | `actionlint` (optional) or manual dry-run |
| Integration | End-to-end release | Cut `v1.1.0` on a test branch, verify release created |
| Manual | Coolify webhook | Trigger release, verify deploy log in Coolify UI |

## Migration / Rollout

No data migration required for this change. Database migrations continue to run via `entrypoint.sh` on container start.

## Open Questions

- [ ] Coolify webhook endpoint URL and token format (must be configured in Coolify UI and stored as GitHub secret)
- [ ] Confirm whether `release-please` is permanently out of scope or future phase

## 1. Architecture Overview

See Data Flow diagram above. Developer pushes a tag → GitHub Actions validates → tests → changelog → GitHub Release → Coolify webhook → deploy.

## 2. Versioning Source of Truth

- `VERSION` at root contains `1.1.0` (no `v`). Tags are `v1.1.0`.
- `release.yml` validates: `cat VERSION | sed 's/^/v/'` must equal `${{ github.ref_name }}`.
- `frontend/package.json` version is cosmetic; build scripts can read `VERSION` if needed, but the root file is the authority.
- `scripts/release.sh` bumps `VERSION`, commits, and tags atomically to prevent mismatch.

## 3. Changelog Generation

- **Tool**: `git-cliff` (installed via GitHub Actions `cargo install` or pre-built binary).
- **Config**: `cliff.toml` at root.
- **Groups**: `["feat", "Features"]`, `["fix", "Bug Fixes"]`, `["chore", "Maintenance"]`, `["docs", "Documentation"]`, `["BREAKING CHANGE", "Breaking Changes"]`.
- **Scope**: `--from $(git describe --tags --abbrev=0)` to `HEAD`.
- **First run**: Hand-curate `CHANGELOG.md` for the 22 historical commits since `v1.0.0`, then append automatically from `v1.1.0` onward.

## 4. GitHub Actions Workflows

### `.github/workflows/ci.yml`
```yaml
on:
  pull_request:
    branches: [main]
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      backend: ${{ steps.filter.outputs.backend }}
      frontend: ${{ steps.filter.outputs.frontend }}
    steps:
      - uses: dorny/paths-filter@v3
        with:
          filters: |
            backend: ['backend/**']
            frontend: ['frontend/**']
  backend-tests:
    needs: changes
    if: ${{ needs.changes.outputs.backend == 'true' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/
  frontend-tests:
    needs: changes
    if: ${{ needs.changes.outputs.frontend == 'true' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
        working-directory: frontend
      - run: npm run test
        working-directory: frontend
```

### `.github/workflows/release.yml`
```yaml
on:
  push:
    tags: ['v*.*.*']
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          version=$(cat VERSION)
          if [ "v${version}" != "${{ github.ref_name }}" ]; then
            echo "VERSION mismatch: ${version} vs ${{ github.ref_name }}"
            exit 1
          fi
  tests:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      # run both backend and frontend tests unconditionally
  changelog:
    needs: tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - run: cargo install git-cliff
      - run: git-cliff --tag ${{ github.ref_name }} --output CHANGELOG.md
      - uses: actions/upload-artifact@v4
        with: { name: changelog, path: CHANGELOG.md }
  release:
    needs: changelog
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with: { name: changelog }
      - uses: softprops/action-gh-release@v2
        with:
          body_path: CHANGELOG.md
          token: ${{ secrets.GITHUB_TOKEN }}
  notify:
    needs: release
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "::add-mask::${{ secrets.COOLIFY_WEBHOOK_URL }}"
          curl -X POST -H "Authorization: Bearer ${{ secrets.COOLIFY_WEBHOOK_TOKEN }}" \
            ${{ secrets.COOLIFY_WEBHOOK_URL }} -fsS
  smoke-test:
    needs: notify
    runs-on: ubuntu-latest
    steps:
      - run: sleep 90
      - name: Health probe
        run: |
          curl -fsS -o /dev/null -w "%{http_code}" https://prodescaloneta.online/health | grep -q '^200$'
      - name: Auth layer probe (expects 401 without token)
        run: |
          code=$(curl -s -o /dev/null -w "%{http_code}" https://prodescaloneta.online/api/auth/me)
          test "$code" = "401"
  notify-failure:
    needs: smoke-test
    if: failure()
    runs-on: ubuntu-latest
    permissions:
      issues: write
    steps:
      - uses: actions/checkout@v4
      - name: Open incident issue
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh issue create \
            --title "🚨 Smoke test failed for ${{ github.ref_name }}" \
            --body "The release workflow completed but post-deploy smoke tests failed. Workflow run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}. Inspect the deploy in Coolify and consider rolling back to the previous stable tag." \
            --label "release,incident"
```

**Secrets**: `COOLIFY_WEBHOOK_URL`, `COOLIFY_WEBHOOK_TOKEN` (optional, depending on Coolify config).

*Note: The exact smoke endpoints are configurable during implementation; the design nails down probe types and failure behavior.*

## 5. Conventional Commit Enforcement

- **Root `package.json`**: `prepare: "husky"`, devDeps: `husky`, `@commitlint/cli`, `@commitlint/config-conventional`.
- **`.husky/commit-msg`**: `npx --no commitlint --edit ${1}`.
- **Merge commits**: `--config` or `commitlint.config.js` can ignore merges with `ignores: [(message) => message.startsWith('Merge')]`. Actually, use `defaultIgnores: true` in commitlint config.
- **Backend dev concern**: Node is required for Husky. Since this is a solo-dev monorepo and frontend already needs Node, this is acceptable. If a backend-only contributor joins, they can install Node or use the `pre-commit` Python framework as an alternative.

## 6. Backend CORS Env-Driven Refactor

- **Change**: In `backend/app/__init__.py`, remove the hardcoded `prodescaloneta.online` entries from the CORS origins list.
- **New behavior**: CORS origins = `[os.getenv("FRONTEND_URL", "http://localhost:5173")]`.
- **Production**: If `FRONTEND_URL` is not set and `FLASK_ENV == "production"`, fail fast with a clear error.
- **`.env.example`**: Add comment above `FRONTEND_URL` explaining it is required in production.
- **Coolify**: Add `FRONTEND_URL=https://prodescaloneta.online` to Coolify environment variables.
- **Backward compat**: Local dev continues to work because `FRONTEND_URL` defaults to `http://localhost:5173` in development.

## 7. Coolify Deployment Trigger

- **Decision**: Webhook (explicit).
- **Why**: More control, faster than polling, no magic. The release workflow is the single source of truth for "deploy now."
- **Implementation**: `curl` POST to Coolify webhook URL at the end of `release.yml`.
- **Token storage**: `COOLIFY_WEBHOOK_URL` and `COOLIFY_WEBHOOK_TOKEN` in GitHub repository secrets.
- **Logging**: Use `echo "::add-mask::${{ secrets.COOLIFY_WEBHOOK_URL }}"` to prevent leaking in logs.
- **Fallback**: If webhook fails, the GitHub Release still exists. Manual deploy via Coolify UI (re-deploy button) is documented in `docs/RELEASE.md`.

## 8. Secrets Cleanup Procedure

1. `git rm --cached .env` (if tracked) — already untracked, so just verify `.gitignore`.
2. Confirm `.env` in `.gitignore`.
3. **Real secrets currently in `.env`**: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `JWT_SECRET`, `SECRET_KEY`, `INGESTION_SECRET`.
4. **Rotate**: Generate new Google OAuth credentials in Google Cloud Console. Generate new random strings for `JWT_SECRET`, `SECRET_KEY`, `INGESTION_SECRET`.
5. **Update Coolify**: Set new secrets as environment variables in the Coolify project.
6. **History**: Do NOT scrub git history. Rationale: solo dev, likely private repo, and rotated secrets neutralize the risk of old commits.

## 9. Migration Safety Checklist

Document in `docs/RELEASE.md`:

- [ ] Review `git diff $(git describe --tags --abbrev=0)..HEAD -- backend/alembic/versions/`.
- [ ] Classify each migration: additive (safe) vs destructive (requires backup).
- [ ] For destructive changes: take DB backup via Coolify UI before deploy.
- [ ] For schema changes touching live data: test locally against a production data snapshot.
- [ ] Post-deploy smoke test (5 min): login, submit a prediction, view leaderboard, check webhook.

## 10. Local Dev Environment

- `docker-compose up db` brings up PostgreSQL.
- `cd backend && flask run` brings up backend (or `docker-compose up backend`).
- `cd frontend && npm run dev` brings up Vite dev server.
- `.env` is gitignored; copied from `.env.example` and filled locally.
- No prod resources accessed from local.

## 11. Documentation Deliverable: `docs/RELEASE.md`

Outline:
1. How to cut a release (run `scripts/release.sh`, push tag, verify GitHub Actions).
2. How to write a conventional commit (allowed types, examples).
3. How to do a hotfix (branch from tag, fix, PR, `scripts/release.sh` with patch bump).
4. Migration safety checklist (Section 9).
5. Coolify deploy troubleshooting (webhook failure, manual redeploy).
6. Secrets rotation runbook (how to rotate, where to update).
7. Rollback runbook (Section 14.4 of design).

## 12. Implementation Order

1. Verify `.env` is untracked and `.gitignore` is correct.
2. Rotate secrets in Google Cloud Console and Coolify.
3. Create root `package.json` + Husky + commitlint.
4. Create root `VERSION` file (start with `1.1.0`).
5. Refactor backend CORS + update `.env.example`.
6. Create `.github/workflows/ci.yml`.
7. Install `git-cliff` config and generate initial `CHANGELOG.md`.
8. Create `.github/workflows/release.yml`.
9. Configure Coolify webhook + test.
10. Write `docs/RELEASE.md`.
11. End-to-end test: cut `v1.1.0`.

## 13. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Husky breaks for backend-only contributors | Document Node requirement; offer `pre-commit` as alternative if team grows |
| Coolify webhook fails | Manual redeploy fallback documented in `docs/RELEASE.md` |
| First auto-generated changelog is messy | Hand-curate first `CHANGELOG.md` entry; auto-generate from `v1.1.0` onward |
| Tag/VERSION mismatch panics developer | `scripts/release.sh` handles bump, commit, and tag atomically |
| CORS fail-fast breaks prod deploy | `FRONTEND_URL` env var documented in `.env.example` and Coolify setup checklist |
| Operator does destructive migration without backup | Section 14.3 checklist in release runbook is mandatory before destructive tags |
| Smoke test probes a slow-warming endpoint | 90s sleep before first probe; endpoint choice avoids cold paths |
| GitHub Releases "Latest" marker becomes wrong after manual Coolify rollback | `gh release edit <tag> --latest` step in runbook |

## 14. Rollback Policy

### 14.1 Strategy Decisions

| Dimension | Decision | Why |
|---|---|---|
| DB rollback | Forward-fix only + manual backup for destructive | Solo dev, low schema churn, downgrade scripts hard to maintain |
| Code rollback | Manual via Coolify UI | Fastest under stress, no automation to fail |
| Detection | Smoke test post-deploy + GitHub issue on failure | Catches catastrophic bugs in <2 min after deploy |
| Traceability | GitHub Releases | Already exists, no extra moving parts |

### 14.2 Expand-Contract Migration Pattern

**Concrete example: rename column `users.username` to `users.handle`**

- **Wrong way**: one migration drops `username` and adds `handle`. Destructive — code rollback cannot read the old column.
- **Right way**:
  - Release N: add `handle` column; write to **both** on every update; backfill `handle` from `username`; keep both columns readable
  - Release N+1 (after monitoring confirms no code reads `username`): drop `username` in a new migration
- Each release is independently rollback-safe by the code-rollback path.

### 14.3 Pre-Release Migration Classification Checklist

Run before cutting a tag that includes migrations:

```bash
git diff $(git describe --tags --abbrev=0)..HEAD -- backend/migrations/
```

Classify every changed migration into one of three buckets:

- **Additive (safe)**: new table, new nullable column, new index, new constraint marked `NOT VALID`, idempotent data backfill
- **Restrictive (caution)**: `NOT NULL` on existing column (needs prior backfill), unique constraint on existing column (needs dedupe), column type narrowing
- **Destructive (manual backup required)**: `DROP COLUMN`, `DROP TABLE`, `DROP INDEX` touching live data, data deletion in upgrade step

**Rule**: for any "Restrictive" or "Destructive" migration, the operator MUST take a DB backup via Coolify UI before pushing the tag.

### 14.4 Rollback Procedure (5-Step Runbook)

1. Identify the broken release tag and the last known-good tag from the GitHub Releases page.
2. Coolify UI → project → deployments → click the previous good tag → **Redeploy**.
3. Wait for Coolify to redeploy (~2 min); verify with a manual `curl` to `/health`.
4. If the broken release included a destructive migration, **restore the DB backup** taken before the destructive migration via Coolify UI.
5. Post-mortem (cold): in calm time, optionally run `gh release edit <good-tag> --latest` to fix the "Latest" marker; write a forward-fix PR; document the incident.

### 14.5 Smoke Test Design

The smoke test runs as a job after the `notify` job in `release.yml` (see Section 4 for YAML sketch).

- **Warm-up**: sleeps 90 seconds before the first probe to give Coolify time to redeploy and warm.
- **Probes** (minimum set):
  - `GET https://prodescaloneta.online/health` → expects `200`
  - `GET https://prodescaloneta.online/api/auth/me` → expects `401` (proves auth layer is up; no token attached on purpose)
- **Optional probes** (worth considering during implementation): `GET /api/groups/standings` (public-ish endpoint with DB read)
- **Configuration**: smoke endpoints list lives in a `SMOKE_TEST_URLS` workflow env variable to allow changes without editing YAML.
- **Failure behavior**: on any probe failure the `smoke-test` job fails, and a follow-up `notify-failure` job with `if: failure()` runs `gh issue create` with title "Smoke test failed for <tag>" and body containing the workflow run URL.
- **Important**: even if the smoke test fails, the GitHub Release stays published. The operator manually rolls back via Coolify UI based on the issue notification.
