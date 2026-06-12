# Tasks: Release Strategy

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~555 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | 5 slices (see below) |
| Delivery strategy | ask-always |
| Chain strategy | feature-branch-chain |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Tasks | PR | Focus | Est. Lines |
|------|-------|----|-------|------------|
| A | T-01, T-03–T-06 | PR 1 | Hygiene + foundations (gitignore, Husky, commitlint, VERSION) | ~24 |
| B | T-07, T-08 | PR 2 | Backend env-driven CORS | ~13 |
| C | T-09 | PR 3 | CI workflow | ~40 |
| D | T-10–T-13, T-12-bis | PR 4 | Release pipeline + changelog + release.sh + smoke test | ~195 |
| E | T-15, T-15-bis, T-16 | PR 5 | Docs + rollback runbook + e2e test | ~280 |

**Manual actions** (T-02, T-14) run outside PRs and must complete before Slice E.

---

## Phase 1: Git Hygiene Verification

### T-01: Verify .env is untracked and .gitignore is complete
- **Files**: `.gitignore` (verify), `.env` (verify not tracked)
- **Depends on**: none
- **Spec coverage**: REQ-8
- **Verification**:
  - `git ls-files | grep -E "^\.env$"` returns empty
  - `cat .gitignore | grep -E "^\.env"` shows `.env` and `.env.*` patterns
  - If gaps found, add `.env` and `.env.*` to `.gitignore`
- **Estimated changed lines**: 0–3
- **Manual or automated**: AUTOMATED
- **Commit message**: `chore: verify .env gitignore patterns`

## Phase 2: Secrets Rotation

### T-02: Rotate secrets in Google Cloud Console and Coolify
- **Files**: none (UI-based actions)
- **Depends on**: T-01
- **Spec coverage**: REQ-8
- **Verification**:
  - Google Cloud Console → APIs & Services → Credentials → regenerate OAuth 2.0 Client ID/Secret
  - `JWT_SECRET`, `SECRET_KEY`, `INGESTION_SECRET` regenerated as random strings
  - Coolify project env vars updated with new values
  - `.env` file locally updated with new values
  - Old credentials invalidated (test a login to confirm new ones work)
- **Estimated changed lines**: 0
- **Manual or automated**: MANUAL
- **Commit message**: N/A

## Phase 3: Commitlint & Husky

### T-03: Create root package.json with Husky and commitlint dependencies
- **Files**: `package.json` (new, root)
- **Depends on**: T-01
- **Spec coverage**: REQ-5
- **Verification**:
  - `npm install` succeeds at repo root
  - `npx husky --version` prints a version
  - `npm run prepare` executes `husky` without error
- **Estimated changed lines**: ~15
- **Manual or automated**: AUTOMATED
- **Commit message**: `chore: add husky and commitlint dependencies`

### T-04: Create commitlint.config.js
- **Files**: `commitlint.config.js` (new, root)
- **Depends on**: T-03
- **Spec coverage**: REQ-5
- **Verification**:
  - `echo "feat: test" | npx commitlint --config commitlint.config.js` passes
  - `echo "nuevos cambios" | npx commitlint --config commitlint.config.js` fails with type error
  - Merge commit message `Merge pull request #42` is ignored (defaultIgnores: true)
- **Estimated changed lines**: ~5
- **Manual or automated**: AUTOMATED
- **Commit message**: `chore: add commitlint configuration`

### T-05: Create .husky/commit-msg hook
- **Files**: `.husky/commit-msg` (new)
- **Depends on**: T-04
- **Spec coverage**: REQ-5
- **Verification**:
  - `git commit --allow-empty -m "feat: test hook"` succeeds
  - `git commit --allow-empty -m "bad message"` fails with commitlint error
  - `npx commitlint --edit .git/COMMIT_EDITMSG` works via the hook
- **Estimated changed lines**: ~3
- **Manual or automated**: AUTOMATED
- **Commit message**: `chore: add commit-msg husky hook`

## Phase 4: Versioning

