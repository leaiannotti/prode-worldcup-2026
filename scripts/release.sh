#!/usr/bin/env bash
# Cut a new release: validate changelog, bump VERSION, commit, tag.
# Usage: scripts/release.sh <major|minor|patch>
set -euo pipefail

bump="${1:-}"
if [[ "$bump" != "major" && "$bump" != "minor" && "$bump" != "patch" ]]; then
  echo "Usage: $0 <major|minor|patch>" >&2
  exit 1
fi

# Repo root — resolve so the script works from anywhere.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

CHANGELOG_PATH="backend/app/changelog.json"

# Must be on main (or release-strategy during the multi-PR change). After the change merges to main, switch to enforcing main only.
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" != "main" && "$current_branch" != "release-strategy" ]]; then
  echo "Error: must be on main (or release-strategy during release-strategy change). Currently on: $current_branch" >&2
  exit 1
fi

# Working tree must be clean
if ! git diff-index --quiet HEAD --; then
  echo "Error: working tree has uncommitted changes" >&2
  exit 1
fi

# Pull latest
git pull --ff-only

# Read current version and compute the next one
current=$(cat VERSION)
IFS='.' read -r major minor patch <<< "$current"

case "$bump" in
  major) new="$((major + 1)).0.0" ;;
  minor) new="${major}.$((minor + 1)).0" ;;
  patch) new="${major}.${minor}.$((patch + 1))" ;;
esac

# --- Changelog validation ---
# Before bumping VERSION, make sure backend/app/changelog.json contains
# an entry for the new version. This guarantees the "What's New" modal
# always has user-facing notes for the released version.
#
# Exit codes from the python validator:
#   0 — entry present and well-formed (may have auto-filled released_at)
#   2 — entry missing for the target version
#   3 — duplicate entries for the target version
#   4 — entry missing top-level keys (version / released_at / translations)
#   5 — entry missing es or en translation
#   6 — translation missing title / new / fixed
#   anything else — unexpected python error

if [[ ! -f "$CHANGELOG_PATH" ]]; then
  echo "Error: $CHANGELOG_PATH not found." >&2
  echo "The release flow expects a hand-curated changelog at this path." >&2
  exit 1
fi

set +e
python3 scripts/_validate_changelog.py "$CHANGELOG_PATH" "$new"
validator_status=$?
set -e

if [[ $validator_status -eq 2 ]]; then
  today="$(date -u +%Y-%m-%d)"
  cat >&2 <<EOF

Error: $CHANGELOG_PATH does not contain an entry for v$new.

Before cutting this release, add the following entry as the FIRST item
in the "entries" array of $CHANGELOG_PATH and fill in the bullet points
with user-facing notes (what changed from the user's perspective):

  {
    "version": "$new",
    "released_at": "$today",
    "translations": {
      "es": {
        "title": "¡Hay novedades!",
        "new": [],
        "fixed": []
      },
      "en": {
        "title": "What's new",
        "new": [],
        "fixed": []
      }
    }
  }

Then commit the changelog with a conventional message, e.g.:

  git add $CHANGELOG_PATH
  git commit -m "docs(changelog): add v$new release notes"

After that, re-run: scripts/release.sh $bump

EOF
  exit 1
fi

if [[ $validator_status -ne 0 ]]; then
  echo "Error: changelog validation failed (exit code $validator_status). See messages above." >&2
  exit 1
fi

# If the python validator modified the changelog (auto-filled released_at), stage it.
# It is safe to add even if unchanged — git just no-ops.
if ! git diff --quiet -- "$CHANGELOG_PATH"; then
  echo "  Staging changelog with auto-filled released_at."
  git add "$CHANGELOG_PATH"
fi

# --- Bump VERSION ---
echo "Bumping VERSION: $current → $new"
echo "$new" > VERSION

git add VERSION

# If the changelog was auto-modified, it is already staged; combine both files
# into the same release commit to keep history clean.
git commit -m "chore(release): v${new}"
git tag -a "v${new}" -m "Release v${new}"

echo ""
echo "Created tag v${new}. Push with:"
echo "  git push && git push --tags"
echo ""
echo "Or push everything in one command:"
echo "  git push --follow-tags"
