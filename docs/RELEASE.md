# Release runbook

How to cut releases, handle hotfixes, and recover from incidents for prode-worldcup-2026.

## Quick reference

- **Tag format**: `vMAJOR.MINOR.PATCH` (e.g. `v1.1.0`)
- **Branch source for deploys**: `main` (Coolify pulls from `main`)
- **Auto-deploy**: OFF in Coolify for both backend and frontend (triggered only by release workflow)
- **Release script**: `scripts/release.sh`
- **Workflow**: `.github/workflows/release.yml`
- **Production backend**: `https://api.prodescaloneta.online`
- **Production frontend**: `https://prodescaloneta.online`

## 1. Cutting a release

(REQ-2)

### 1.1. Write the user-facing changelog FIRST

Before bumping the version, add an entry to `backend/app/changelog.json`
with notes written **from the user's perspective**. This is what powers
the in-app "What's New" modal — keep it readable and non-technical.

Add the new entry as the **first** item in the `entries` array (newest first):

```json
{
  "version": "1.1.1",
  "released_at": "",
  "translations": {
    "es": {
      "title": "¡Hay novedades!",
      "new": ["..."],
      "fixed": ["..."]
    },
    "en": {
      "title": "What's new",
      "new": ["..."],
      "fixed": ["..."]
    }
  }
}
```

- Leave `released_at` empty — the release script auto-fills it with today's UTC date.
- `new` and `fixed` are required; `improved` is optional.
- Both `es` and `en` are mandatory.

Commit the changelog with a conventional message:

```bash
git add backend/app/changelog.json
git commit -m "docs(changelog): add v1.1.1 release notes"
```

> The release script (`scripts/release.sh`) validates this file before
> bumping `VERSION`. If the entry is missing or malformed, the script
> fails and shows a copy-pasteable template. There is also a backend
> test (`test_version_matches_repo_root_version_file`) that guards
> against drift between `changelog.json` and `VERSION` in CI.

### 1.2. Developer runs the release script

Check out `main` and pull the latest changes:

```bash
git checkout main
git pull
```

Run the helper script with the desired bump level:

```bash
scripts/release.sh patch   # bug fix
scripts/release.sh minor   # new feature
scripts/release.sh major   # breaking change
```

What the script does:
1. Verifies you are on `main` (or `release-strategy` during the change)
2. Verifies the working tree is clean
3. Pulls latest with `--ff-only`
4. Reads `VERSION`, computes the next version
5. **Validates `backend/app/changelog.json` has a well-formed entry for the next version** (see section 1.1). Auto-fills `released_at` if empty.
6. Writes the new version back to `VERSION`
7. Commits with `chore(release): vX.Y.Z` (combining `VERSION` bump and any changelog auto-fill in one commit)
8. Tags with `vX.Y.Z`

### 1.3. Push the tag

```bash
git push --follow-tags
```

This pushes both the commit and the tag in one command. The `release.yml` workflow triggers on the tag push.

### 1.4. Watch the release

Monitor the run at:
`https://github.com/leaiannotti/prode-worldcup-2026/actions`

Workflow steps in order:

1. **validate** — reads `VERSION` and compares to the tag name; fails fast if mismatched
2. **backend-tests** — installs Python deps, runs `pytest backend/`
3. **frontend-tests** — installs Node deps, runs `npm run test` in `frontend/`
4. **changelog** — runs `git-cliff` with `cliff.toml` to generate `RELEASE_NOTES.md`
5. **release** — creates a GitHub Release using the generated notes
6. **notify** — POSTs to both Coolify webhooks:
   - Backend: `COOLIFY_BACKEND_WEBHOOK_URL`
   - Frontend: `COOLIFY_FRONTEND_WEBHOOK_URL`
   - Both use `COOLIFY_WEBHOOK_TOKEN` as Bearer token
   - URLs and tokens are masked in logs
7. **smoke-test** — waits 90s, then probes `GET /health` (expect `200`) and `GET /api/auth/me` (expect `401`)
8. **notify-failure** — runs only if smoke-test fails; opens a GitHub issue with the workflow URL

### 1.5. Verify the release

Check the GitHub Release page:
`https://github.com/leaiannotti/prode-worldcup-2026/releases`

The release body should contain the changelog grouped by conventional commit type.

