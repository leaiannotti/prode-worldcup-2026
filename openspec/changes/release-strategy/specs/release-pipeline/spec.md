# Release Pipeline Specification

## Purpose

CI/CD, versioning, changelog, deployment, and commit enforcement for the prode-worldcup-2026 monorepo.

## Requirements

### REQ-1: CI on Pull Requests

MUST run `pytest` and `vitest run` on every PR to `main`.

- GIVEN a PR to `main`
- WHEN CI runs
- THEN tests pass; PR mergeable

- GIVEN a PR to `main` with failing tests
- WHEN CI completes
- THEN PR blocked; failures visible

### REQ-2: Tag-Triggered Release

MUST trigger release workflow on `v*.*.*` tags.

- GIVEN tag `v1.2.0` on stable `main`
- WHEN workflow runs
- THEN tests pass, changelog generates, GitHub Release creates, Coolify deploys

- GIVEN tag `v1.2.0` on failing commit
- WHEN tests run
- THEN workflow aborts before GitHub Release

- GIVEN tag `v1.2.0` already exists
- WHEN pushed again
- THEN workflow detects existing release and skips duplicates

### REQ-3: Unified Versioning

MUST use root `VERSION` file as single source of truth.

- GIVEN `VERSION` is `1.2.0` and tag `v1.1.0` pushed
- WHEN workflow starts
- THEN fails with version mismatch error

- GIVEN `VERSION` bumped to `1.2.0` on `main`
- WHEN tag `v1.2.0` pushed
- THEN workflow proceeds using `1.2.0`

### REQ-4: Changelog Generation

MUST generate changelog grouped by conventional commit type.

- GIVEN 22 commits since `v1.0.0`
- WHEN new tag released
- THEN entries grouped by `feat`, `fix`, `chore`; appended to `CHANGELOG.md` and included in Release body

- GIVEN only `fix:` commits since last tag
- WHEN release runs
- THEN changelog contains only `Bug Fixes` section

- GIVEN a commit has `!` or `BREAKING CHANGE:` footer
- WHEN release runs
- THEN changelog includes `Breaking Changes` section

### REQ-5: Conventional Commit Enforcement

MUST reject non-conventional commits at commit time via git hook.

- GIVEN commit message `feat: add leaderboard`
- WHEN hook executes
- THEN commit accepted

- GIVEN commit message `nuevos cambios`
- WHEN hook executes
- THEN commit rejected with error listing allowed types

- GIVEN merge commit `Merge pull request #42`
- WHEN hook executes
- THEN commit accepted without validation

- GIVEN rebase produces `fix: typo`
- WHEN hook executes
- THEN accepted; invalid messages rejected with same error

### REQ-6: Coolify Deployment

MUST notify Coolify after successful GitHub Release without leaking secrets.

- GIVEN successful GitHub Release
- WHEN notification runs
- THEN Coolify deploys; logs contain no secrets

- GIVEN Coolify is unreachable
- WHEN notification runs
- THEN workflow reports failure; Release remains valid; manual deploy is fallback

- GIVEN Coolify webhook secret rotated
- WHEN workflow runs with new secret
- THEN notification succeeds; old secret no longer referenced

### REQ-7: Environment Configuration

MUST read CORS origin from `FRONTEND_URL`.

- GIVEN `FRONTEND_URL` set (e.g., `https://prodescaloneta.online` or `http://localhost:5173`)
- WHEN backend starts
- THEN CORS uses that origin

- GIVEN `FRONTEND_URL` not set
- WHEN backend starts
- THEN fails fast with clear error (or safe local default per design)

### REQ-8: Secrets Hygiene

MUST NOT track `.env` in git or expose real values.

- GIVEN `.env` in `.gitignore`
- WHEN developer modifies `.env`
- THEN git ignores it

- GIVEN `.env.example` inspected
- THEN all values are placeholders; no real secrets

### REQ-9: Migration Safety

MUST run migrations safely on container startup via `entrypoint.sh`.

- GIVEN migration adds nullable column
- WHEN `flask db upgrade` runs in `entrypoint.sh`
- THEN succeeds without data loss

- GIVEN destructive migration planned
- WHEN release process runs
- THEN `docs/RELEASE.md` checklist followed: backup, local test, rollback plan

- GIVEN migration script has error
- WHEN `flask db upgrade` runs
- THEN container fails to start; database not corrupted

### REQ-10: Hotfix Support

MUST support hotfix cuts within ~10 minutes.

- GIVEN critical fix merged to `main`
- WHEN tag `v1.2.1-hotfix` pushed
- THEN workflow runs immediately; deploys to production within ~10 minutes