### T-06: Create root VERSION file
- **Files**: `VERSION` (new, root)
- **Depends on**: none
- **Spec coverage**: REQ-3
- **Verification**:
  - `cat VERSION` prints `1.1.0` (no `v` prefix)
  - `git tag v1.1.0` matches when `cat VERSION | sed 's/^/v/'` is compared
- **Estimated changed lines**: 1
- **Manual or automated**: AUTOMATED
- **Commit message**: `chore: initialize VERSION at 1.1.0`

## Phase 5: Backend CORS Refactor

### T-07: Refactor backend CORS to env-driven and remove hardcoded domains
- **Files**: `backend/app/__init__.py`
- **Depends on**: T-06
- **Spec coverage**: REQ-7
- **Verification**:
  - RED: Write failing test `backend/tests/test_cors.py` asserting CORS origin equals `FRONTEND_URL` env var
  - GREEN: Modify `backend/app/__init__.py` to remove hardcoded `prodescaloneta.online` lines; use `os.getenv("FRONTEND_URL")` with fallback to `http://localhost:5173`; fail fast in production when `FRONTEND_URL` is unset
  - Test passes: `pytest backend/tests/test_cors.py -v`
  - Existing test suite passes: `pytest backend/`
- **Estimated changed lines**: ~8
- **Manual or automated**: AUTOMATED
- **Commit message**: `feat: make backend CORS origin env-driven`

### T-08: Update .env.example with FRONTEND_URL documentation
- **Files**: `.env.example`
- **Depends on**: T-07
- **Spec coverage**: REQ-7, REQ-8
- **Verification**:
  - `.env.example` contains `FRONTEND_URL` with a comment explaining it is required in production
  - No real secrets present; all values are placeholders
- **Estimated changed lines**: ~5
- **Manual or automated**: AUTOMATED
- **Commit message**: `docs: document FRONTEND_URL requirement in .env.example`

## Phase 6: CI Workflow

### T-09: Create .github/workflows/ci.yml
- **Files**: `.github/workflows/ci.yml` (new)
- **Depends on**: T-07, T-08
- **Spec coverage**: REQ-1
- **Verification**:
  - `actionlint` (if installed) or manual YAML validation passes
  - Workflow triggers on PR to `main`; path filters for `backend/**` and `frontend/**`
  - Backend job runs `pip install -r backend/requirements.txt && pytest backend/`
  - Frontend job runs `npm ci && npm run test` in `frontend/`
  - Manual dry-run via `act` (optional) or push to a test branch and open PR to verify
- **Estimated changed lines**: ~40
- **Manual or automated**: AUTOMATED
- **Commit message**: `ci: add PR test gate workflow`

## Phase 7: Changelog Tool

### T-10: Create git-cliff config (cliff.toml)
- **Files**: `cliff.toml` (new, root)
- **Depends on**: none
- **Spec coverage**: REQ-4
- **Verification**:
  - `git-cliff --config cliff.toml --from v1.0.0 --to HEAD` outputs grouped changelog (feat, fix, chore, docs, BREAKING)
  - Groups match design: `["feat", "Features"]`, `["fix", "Bug Fixes"]`, etc.
  - `cargo install git-cliff` or use pre-built binary to test locally
- **Estimated changed lines**: ~30
- **Manual or automated**: AUTOMATED
- **Commit message**: `chore: add git-cliff changelog configuration`

### T-11: Generate initial CHANGELOG.md
- **Files**: `CHANGELOG.md` (new, root)
- **Depends on**: T-10
- **Spec coverage**: REQ-4
- **Verification**:
  - `CHANGELOG.md` exists at root with a hand-curated entry for `v1.0.0` → `v1.1.0`
  - Historical commits (22 since `v1.0.0`) are grouped by type
  - Future releases will append automatically via `git-cliff`
- **Estimated changed lines**: ~50
- **Manual or automated**: AUTOMATED
- **Commit message**: `docs: add initial CHANGELOG.md`

## Phase 8: Release Workflow