Check Coolify deployments:
- Backend: `https://api.prodescaloneta.online/health` → `200`
- Frontend: `https://prodescaloneta.online` → loads in browser

Expected total time from tag push to smoke-test completion: ~10 minutes.

## 2. Conventional commits guide

(REQ-5)

Allowed types (enforced by `commitlint.config.js`):

- `build` — build system or dependency changes
- `chore` — maintenance, tooling, cleanup
- `ci` — CI/CD workflow changes
- `docs` — documentation changes
- `feat` — new feature
- `fix` — bug fix
- `perf` — performance improvement
- `refactor` — code change that neither fixes a bug nor adds a feature
- `revert` — reverts a previous commit
- `style` — formatting, missing semicolons, etc.
- `test` — adding or correcting tests

### Examples

**GOOD:**

```
feat: add leaderboard pagination
fix(backend): correct CORS origin check
docs: document release runbook
```

**BAD:**

```
nuevos cambios                 # missing type
feat ADD leaderboard           # type must be lowercase, no space before colon
feat: Add leaderboard.         # description should be lowercase, no trailing period
fix:                           # empty description
```

### How enforcement works

Husky runs a `commit-msg` hook on every commit. The hook calls `commitlint` with `commitlint.config.js`. If the message does not match the conventional format, the commit is rejected and you see the allowed type list.

Merge commits are auto-ignored (`defaultIgnores: true`). You do not need to rewrite merge messages.

### Hotfix tip

If the hook blocks you at 2 AM, the most common mistakes are:
- Missing type
- Misspelled type
- Capital letter after the colon
- Trailing period

**NEVER use `--no-verify`.** Fix the message and retry.

## 3. Hotfix procedure

(REQ-10)

Scenario: critical bug in production during a live World Cup match.

Steps:

1. Branch from `main` (or from the last known-good tag if `main` is dirty):
   ```bash
   git checkout main
   git pull
   git checkout -b fix/hotfix-description
   ```
2. Apply the smallest possible fix. One change, one commit.
3. Open a PR to `main`. If you are the only developer, you may self-merge after a quick sanity check.
4. Run the release script with `patch`:
   ```bash
   scripts/release.sh patch
   ```
5. Push:
   ```bash
   git push --follow-tags
   ```
6. Monitor the workflow and smoke test.
7. If the fix works, merge the hotfix branch to `main`.

Expected total time: ~10 minutes.

If multiple things are broken: do **one hotfix at a time**. Resist bundling. Each hotfix is a separate patch release.

## 4. Migration safety

(REQ-9)

Database migrations run automatically via `entrypoint.sh` when the container starts. Before cutting a release that includes migrations, classify every migration into one of three buckets.

### 4.1. Three-bucket classification

**Additive (safe)** — deploy without special action:
- New table
- New nullable column
- New index
- New constraint with `NOT VALID`
- Idempotent data backfill

**Restrictive (caution)** — needs preparation before the release:
- `NOT NULL` on an existing column (requires prior backfill)
- Unique constraint on an existing column (requires deduplication)
- Column type narrowing

**Destructive (manual backup required)** — always back up before deploying:
- `DROP COLUMN`
- `DROP TABLE`
- `DROP INDEX` touching live data
- Data deletion in an upgrade step

### 4.2. Pre-release checklist

1. Inspect the migration diff:
   ```bash
   git diff $(git describe --tags --abbrev=0)..HEAD -- backend/alembic/versions/
   ```
2. Classify each migration into a bucket.
3. For any Restrictive or Destructive migration: take a DB backup in the Coolify UI **before** pushing the tag.
4. Note in the release notes which migrations are restrictive or destructive.
5. For Destructive changes: prefer the expand-contract pattern.

### 4.3. Expand-contract pattern

This makes each release independently rollback-safe.

**Concrete example: rename `users.username` to `users.handle`**

- **Wrong way**: one migration drops `username` and adds `handle`. Destructive — code rollback cannot read the old column.
- **Right way**:
  - Release N: add `handle` column; write to **both** on every update; backfill `handle` from `username`; keep both columns readable
  - Release N+1 (after monitoring confirms no code reads `username`): drop `username` in a new migration

Each release is independently rollback-safe by the code-rollback path.

### 4.4. Post-deploy verification

