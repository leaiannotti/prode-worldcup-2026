# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - YYYY-MM-DD

### Features
- Add `/health` endpoint to backend for smoke tests
- Make backend CORS origin env-driven from `FRONTEND_URL`
- Add commit-msg Husky hook with commitlint
- Add delete league with confirmation and fix rank badge light mode
- Add argentinization, admin panel, community insights, email auth, page loader and production fixes

### Bug Fixes
- Ensure `users.google_sub` is nullable
- Case-insensitive invite codes
- Preserve activity events when deleting prediction group
- Refresh standing widget after creating or joining a league
- Correct `/partidos` route to `/matches`
- Read `FRONTEND_URL` from env in `BaseConfig`
- Add `OAUTH_REDIRECT_URI` to `ProductionConfig`
- Use `VITE_API_URL` for all direct fetch calls in production
- Safe migrations for fresh DB + entrypoint script
- Hide page loader on login route
- Move `apiBase` to script setup to avoid template parse error
- Use `VITE_API_URL` for auth endpoints in production
- Add email-validator dependency for pydantic
- Add CORS support for production domain
- Include `frontend/src/lib` in git (was excluded by gitignore)
- Skip migrations on fresh DB, use `create_all` instead
- Include `jsons` in backend for production deploy

### Documentation
- Document `FRONTEND_URL` requirement in `.env.example`
- Add rollback policy to release-strategy plan
- Add release-strategy change artifacts

### Maintenance
- Add git-cliff changelog configuration
- Add commitlint configuration
- Add Husky and commitlint dependencies
- Initialize `VERSION` at `1.1.0`
- Mark slice A, B, and C tasks complete

### CI/Build
- Add PR test gate workflow for `main` and `release-strategy`
- Add frontend Dockerfile and nginx config for production
- Produccionizar backend con gunicorn

## [1.0.0] - 2026-06-09

Initial release.