### T-12: Create .github/workflows/release.yml
- **Files**: `.github/workflows/release.yml` (new)
- **Depends on**: T-09, T-11
- **Spec coverage**: REQ-2, REQ-3, REQ-4, REQ-6
- **Verification**:
  - Workflow triggers on `v*.*.*` tags
  - Validate step compares `VERSION` to tag name; mismatches fail fast
  - Tests step runs both backend and frontend tests
  - Changelog step runs `git-cliff` and uploads artifact
  - Release step uses `softprops/action-gh-release` with `body_path: CHANGELOG.md`
  - Notify step POSTs to `COOLIFY_WEBHOOK_URL` with `::add-mask::` to hide secrets
  - `actionlint` or manual YAML validation passes
- **Estimated changed lines**: ~60
- **Manual or automated**: AUTOMATED
- **Commit message**: `ci: add tag-triggered release workflow`

### T-12-bis: Add smoke-test + notify-failure jobs to release.yml
- **Files**: `.github/workflows/release.yml`
- **Depends on**: T-12
- **Spec coverage**: REQ-11 (sub-area C — smoke test detection)
- **Verification**:
  - `actionlint` passes; workflow includes `smoke-test` job with 90s sleep + curl probes
  - `notify-failure` job with `if: failure()` creates GitHub issue
- **Estimated changed lines**: ~30
- **Manual or automated**: AUTOMATED
- **Commit message**: `ci: add post-deploy smoke test and incident notification`

### T-13: Create scripts/release.sh
- **Files**: `scripts/release.sh` (new)
- **Depends on**: T-12
- **Spec coverage**: REQ-3
- **Verification**:
  - `scripts/release.sh` accepts `major`, `minor`, or `patch` argument
  - Bumps `VERSION`, commits, and tags atomically (e.g., `v1.1.0`)
  - Prevents mismatched tag/VERSION by doing all three in one commit
  - `bash -n scripts/release.sh` passes syntax check
  - Dry-run shows expected commands without executing (optional flag)
- **Estimated changed lines**: ~25
- **Manual or automated**: AUTOMATED
- **Commit message**: `build: add release helper script`

## Phase 9: Coolify Webhook Configuration

### T-14: Configure Coolify webhook and GitHub Actions secrets
- **Files**: none (UI-based actions)
- **Depends on**: T-12, T-13
- **Spec coverage**: REQ-6
- **Verification**:
  - Coolify UI → Project → Webhooks → create endpoint; copy URL and token
  - GitHub repo → Settings → Secrets and variables → Actions → add `COOLIFY_WEBHOOK_URL` and `COOLIFY_WEBHOOK_TOKEN`
  - Test webhook with `curl` (masked) and confirm Coolify shows incoming request
  - Verify `release.yml` logs do not leak the URL or token
- **Estimated changed lines**: 0
- **Manual or automated**: MANUAL
- **Commit message**: N/A

## Phase 10: Documentation

### T-15: Write docs/RELEASE.md
- **Files**: `docs/RELEASE.md` (new)
- **Depends on**: T-13, T-14
- **Spec coverage**: REQ-9, REQ-10
- **Verification**:
  - `docs/RELEASE.md` exists and covers all 6 sections from design:
    1. How to cut a release (`scripts/release.sh`, push tag, verify GitHub Actions)
    2. Conventional commit guide (allowed types, examples)
    3. Hotfix procedure (branch from tag, fix, PR, patch bump)
    4. Migration safety checklist (backup, local test, rollback)
    5. Coolify troubleshooting (webhook failure, manual redeploy)
    6. Secrets rotation runbook (how to rotate, where to update)
  - `mkdocs` or `README.md` links to `docs/RELEASE.md` (optional)
- **Estimated changed lines**: ~200
- **Manual or automated**: AUTOMATED
- **Commit message**: `docs: add release runbook`

### T-15-bis: Expand docs/RELEASE.md with rollback runbook
- **Files**: `docs/RELEASE.md` (modify the T-15 doc to include rollback section)
- **Depends on**: T-15
- **Spec coverage**: REQ-11 (all sub-areas A/B/C/D)
- **Verification**:
  - `docs/RELEASE.md` contains: forward-fix migration policy, expand-contract example, pre-release migration classification checklist (3 buckets), 5-step rollback runbook, smoke test failure response
- **Estimated changed lines**: ~80
- **Manual or automated**: AUTOMATED
- **Commit message**: `docs: add rollback runbook to release docs`