After a release with migrations:
- Backend logs in Coolify show clean startup (no migration errors)
- `/health` returns `200`
- A test login or request works

## 5. Rollback procedure

(REQ-11)

### 5.1. Rollback policy dimensions

| Dimension | Decision |
|-----------|----------|
| DB rollback | Forward-fix only. Never run `flask db downgrade`. For destructive migrations, restore the manual backup taken before the release. |
| Code rollback | Manual via Coolify UI — select the previous stable tag from the deployments list, click **Redeploy**. |
| Detection | Post-deploy smoke test in `release.yml`. On failure, a GitHub issue is created automatically. |
| Traceability | GitHub Releases page is the source of truth. No `stable` tag, no `STABLE_VERSION` file, no manual log. |

### 5.2. 5-step rollback runbook

1. Identify the broken release tag and the last known-good tag from the GitHub Releases page.
2. Coolify UI → backend (and frontend separately) → deployments → click the previous good tag → **Redeploy**.
3. Wait ~2 minutes, then verify:
   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" https://api.prodescaloneta.online/health
   ```
   Expect `200`.
4. If the broken release included a destructive migration: restore the DB backup taken before that release via the Coolify UI.
5. Post-mortem (in calm time): optionally run `gh release edit <good-tag> --latest` to fix the "Latest" marker; write a forward-fix PR; document the incident.

### 5.3. When smoke test fails

If the smoke test fails, the `notify-failure` job opens a GitHub issue with:
- Title: `🚨 Smoke test failed for vX.Y.Z`
- Body: link to the workflow run
- Labels: `release`, `incident`

Triage:
1. Open the workflow run and inspect the `smoke-test` job logs.
2. Check Coolify → backend → deployments for the last deploy status.
3. If production is broken, follow the 5-step rollback runbook above.
4. If the deploy is still in progress, wait and re-run the smoke test manually.

## 6. Coolify troubleshooting

### 6.1. Webhook returns non-2xx

- Verify the secret is correct in GitHub → Settings → Secrets and variables → Actions.
- Verify the Coolify token still exists and has `deploy` + `write` scopes.
- Manually test the webhook with curl (without revealing the secret):
  ```bash
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST \
    -H "Authorization: Bearer <token>" \
    <webhook_url>
  ```
- Check Coolify logs for inbound webhook receipt.

### 6.2. Deploy fails after webhook trigger

- Coolify UI → deployments → click the failed deploy → view build logs.
- Common causes: missing env var, build error, container OOM.
- For env var changes: you must **redeploy** after editing — env vars are injected at container start.

### 6.3. Smoke test fails on /health

- Check Coolify → backend → deployments → status of the last deploy.
- If deploy shows "Running" or "Success" but `/health` fails: the deployed code may not include the `/health` endpoint (verify the git ref Coolify is pointing at).
- If deploy shows "Failed": fix the failed deploy first.

## 7. Secrets rotation runbook

(T-15-ter)

### 7.1. When to rotate

- Suspected leak (shared `.env` via screen share, accidental paste, etc.)
- Scheduled rotation (recommended every 6–12 months)
- Team member offboarding

### 7.2. Secrets in production

- `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`: Google OAuth credentials
- `JWT_SECRET`: signs user session tokens
- `SECRET_KEY`: Flask session signing
- `INGESTION_SECRET`: webhook auth for data ingestion

### 7.3. Safe rotation procedure (zero downtime)

#### Google OAuth (`GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`)

1. Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client IDs.
2. Click your client → **"Add another secret"** (do NOT delete the old one yet).
3. Copy the new client secret.
4. Coolify → backend → Environment Variables → update `GOOGLE_CLIENT_SECRET`.
5. Redeploy backend.
6. Test login with a real Google account.
7. If login works: return to Google Cloud Console, **DELETE** the old secret.
8. If login fails: revert in Coolify to the old secret, redeploy, debug.

#### `JWT_SECRET`

**WARNING**: rotating `JWT_SECRET` invalidates **all** currently issued tokens. Every logged-in user is logged out and must re-login. No data is lost.

1. Generate a new secret:
   ```bash
   openssl rand -hex 32
   ```
2. Coolify → backend → Environment Variables → update `JWT_SECRET`.
3. Redeploy backend.
4. Users will be silently logged out on their next request.

#### `SECRET_KEY` (Flask)

Similar to `JWT_SECRET`: invalidates signed cookies. Users re-login.

1. Generate a new secret:
   ```bash
   openssl rand -hex 32
   ```
2. Coolify → backend → Environment Variables → update `SECRET_KEY`.
3. Redeploy backend.

#### `INGESTION_SECRET`

Only affects the webhook ingest endpoint, not user sessions.

1. Generate a new secret:
   ```bash
   openssl rand -hex 32
   ```
2. Update on **both** ends simultaneously:
   - Coolify → backend → Environment Variables → `INGESTION_SECRET`
   - The source of the webhook (whoever calls it)
3. Redeploy backend.

### 7.4. After rotation

- Update local `.env` files on all developer machines.
- Note the rotation date in this runbook or a separate audit log.
- If suspected compromise: also check application logs for suspicious activity around the suspected exposure date.

## 8. First release: cutting v1.1.0

(T-16, deferred to manual execution)

This is the end-to-end validation of the entire pipeline.

### 8.1. Prerequisites

- [ ] `release-strategy` merged to `main`
- [ ] Coolify deployed `main` manually (button) and verified:
  - [ ] `/health` returns `200`
  - [ ] Frontend loads at `https://prodescaloneta.online`
  - [ ] Login still works
  - [ ] CORS header shows `https://prodescaloneta.online` (with `https://`)
