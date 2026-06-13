"""Version blueprint — public endpoints to expose the current app version
and the changelog entries for the "What's New" modal.

Both endpoints are intentionally public (no auth required) so the frontend
can fetch them on app boot, before the user is logged in.
"""
import json
from pathlib import Path
from functools import lru_cache
from flask import Blueprint, jsonify, request

bp = Blueprint("version", __name__, url_prefix="/api")

# Path to the changelog file (lives alongside the app package).
_CHANGELOG_PATH = Path(__file__).resolve().parent.parent / "changelog.json"


@lru_cache(maxsize=1)
def _load_changelog() -> dict:
    """Load and cache the changelog JSON. Cached for the process lifetime.

    The cache is intentional: changelog only changes between deploys, and
    each deploy starts a new process. If the file is missing or malformed,
    we return an empty structure so the API never 500s.
    """
    if not _CHANGELOG_PATH.exists():
        return {"entries": []}
    try:
        with _CHANGELOG_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "entries" not in data:
            return {"entries": []}
        if not isinstance(data["entries"], list):
            return {"entries": []}
        return data
    except (json.JSONDecodeError, OSError):
        return {"entries": []}


def _current_version() -> str:
    """Return the current app version from the first changelog entry.

    Falls back to '0.0.0-dev' if the changelog is missing or empty so the
    endpoint always returns a stable shape.
    """
    data = _load_changelog()
    entries = data.get("entries", [])
    if entries and isinstance(entries[0], dict):
        version = entries[0].get("version")
        if isinstance(version, str) and version:
            return version
    return "0.0.0-dev"


def _compare_semver(a: str, b: str) -> int:
    """Compare two semver-ish strings. Returns 1 if a > b, -1 if a < b, 0 if equal.

    Tolerant of non-numeric segments and missing pieces — falls back to string
    comparison for any segment that does not parse as an int.
    """
    def _parts(v: str) -> list:
        # Strip a leading 'v' just in case ("v1.1.0" -> "1.1.0").
        v = v.lstrip("vV")
        out = []
        for seg in v.split("."):
            try:
                out.append((0, int(seg)))
            except ValueError:
                out.append((1, seg))
        return out

    pa, pb = _parts(a), _parts(b)
    # Pad shorter list with (0, 0) so 1.1 == 1.1.0
    while len(pa) < len(pb):
        pa.append((0, 0))
    while len(pb) < len(pa):
        pb.append((0, 0))

    if pa > pb:
        return 1
    if pa < pb:
        return -1
    return 0


@bp.route("/version", methods=["GET"])
def get_version():
    """GET /api/version — return the current app version.

    Public endpoint. The frontend fetches this once at boot to know which
    version is running and to decide whether to show the "What's New" modal.
    """
    return jsonify({"version": _current_version()}), 200


@bp.route("/changelog", methods=["GET"])
def get_changelog():
    """GET /api/changelog — return changelog entries.

    Query params:
    - since (optional): only return entries strictly newer than this version.
      Useful for the "What's New" modal — the frontend sends the last
      version the user has acknowledged and gets back only the new stuff.

    Response shape:
    {
        "current": "1.1.0",
        "entries": [
            {"version": "1.1.0", "released_at": "...", "translations": {...}},
            ...
        ]
    }
    """
    data = _load_changelog()
    entries = data.get("entries", [])
    current = _current_version()

    since = request.args.get("since")
    if since:
        entries = [
            e for e in entries
            if isinstance(e, dict)
            and isinstance(e.get("version"), str)
            and _compare_semver(e["version"], since) > 0
        ]

    return jsonify({"current": current, "entries": entries}), 200