## Phase 11: End-to-End Verification

### T-16: End-to-end test: cut v1.1.0
- **Files**: none (verification only)
- **Depends on**: T-15, T-02 (secrets must be rotated first)
- **Spec coverage**: REQ-2, REQ-6, REQ-10
- **Verification**:
  - Run `scripts/release.sh patch` or manually push `v1.1.0` tag
  - GitHub Actions `release.yml` runs and succeeds
  - GitHub Release page shows `v1.1.0` with changelog body
  - Coolify receives webhook and deploys the tagged version
  - App smoke test passes (login, submit prediction, view leaderboard)
  - Total time from tag push to deploy is ~10 minutes
- **Estimated changed lines**: 0
- **Manual or automated**: MANUAL
- **Commit message**: N/A

---

## Section 2: Review Workload Forecast

- **Total estimated changed lines**: ~555
- **Risk classification**: High (exceeds 400-line budget)
- **400-line budget risk**: High
- **Chained PRs recommended**: Yes
- **Decision needed before apply**: Yes
- **Delivery strategy**: ask-always
- **Chain strategy**: feature-branch-chain
- **Suggested work-unit PR split**:
  - PR 1 (Slice A): Foundations — ~24 lines
  - PR 2 (Slice B): Backend CORS — ~13 lines
  - PR 3 (Slice C): CI — ~40 lines
  - PR 4 (Slice D): Release pipeline + smoke test — ~195 lines
  - PR 5 (Slice E): Docs + rollback runbook + E2E — ~280 lines

Manual tasks (T-02, T-14) must complete before PR 5. The largest slices are D and E, both staying under 400 lines individually. The 5-slice plan remains valid.

---

## Section 3: Manual Action Inventory

| # | Task | Where | What | How to Verify |
|---|------|-------|------|---------------|
| 1 | Rotate Google OAuth | Google Cloud Console → APIs & Services → Credentials | Regenerate OAuth 2.0 Client ID and Client Secret | Update `.env` and test a login; old credentials should fail |
| 2 | Rotate `JWT_SECRET` | Local terminal | `openssl rand -hex 32` (or similar) | New JWT tokens issued and validated by backend |
| 3 | Rotate `SECRET_KEY` | Local terminal | `openssl rand -hex 32` | Sessions/cookies still work |
| 4 | Rotate `INGESTION_SECRET` | Local terminal | `openssl rand -hex 32` | Webhook ingestion endpoint still authenticates |
| 5 | Update Coolify env vars | Coolify UI → Project → Environment | Add new secrets and `FRONTEND_URL=https://prodescaloneta.online` | Redeploy app and verify login works |
| 6 | Configure Coolify webhook | Coolify UI → Webhooks | Create endpoint; copy URL + token | Test `curl` to URL returns 2xx; Coolify deploys on trigger |
| 7 | Add GitHub secrets | GitHub repo → Settings → Secrets and variables → Actions | `COOLIFY_WEBHOOK_URL`, `COOLIFY_WEBHOOK_TOKEN` | `release.yml` notify step succeeds; logs mask the URL |
| 8 | E2E test cut | Local terminal | Run `scripts/release.sh patch` or push `v1.1.0` tag | GitHub Release created; Coolify deploys; app smoke test passes |
| 9 | Verify smoke test endpoints | Local terminal / browser | Manually curl `/health` and `/api/auth/me` against prod BEFORE adding them as smoke test probes in T-12-bis | `curl` returns 200 for `/health` and 401 for `/api/auth/me` |

**Important**: T-02 (secrets rotation) must be completed BEFORE T-16 (e2e test). The old `.env` values are already in git history; rotating them neutralizes the risk. Item 9 must be completed before T-12-bis so the smoke test workflow does not fail on first run.

---

## Section 4: Dependency Graph