- [ ] All GitHub Actions secrets configured (verify in Settings → Secrets):
  - `COOLIFY_BACKEND_WEBHOOK_URL`
  - `COOLIFY_FRONTEND_WEBHOOK_URL`
  - `COOLIFY_WEBHOOK_TOKEN`
- [ ] Hand-curated `CHANGELOG.md` is up-to-date (technical, derived from commits)
- [ ] User-facing `backend/app/changelog.json` has an entry for the new version (see section 1.1)

### 8.2. Cutting v1.1.0

1. `git checkout main && git pull`
2. `scripts/release.sh minor` (or `patch` if the intent is a bug-fix release)
3. Inspect the changes:
   ```bash
   git show HEAD
   ```
   Should show only the `VERSION` bump and a conventional commit.
4. `git push --follow-tags`
5. Watch GitHub Actions: `https://github.com/leaiannotti/prode-worldcup-2026/actions`
6. Verify the release: `https://github.com/leaiannotti/prode-worldcup-2026/releases`
7. Verify deploys in Coolify (backend + frontend)
8. Smoke test should pass automatically (~90s after deploy)

### 8.3. If something fails

- **Workflow fails before tests**: `VERSION` mismatch — fix the `VERSION` file, force-push the tag (rare).
- **Tests fail**: fix the test or code, then do a new patch release.
- **Coolify webhook fails**: check the issue auto-created, fix the secret, manually deploy via Coolify UI.
- **Smoke test fails**: an issue is auto-created with details. Follow the rollback procedure if production is broken.

### 8.4. Success criteria

- [ ] GitHub Release page shows `v1.1.0` with auto-generated changelog
- [ ] Both Coolify apps show the new deploy
- [ ] `/health` returns `200`
- [ ] Frontend works in browser
- [ ] No incident issue was opened

## 9. Glossary

- **Cut a release**: bump `VERSION`, create tag, push — triggers the automated release pipeline.
- **Tracker branch**: the long-lived branch where chained PRs accumulate before merging to `main` (during this change: `release-strategy`).
- **Forward-fix**: fixing a bug by shipping a new release with the fix, not by reverting or downgrading.
- **Expand-contract**: schema migration pattern where each release is rollback-safe (one release adds, the next release removes after monitoring).
- **Conventional commit**: commit message format `type(scope): description` enforced by Husky + commitlint.
- **Smoke test**: minimal post-deploy probe to detect catastrophic failures.
- **Hotfix**: emergency release for a critical bug, typically a small patch.

## See also

- [proposal](../openspec/changes/release-strategy/proposal.md) (during the change; will be archived)
- [.github/workflows/release.yml](../.github/workflows/release.yml) — actual release workflow
- [.github/workflows/ci.yml](../.github/workflows/ci.yml) — PR test gate
- [scripts/release.sh](../scripts/release.sh) — release helper
- [cliff.toml](../cliff.toml) — changelog generator config
- [commitlint.config.js](../commitlint.config.js) — commit message rules
