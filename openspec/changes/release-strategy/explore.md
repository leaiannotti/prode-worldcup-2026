## Exploration: Release Strategy for prode-worldcup-2026

### Current State

The repository is a **monorepo** containing two applications:
- **Frontend**: Vue 3 + Vite + TypeScript (package version `0.1.0`)
- **Backend**: Python Flask + SQLAlchemy + Alembic (no version file; only `requirements.txt`)

**Deployment**: The application is currently hosted on **Coolify** on the user's VPS, serving the production domain `prodescaloneta.online`. The CORS configuration in `backend/app/__init__.py` hardcodes this domain. There is **no GitHub Actions CI/CD**, no existing `CHANGELOG`, and no automated release infrastructure.

**Commits**: There is partial adoption of **Conventional Commits** (`feat:`, `fix:`, `chore:`, `docs:`). Out of ~40 commits, roughly 30 follow the convention. However, there are also non-conventional commits (e.g., `nuevos cambios`, `debug: log FRONTEND_URL`, merge commits). The single existing tag is `v1.0.0`, placed on a commit titled `nuevos cambios` (not a conventional commit). There are **22 commits on `main` since `v1.0.0`**, including multiple bug fixes and a large feature (`feat: argentinization, admin panel, community insights, email auth, page loader and production fixes`).

**Environments**: 
- **Dev**: Local development using `docker-compose.yml` (db + backend) and Vite dev server for frontend. Uses `.env` file with `FLASK_ENV=development`.
- **Prod**: Coolify deployment. The `frontend/Dockerfile` builds a production bundle served by nginx, and the `backend/Dockerfile` runs gunicorn via `entrypoint.sh` (which runs `flask db upgrade` then starts gunicorn). There is **no staging or preview environment**.

**Branching**: `main` is the default branch. The current working branch is `release-strategy`. Historical PRs were merged via feature branches (`feat/pr2-auth`, `feat/pr3-core-backend`, `feat/pr4-leaderboard-history`). The current pattern appears to be **feature branches merged into `main` via PRs**.

---

### Affected Areas

- `frontend/package.json` — contains version `0.1.0`, needs to be versioned or removed if using unified repo versioning
- `backend/` — no version tracking; needs a version file or unified repo versioning
- `.github/workflows/` — does not exist yet; needs to be created for any automated release or CI
- `frontend/Dockerfile` — already production-ready; will be triggered by Coolify on tag or branch push
- `backend/Dockerfile` + `entrypoint.sh` — already production-ready; runs migrations on startup
- `backend/app/__init__.py` — hardcodes production CORS origin `prodescaloneta.online`; needs to be env-driven for multi-env
- `.env.example` — documents local dev env vars; does not distinguish prod vs dev
- `README.md` — documents manual setup but no deployment/release process

---

### Approaches

#### 1. **GitHub Actions + Manual Tag + Coolify Webhook**
- **Description**: Create a simple GitHub Actions workflow that runs tests on every PR. On a manually pushed tag (e.g., `v1.1.0`), the workflow creates a GitHub Release and generates a changelog from commit messages. Coolify is configured to auto-deploy on new tags.
- **Pros**: 
  - Minimal complexity; no new tools to learn
  - Full control over when a release happens
  - Coolify can natively trigger on tag push
  - Changelog can be generated via `git log` or a simple script
- **Cons**: 
  - Manual changelog generation is error-prone
  - No versioning automation; human must decide version bump
  - Commit messages are not consistently conventional, making automated changelogs messy
- **Effort**: Low

#### 2. **release-please (Google) + Conventional Commits**
- **Description**: Adopt `release-please` (GitHub Action) which opens a "Release PR" on every conventional commit. The PR accumulates changes and version bumps. When the PR is merged, a GitHub Release and changelog are auto-generated. Coolify can deploy on the new tag.
- **Pros**: 
  - Industry-standard, PR-based review of releases
  - Auto-generates changelogs and version bumps
  - Integrates cleanly with GitHub Releases
  - Encourages enforcing conventional commits
- **Cons**: 
  - Requires strict conventional commits (currently ~75% compliance)
  - `release-please` has a learning curve and config file
  - Monorepo support requires manifest mode (slightly more complex)
  - May feel heavy for a single-developer project
- **Effort**: Medium

#### 3. **semantic-release**
- **Description**: Full automation on every push to `main`. `semantic-release` analyzes commits, bumps version, generates changelog, creates GitHub Release, and pushes tag. No human intervention.
- **Pros**: 
  - Fully automated; zero manual release steps
  - Rich plugin ecosystem (npm, GitHub, Docker, etc.)
