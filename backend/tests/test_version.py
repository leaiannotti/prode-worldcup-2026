"""Tests for /api/version and /api/changelog endpoints."""
import json
from pathlib import Path

from app.blueprints import version as version_bp


# Repo-root VERSION file. The release workflow validates that the git tag
# matches this file; we validate that the changelog's first entry matches it,
# so the version surfaced to the frontend stays consistent with the released tag.
_REPO_ROOT_VERSION = Path(__file__).resolve().parent.parent.parent / "VERSION"
_CHANGELOG = Path(__file__).resolve().parent.parent / "app" / "changelog.json"


class TestVersionEndpoint:
    """GET /api/version — public endpoint exposing the current app version."""

    def setup_method(self):
        # Reset cached changelog between tests so changes to the JSON are picked up.
        version_bp._load_changelog.cache_clear()

    def test_returns_200_with_version(self, client):
        resp = client.get("/api/version")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "version" in data
        assert isinstance(data["version"], str)
        assert data["version"]

    def test_no_auth_required(self, client):
        # Endpoint is intentionally public so unauthenticated app boots can fetch it.
        resp = client.get("/api/version")
        assert resp.status_code == 200

    def test_version_matches_repo_root_version_file(self, client):
        """The version surfaced via the API must match the repo-root VERSION file.

        VERSION is the source of truth validated by the release workflow against
        the git tag. If this assertion fails, the changelog drifted from VERSION
        and the release pipeline will eventually fail too — fail loudly here.
        """
        if not _REPO_ROOT_VERSION.exists():
            # Skip in environments where the repo root is not present
            # (e.g. running tests inside a container with only ./backend).
            return
        expected = _REPO_ROOT_VERSION.read_text().strip()
        resp = client.get("/api/version")
        assert resp.get_json()["version"] == expected, (
            f"Changelog first entry version ({resp.get_json()['version']}) "
            f"drifted from repo-root VERSION file ({expected}). "
            f"Update {_CHANGELOG} so its newest entry matches VERSION."
        )


class TestChangelogEndpoint:
    """GET /api/changelog — public endpoint serving release notes."""

    def setup_method(self):
        version_bp._load_changelog.cache_clear()

    def test_returns_200_with_entries(self, client):
        resp = client.get("/api/changelog")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "current" in data
        assert "entries" in data
        assert isinstance(data["entries"], list)

    def test_no_auth_required(self, client):
        resp = client.get("/api/changelog")
        assert resp.status_code == 200

    def test_entries_have_required_shape(self, client):
        resp = client.get("/api/changelog")
        entries = resp.get_json()["entries"]
        assert entries, "Changelog must have at least one entry"
        for entry in entries:
            assert "version" in entry
            assert "released_at" in entry
            assert "translations" in entry
            for lang in ("es", "en"):
                assert lang in entry["translations"], (
                    f"Entry {entry['version']} is missing the '{lang}' translation"
                )
                tr = entry["translations"][lang]
                assert "title" in tr
                assert "new" in tr
                assert "fixed" in tr
                assert isinstance(tr["new"], list)
                assert isinstance(tr["fixed"], list)

    def test_since_filters_older_entries(self, client):
        # Asking for changes since the current version must return nothing —
        # the user is already up to date.
        current = client.get("/api/version").get_json()["version"]
        resp = client.get(f"/api/changelog?since={current}")
        assert resp.status_code == 200
        assert resp.get_json()["entries"] == []

    def test_since_with_older_version_returns_entries(self, client):
        # 0.0.0 is older than anything we will ever ship.
        resp = client.get("/api/changelog?since=0.0.0")
        assert resp.status_code == 200
        entries = resp.get_json()["entries"]
        assert len(entries) >= 1

    def test_since_does_not_crash_on_invalid(self, client):
        # Garbage 'since' must never 500 the endpoint. The exact filtering
        # behavior for non-semver strings is intentionally undefined — what
        # matters is that the client gets a clean response and can degrade.
        resp = client.get("/api/changelog?since=not-a-version")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "entries" in data
        assert isinstance(data["entries"], list)

    def test_entries_are_newest_first(self, client):
        resp = client.get("/api/changelog")
        entries = resp.get_json()["entries"]
        if len(entries) < 2:
            return  # Only one entry — nothing to compare.
        for prev, curr in zip(entries, entries[1:]):
            cmp = version_bp._compare_semver(prev["version"], curr["version"])
            assert cmp >= 0, (
                f"Changelog entries are not in newest-first order: "
                f"{prev['version']} should be >= {curr['version']}"
            )


class TestChangelogFileStructure:
    """The changelog.json file itself must be valid and well-formed."""

    def test_file_exists(self):
        assert _CHANGELOG.exists(), f"Missing changelog file at {_CHANGELOG}"

    def test_file_is_valid_json(self):
        with _CHANGELOG.open() as f:
            data = json.load(f)
        assert "entries" in data
        assert isinstance(data["entries"], list)
        assert data["entries"], "Changelog must have at least one entry"