```
T-01 (gitignore verify) ──┬──→ T-03 (package.json) ──→ T-04 (commitlint) ──→ T-05 (Husky hook)
                          │
                          └──→ T-02 (secrets rotation MANUAL) ─────────────────────────────────────┐
                                                                                                  │
T-06 (VERSION file) ───────────────────────────────────────────→ T-07 (CORS refactor) ──→ T-08 (.env.example)
                                                                                                  │
                                                                                                  ↓
                                                                                          T-09 (CI workflow)
                                                                                                  │
                                                                                                  ↓
                                                                                          T-10 (cliff.toml) ──→ T-11 (CHANGELOG.md)
                                                                                                  │
                                                                                                  ↓
                                                                                           T-12 (release.yml) ──→ T-12-bis (smoke test) ──→ T-13 (release.sh)
                                                                                                   │
                                                                                                   ↓
                                                                                           T-14 (Coolify webhook MANUAL)
                                                                                                   │
                                                                                                   ↓
                                                                                           T-15 (docs/RELEASE.md) ──→ T-15-bis (rollback runbook)
                                                                                                   │
                                                                                                   ↓
                                                                                           T-16 (e2e test MANUAL)
```

**Key dependencies**:
- T-02 is independent of code but must finish before T-16 (e2e needs new secrets)
- T-03, T-04, T-05 form a chain (Husky setup)
- T-07, T-08 form a chain (CORS + env docs)
- T-10, T-11 form a chain (cliff config → changelog)
- T-12, T-12-bis, T-13 form a chain (release workflow → smoke test → helper script)
- T-14 must happen after T-12 because it tests the webhook defined in `release.yml`
- T-15 is the documentation capstone; depends on T-13 (script) and T-14 (webhook)
- T-15-bis extends T-15 with rollback runbook
- T-16 is the final verification; depends on everything plus manual T-02

---

## Section 5: Strict TDD Mode Applicability

Project capability: `strict_tdd: true` (from SDD init).

| Task | TDD Required? | Rationale | TDD Steps |
|------|--------------|-----------|-----------|
| T-01 | No | Git hygiene check; no code to test | — |
| T-02 | No | Manual secrets rotation | — |
| T-03 | No | Config file (package.json) | — |
| T-04 | No | Config file (commitlint) | — |
| T-05 | No | Hook script | — |
| T-06 | No | Single-line file | — |
| T-07 | **Yes** | Code change in `backend/app/__init__.py` with verifiable behavior | RED: Write `backend/tests/test_cors.py` asserting CORS origin is `FRONTEND_URL` env var; GREEN: Refactor `__init__.py` to remove hardcoded domains; REFACTOR: Ensure test suite passes |
| T-08 | No | Documentation file (.env.example) | — |
| T-09 | No | YAML workflow; tested via dry-run | — |
| T-10 | No | TOML config file | — |
| T-11 | No | Markdown file; verified by inspection | — |
| T-12 | No | YAML workflow; tested via dry-run | — |
| T-12-bis | No | YAML workflow; manual dry-run | — |
| T-13 | No | Shell script; syntax checked by `bash -n` | — |
| T-14 | No | Manual UI configuration | — |
| T-15 | No | Documentation file | — |
| T-15-bis | No | Documentation | — |
| T-16 | No | Manual end-to-end verification | — |

**Only T-07 requires strict TDD**. The test should verify:
1. `FRONTEND_URL` env var is used as the CORS origin when set.
2. Production fails fast if `FRONTEND_URL` is unset.
3. Local dev defaults to `http://localhost:5173` when `FRONTEND_URL` is not set.

All other tasks are configuration, documentation, or manual actions that do not have unit-testable code changes.

---

## Slice A Progress

| Task | Status | Commit |
|------|--------|--------|
| T-01 | ✅ DONE | no change needed (gitignore already complete) |
| T-03 | ✅ DONE | `ab8ffee` — chore: add husky and commitlint dependencies |
| T-04 | ✅ DONE | `3a6d56c` — chore: add commitlint configuration |
| T-05 | ✅ DONE | `faffbad` — chore: add commit-msg husky hook |
| T-06 | ✅ DONE | `a46aa33` — chore: initialize VERSION at 1.1.0 |

## Slice B Progress

| Task | Status | Commit |
|------|--------|--------|
| T-07 | ✅ DONE | `ededaa7` — feat(backend): make CORS origin env-driven from FRONTEND_URL |
| T-08 | ✅ DONE | `628fe44` — docs: document FRONTEND_URL requirement in .env.example |
