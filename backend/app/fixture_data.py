"""FIFA 2026 World Cup fixture data — loads from local JSON files.

This module delegates all fixture data loading to json_loader.py, which reads
from the local JSON files as the authoritative source:
- jsons/worldcup.json — all matches with verified kickoff times
- jsons/worldcup.teams.json — group composition and team metadata

All data is JSON-sourced for correctness and traceability.
"""

from app.json_loader import load_teams_from_json, load_matches_from_json

# Load fixture data from JSON on module import
GROUPS_DATA = load_teams_from_json()
MATCHES_DATA = load_matches_from_json()
