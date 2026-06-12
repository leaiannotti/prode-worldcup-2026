#!/usr/bin/env bash
# Cut a new release: bump VERSION, commit, tag.
# Usage: scripts/release.sh <major|minor|patch>
set -euo pipefail

bump="${1:-}"
if [[ "$bump" != "major" && "$bump" != "minor" && "$bump" != "patch" ]]; then
  echo "Usage: $0 <major|minor|patch>" >&2
  exit 1
fi

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

# Read current version
current=$(cat VERSION)
IFS='.' read -r major minor patch <<< "$current"

case "$bump" in
  major) new="$((major + 1)).0.0" ;;
  minor) new="${major}.$((minor + 1)).0" ;;
  patch) new="${major}.${minor}.$((patch + 1))" ;;
esac

echo "Bumping VERSION: $current → $new"
echo "$new" > VERSION

git add VERSION
git commit -m "chore(release): v${new}"
git tag -a "v${new}" -m "Release v${new}"

echo ""
echo "Created tag v${new}. Push with:"
echo "  git push && git push --tags"
echo ""
echo "Or push everything in one command:"
echo "  git push --follow-tags"
