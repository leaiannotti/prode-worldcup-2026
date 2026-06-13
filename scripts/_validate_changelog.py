#!/usr/bin/env python3
"""Validate that backend/app/changelog.json has a well-formed entry for the
target release version. If the entry's released_at is empty or a placeholder,
auto-fill it with today's UTC date and write the file back.

Invoked by scripts/release.sh. Exit codes are part of the contract:
    0 - entry present and well-formed (may have been auto-filled)
    2 - entry missing for the target version
    3 - duplicate entries for the target version
    4 - entry missing top-level keys
    5 - entry missing es or en translation
    6 - translation missing title / new / fixed
"""
import json
import sys
from datetime import datetime, timezone

PLACEHOLDERS = {"", "YYYY-MM-DD", "TBD", "tbd"}
REQUIRED_TOP_KEYS = {"version", "released_at", "translations"}
REQUIRED_LANGS = ("es", "en")
REQUIRED_TR_KEYS = ("title", "new", "fixed")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: _validate_changelog.py <path> <target_version>", file=sys.stderr)
        return 1

    path, target_version = argv[1], argv[2]

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = data.get("entries", [])
    matching = [
        e for e in entries
        if isinstance(e, dict) and e.get("version") == target_version
    ]

    if not matching:
        return 2

    if len(matching) > 1:
        print(
            f"Error: {path} has {len(matching)} entries for version "
            f"{target_version}. Each version must be unique.",
            file=sys.stderr,
        )
        return 3

    entry = matching[0]

    # Auto-fill released_at if empty or placeholder.
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    released_at = entry.get("released_at", "")
    if released_at in PLACEHOLDERS:
        entry["released_at"] = today
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(
            f"  Auto-filled released_at for v{target_version}: {today}",
            file=sys.stderr,
        )

    # Validate required top-level keys.
    missing_top = REQUIRED_TOP_KEYS - set(entry.keys())
    if missing_top:
        print(
            f"Error: entry for v{target_version} is missing required keys: "
            f"{sorted(missing_top)}",
            file=sys.stderr,
        )
        return 4

    # Validate translations.
    translations = entry["translations"]
    for lang in REQUIRED_LANGS:
        if lang not in translations:
            print(
                f"Error: entry for v{target_version} is missing the "
                f"'{lang}' translation.",
                file=sys.stderr,
            )
            return 5
        tr = translations[lang]
        for key in REQUIRED_TR_KEYS:
            if key not in tr:
                print(
                    f"Error: entry for v{target_version} translation "
                    f"'{lang}' is missing key '{key}'.",
                    file=sys.stderr,
                )
                return 6

    print(f"  Changelog entry for v{target_version} OK.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
