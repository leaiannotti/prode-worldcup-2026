# Proposal: Release Strategy

## Why

The repository currently has no CI/CD, no changelog, and no automated release process. The single existing tag `v1.0.0` is 22 commits behind `main`, which includes multiple bug fixes and a large feature. Frontend `package.json` claims `0.1.0`, creating version drift. A `.env` file containing real Google OAuth credentials is tracked in git, posing a critical security risk. Database migrations run automatically on container start without a safety checklist. The goal is to enable incremental development with automatic releases on tag push, complete with GitHub Releases, changelogs, and safe prod/local environment handling.

## What Changes

### In Scope
- `CHANGELOG.md` at repo root, generated from conventional commits.
- Unified versioning source of truth (root `VERSION` file).
- `.github/workflows/release.yml` triggered on tag push `v*.*.*` — runs tests, generates changelog, creates GitHub Release, notifies Coolify.
- `.github/workflows/ci.yml` triggered on PR to `main` — runs `pytest` (backend) and `vitest run` (frontend).
- `commitlint` + Husky at repo root, monorepo-aware.
- `docs/RELEASE.md` documenting the full release process and Coolify webhook config.
- Backend CORS made env-driven (use existing `FRONTEND_URL` from `.env.example`).
- Migration safety checklist documented.
- `.env` removed from git tracking, added to `.gitignore`, secrets rotated.

### Out of Scope
- Migration to release-please (future change).
- Staging environment.
- Per-package versioning.
- Cleaning up historical commit messages.
- Anything not directly required for tag-to-deploy.

## Capabilities

### New Capabilities
- `release-pipeline`: Tag-triggered CI/CD, changelog generation, GitHub Releases, and Coolify deployment notification.

### Modified Capabilities
- None

## Approach

Phase 1 = GitHub Actions + Manual Tag + Coolify Webhook. Enforce conventional commits via Husky + commitlint. Use a root `VERSION` file as the single source of truth. CI gates PRs and releases on passing tests. Backend CORS reads `FRONTEND_URL` from the environment.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `.github/workflows/` | New | `ci.yml` and `release.yml` |
| `backend/app/__init__.py` | Modified | CORS origin env-driven |
| `docs/RELEASE.md` | New | Release process documentation |
| `VERSION` | New | Unified repo version |
| `.env` / `.gitignore` | Modified | Remove secrets from tracking |
| `CHANGELOG.md` | New | Auto-generated changelog |

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `.env` with real Google OAuth credentials in git | High | Add `.env` to `.gitignore`, rotate secrets, audit `.env.example` |
| Migrations auto-run on container start | Med | Document pre-release migration checklist (backup, review, local test) |
| Hardcoded CORS origin in backend | Med | Refactor to `FRONTEND_URL` env var |
| Version drift (`0.1.0` vs `v1.0.0`) | Med | Define root `VERSION` as single source of truth |
| No tests in CI ever | High | CI workflow gates PR merge and release on `pytest` + `vitest run` |

## Rollback Plan

- Revert a bad release by deleting the tag and re-deploying the previous stable tag in Coolify.
- Revert a bad PR by reverting the merge commit on `main`.

## Dependencies

- Coolify webhook endpoint or auto-deploy capability.
- GitHub Actions runner availability.

## Success Criteria

- [ ] Tag push `vX.Y.Z` produces a GitHub Release with changelog.
- [ ] Coolify deploys the tagged version.
- [ ] PRs run tests before merge.
- [ ] Non-conventional commits are rejected at commit time.
- [ ] `docker-compose up` runs local dev with no prod dependencies.
- [ ] Backend CORS is env-driven.

## Open Questions for Spec/Design

- Exact changelog tool: `git-cliff` vs `conventional-changelog`.
- Coolify deploy trigger method: webhook vs auto-detect on tag.
- Notification mechanism to Coolify (webhook URL, secret).
- Unified version location: root `VERSION` file vs `package.json`.

## Proposal Question Round

The following clarifications were provided by the user/orchestrator and shape this proposal:
1. **Versioning**: Unified — single `vX.Y.Z` for the whole repo.
2. **Environments**: Prod (Coolify) + Local (Docker Compose). No staging.
3. **Release cadence**: On-demand. Must support fast hotfix cuts.
4. **Conventional Commits**: Enforced via git hook (commitlint + Husky).
5. **Approach**: Phase 1 = GitHub Actions + Manual Tag + Coolify Webhook. Migration to release-please is OUT OF SCOPE.