- **Cons**: 
  - Requires 100% conventional commit discipline
  - May create too many releases for a single-developer project
  - Less control over release timing
  - Monorepo support is complex (requires `semantic-release-monorepo` or independent packages)
- **Effort**: Medium–High

#### 4. **Changesets (Atlassian-style)**
- **Description**: Developer adds a `.changeset/*.md` file describing intent with each meaningful change. A GitHub Action later aggregates these into a "Version Packages" PR, which updates versions and changelogs. When merged, a release is cut.
- **Pros**: 
  - Excellent for monorepos (supports per-package versioning)
  - No dependency on commit message discipline
  - Human-curated changelogs (high quality)
- **Cons**: 
  - More manual steps per change (add a changeset file)
  - Overkill for a single-developer project with two packages
  - Another tool and concept to learn
- **Effort**: Medium

---

### Recommendation

**Recommended direction**: **Approach 1 (GitHub Actions + Manual Tag) as a stepping stone, with a clear path to Approach 2 (release-please) once commit discipline is enforced.**

Reasoning:
- The project is **single-developer**, so the overhead of `release-please` or `changesets` is not yet justified.
- The immediate need is **reliable releases** and **changelogs**, not maximum automation.
- Manual tagging gives the user control over release timing, which is important during an active World Cup season (avoid accidental deploys).
- The commit history is **not yet clean enough** for `semantic-release` or `release-please` to work perfectly.
- A simple GitHub Action workflow can be created in one session, and the user can start releasing immediately.

**Path to improvement**: Enforce conventional commits in the next few PRs (e.g., via a PR template or a local git hook). Once discipline is >90%, migrate to `release-please` for full automation.

---

### Risks

- **Commit message inconsistency**: Automated tools will produce poor changelogs if commit messages remain inconsistent. A one-time cleanup or a commit-msg hook is needed.
- **No tests in CI**: Currently no CI runs tests. A release workflow that does not run tests before tagging is risky. The first CI workflow should run `pytest` and `vitest run`.
- **Database migrations on deploy**: The `entrypoint.sh` runs `flask db upgrade` on every container start. This is safe for additive migrations but risky for destructive ones. The release strategy should include a "migration safety" checklist.
- **Single environment**: Without staging, a bad release goes directly to production. Consider a `staging` branch or a Coolify preview deployment if possible.
- **Version drift**: The frontend `package.json` says `0.1.0` while the tag is `v1.0.0`. If adopting unified repo versioning, the `package.json` version should be removed or kept in sync.
- **Secrets in `.env`**: The committed `.env` file contains real Google OAuth credentials and secrets. This is a security risk and should be addressed (add `.env` to `.gitignore` and rotate secrets). The release strategy document should not expose these.

---

### Ready for Proposal

**Yes**, with the following clarifications needed from the user before the proposal phase:

1. **Versioning strategy**: Do you want a single unified version for the whole repo (e.g., `v1.1.0`), or separate versions for frontend and backend?
2. **Staging environment**: Do you want a staging/preview environment on Coolify, or is `prod + local dev` enough for now?
3. **Release cadence**: Do you want to release on every bug fix, or bundle fixes into weekly/bi-weekly releases?
4. **Commit discipline**: Are you willing to enforce conventional commits (e.g., `feat:`, `fix:`) going forward, or do you prefer a manual approach that doesn't depend on commit messages?

---

### Open Questions

- Should the user clean up the existing commit history or just enforce discipline going forward?
- Is Coolify configured to auto-deploy on tag push, or does it currently deploy on `main` branch push?
- Does the user want GitHub Releases to include built Docker images or just source code?
- Should the `.env` file be removed from git history and secrets rotated?

---

### Key Findings Summary

| Dimension | Finding |
|-----------|---------|
| **Monorepo** | Yes — frontend (npm) + backend (pip) |
| **CI/CD** | None — no `.github/workflows/` |
| **Conventional Commits** | Partial (~75% compliance) |
| **Tags/Releases** | One tag: `v1.0.0` (on non-conventional commit) |
| **Changelog** | None |
| **Docker** | Both apps have production-ready Dockerfiles |
| **Hosting** | Coolify on VPS, domain `prodescaloneta.online` |
| **Environments** | Dev (local) + Prod (Coolify); no staging |
| **Migrations** | Auto-run on container startup (`entrypoint.sh`) |
| **Secrets** | `.env` file is committed (security risk) |

---

*Generated by SDD Explore phase for change `release-strategy`.*
