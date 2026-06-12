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

### REQ-11: Rollback Policy

MUST enforce forward-fix for database migrations, manual code rollback via Coolify UI, post-deploy smoke tests, and GitHub Releases as the single source of deployment truth.

#### Scenario: Non-destructive migration requires no special procedure

- GIVEN a release includes a non-destructive migration (add nullable column, add table, add index)
- WHEN released to production
- THEN `entrypoint.sh` runs the migration on container start without additional operator action

#### Scenario: Destructive migration requires backup and flagging

- GIVEN a release includes a destructive migration (drop column, drop table, NOT NULL on existing column with data, type change with data loss)
- WHEN preparing to release
- THEN operator MUST take a DB backup via Coolify UI before pushing the tag, AND the release notes MUST flag the destructive change

#### Scenario: Broken destructive migration follows forward-fix path

- GIVEN a destructive migration was deployed and broke production
- WHEN rolling back
- THEN operator MUST follow the forward-fix path by writing a new migration that restores prior behavior and shipping it as a new release; operator MUST NOT use `flask db downgrade`

#### Scenario: Code rollback via Coolify UI

- GIVEN release `v1.2.0` is deployed and broken
- WHEN operator decides to rollback
- THEN operator opens Coolify UI, selects the previous stable tag (e.g. `v1.1.0`) from deployment history, and clicks redeploy

#### Scenario: Rollback succeeds without destructive migration

- GIVEN the previous stable tag did not include a destructive migration
- WHEN re-deployed
- THEN rollback completes successfully within approximately two minutes

#### Scenario: Rollback with destructive migration requires manual DB restore

- GIVEN the broken release included a destructive migration
- WHEN operator rolls back the code via Coolify UI
- THEN the database may be in a forward-incompatible state; operator MUST manually restore the backup taken before the destructive migration

#### Scenario: Post-deploy smoke test runs after Coolify notification

- GIVEN `release.yml` finishes notifying Coolify
- WHEN smoke test job starts after approximately 90 seconds
- THEN workflow MUST `curl` critical endpoints (at minimum `/health` returns 200, plus one to two additional endpoints defined during design)

#### Scenario: Smoke test failure triggers notification

- GIVEN smoke test fails (non-2xx response or timeout)
- WHEN workflow processes the failure
- THEN workflow MUST report failure clearly, AND a follow-up step with `if: failure()` MUST notify the operator by opening a GitHub issue or posting a comment on the release

#### Scenario: Smoke test success marks release complete

- GIVEN smoke test passes
- WHEN workflow finishes
- THEN release is considered deployed and smoke-tested OK; no additional automation runs

#### Scenario: GitHub Releases is the single source of deployment truth

- GIVEN operator needs to identify which tag is currently deployed
- WHEN checking GitHub Releases page
- THEN the most recent release MUST reflect the currently deployed tag; there is no `stable` floating tag, no `STABLE_VERSION` file, and no manual deployment log in `docs/RELEASE.md`

#### Scenario: Rolled-back tag may appear as latest release

- GIVEN a rollback was performed via Coolify UI to an older tag
- WHEN GitHub Releases page is checked
- THEN the latest GitHub Release may temporarily show the rolled-back tag; operator MAY use `gh release edit <tag> --latest` to correct it in calm time

#### Scenario: Release changelog contains grouped changes

- GIVEN operator wants to know what was included in a previous release
- WHEN viewing the release on GitHub
- THEN the changelog body MUST contain the conventional-commit-grouped changes since the prior tag
