# Archive Report: Release Strategy

## Date Archived

2026-06-13

## Final Outcome

**v1.1.0 released successfully** on 2026-06-12 via the new tag-triggered release pipeline.

- Tag SHA: `52cf27f` (latest on `main` at archive time)
- GitHub Release: v1.1.0 published with auto-generated changelog
- Coolify deployed the tagged version within ~10 minutes
- Production smoke tests passed

## Production Verification

| Endpoint | Expected | Result |
|----------|----------|--------|
| `https://api.prodescaloneta.online/health` | 200 | PASS |
| `https://api.prodescaloneta.online/api/auth/me` | 401 | PASS |
| `https://prodescaloneta.online/` | 200 | PASS |

## Total PRs

7 PRs were created and merged as part of this change:

| PR | Slice | Description |
|----|-------|-------------|
| #77 | Slice A | Foundations — gitignore, Husky, commitlint, VERSION |
| #85 | Slice B | Backend env-driven CORS |
| #86 | Slice C | CI workflow |
| #88 | Slice D | Release pipeline + changelog + release.sh + smoke test |
| #89 | Fix | Split Coolify notify into backend and frontend webhooks |
| #90 | Slice E | Docs + rollback runbook |
| #92 | Integration | Merge all slices to `main` |

## Tasks Completed vs Deferred

| Task | Status | Notes |
|------|--------|-------|
| T-01 | Completed | gitignore verified |
| T-02 | Deferred | Secrets rotation (deferred to post-release; rotated via manual action) |
| T-03 | Completed | Root package.json + Husky + commitlint |
| T-04 | Completed | commitlint.config.js |
| T-05 | Completed | .husky/commit-msg hook |
| T-06 | Completed | Root VERSION file |
| T-07 | Completed | Backend CORS env-driven |
| T-08 | Completed | .env.example FRONTEND_URL docs |
| T-09 | Completed | CI workflow |
| T-10 | Completed | git-cliff config |
| T-11 | Completed | Initial CHANGELOG.md |
| T-12 | Completed | release.yml with validate, tests, changelog, release, notify |
| T-12-bis | Completed | Smoke test + notify-failure jobs |
| T-12-ter | Completed | /health endpoint added |
| T-13 | Completed | scripts/release.sh |
| T-14 | Completed | Coolify webhook configured |
| T-15 | Completed | docs/RELEASE.md |
| T-15-bis | Completed | Rollback runbook |
| T-15-ter | Completed | Secrets rotation runbook |
| T-16 | Completed | End-to-end test v1.1.0 (executed manually; task was marked deferred in tasks.md but was completed during release) |

**Reconciliation note**: T-16 was marked `⏸ DEFERRED` in the persisted tasks artifact because the e2e test was scheduled to run after the `release-strategy` branch merged to `main`. The e2e test was successfully executed on 2026-06-12 as part of the v1.1.0 release, and all production verification endpoints passed. This archive report corrects the task status to **Completed**.

## Lessons Learned

### 1. cliff.toml `github.contributors` footer bug

`git-cliff` v1.x ships with a default template that includes a `github.contributors` footer. When the GitHub token is not configured or the repository has no contributor metadata, the release body generation fails silently or produces an empty release body. The fix was a hotfix commit `52cf27f` that removed the unused footer from `cliff.toml`.

**Takeaway**: Always validate the first auto-generated release body on a test repo or dry-run before the first real tag.

### 2. `/env` claim in CORS

The initial design claimed the backend would read `FRONTEND_URL` from the environment. During implementation, we discovered that the `backend/app/__init__.py` already had a partially env-driven setup, but the `/env` endpoint was leaking environment variables. The fix was to remove the `/env` endpoint entirely and ensure CORS origins were read only from `FRONTEND_URL` at startup.

**Takeaway**: Any "env inspection" endpoint is a security risk; remove it rather than restrict it.

### 3. Deferred T-02 secrets rotation

Secrets rotation was deferred to post-release. The old `.env` values remain in git history, but the new credentials are active in Coolify and the local `.env` file. Future projects should rotate secrets BEFORE the first release, not after.

**Takeaway**: Treat secrets rotation as a prerequisite for any release, not a post-release cleanup.

### 4. Dual Coolify webhooks

The original design assumed a single Coolify webhook would trigger both backend and frontend redeploys. In practice, Coolify required separate webhook URLs for each service. PR #89 fixed this by splitting the `notify` step into two `curl` calls.

**Takeaway**: Verify webhook behavior with a manual `curl` before wiring it into the release workflow.

## Links

- GitHub Release v1.1.0: https://github.com/leaiannotti/prode-worldcup-2026/releases/tag/v1.1.0
- PR #77 (Slice A): https://github.com/leaiannotti/prode-worldcup-2026/pull/77
- PR #85 (Slice B): https://github.com/leaiannotti/prode-worldcup-2026/pull/85
- PR #86 (Slice C): https://github.com/leaiannotti/prode-worldcup-2026/pull/86
- PR #88 (Slice D): https://github.com/leaiannotti/prode-worldcup-2026/pull/88
- PR #89 (Fix): https://github.com/leaiannotti/prode-worldcup-2026/pull/89
- PR #90 (Slice E): https://github.com/leaiannotti/prode-worldcup-2026/pull/90
- PR #92 (Integration): https://github.com/leaiannotti/prode-worldcup-2026/pull/92
- Issue #87 (Follow-up): https://github.com/leaiannotti/prode-worldcup-2026/issues/87

## Archive Contents

- `explore.md` — Exploration findings and current state analysis
- `proposal.md` — Change proposal with scope, approach, and risks
- `design.md` — Technical design, architecture decisions, and rollout plan
- `specs/release-pipeline/spec.md` — Delta spec (11 requirements, 30+ scenarios)
- `tasks.md` — Task breakdown with completion status and commit references
- `archive-report.md` — This file

## Source of Truth

The canonical spec for the `release-pipeline` capability is now at:

```
openspec/specs/release-pipeline/spec.md
```

This archive preserves the delta spec for historical traceability.

---

*Archived by SDD Archive phase on 2026-06-13.*
