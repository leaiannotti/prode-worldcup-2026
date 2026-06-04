"""Load FIFA 2026 World Cup fixture data from local JSON files.

This module is the authoritative source for all fixture data. It reads from:
- jsons/worldcup.json — all matches (group stage only extracted)
- jsons/worldcup.teams.json — group composition and team metadata

All 72 group-stage matches are derived from the JSON source of truth.
"""

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _get_json_dir():
    """Get the jsons directory path (relative to project root)."""
    # Walk up from backend/app to project root
    # __file__ = /path/to/backend/app/json_loader.py
    # .parent = /path/to/backend/app
    # .parent = /path/to/backend
    # .parent = /path/to (project root)
    app_dir = Path(__file__).parent
    backend_dir = app_dir.parent
    project_root = backend_dir.parent
    return project_root / "jsons"


def load_teams_from_json():
    """Load team data from worldcup.teams.json.
    
    Returns:
        dict: Mapping {group_letter: [team_codes]}
              Example: {"A": ["MEX", "RSA", "KOR", "CZE"], ...}
    """
    json_dir = _get_json_dir()
    teams_file = json_dir / "worldcup.teams.json"
    
    with open(teams_file) as f:
        teams_data = json.load(f)
    
    groups = {}
    for team in teams_data:
        group_letter = team["group"]
        code = team["fifa_code"]
        
        if group_letter not in groups:
            groups[group_letter] = []
        groups[group_letter].append(code)
    
    return groups


def _parse_kickoff_utc(date_str, time_str):
    """Parse a kickoff datetime from date and time strings.
    
    Args:
        date_str: ISO date string (e.g., "2026-06-11")
        time_str: Time with timezone (e.g., "13:00 UTC-6")
    
    Returns:
        datetime: UTC kickoff time (naive, in UTC)
    """
    # Extract time and timezone offset
    match = re.match(r'(\d{1,2}):(\d{2})\s+UTC([+-]\d+)', time_str)
    if not match:
        raise ValueError(f"Invalid time format: {time_str}")
    
    hour, minute, tz_offset = match.groups()
    hour, minute = int(hour), int(minute)
    tz_offset = int(tz_offset)
    
    # Create datetime in local timezone (the offset tells us local hour + minute)
    local_dt = datetime.strptime(date_str, '%Y-%m-%d')
    local_dt = local_dt.replace(hour=hour, minute=minute)
    
    # Convert to UTC by subtracting the offset
    # If time_str says "13:00 UTC-6", that means local time is 13:00 in UTC-6 zone
    # UTC time = 13:00 - (-6) = 13:00 + 6 hours = 19:00 UTC
    utc_dt = local_dt - timedelta(hours=tz_offset)
    
    return utc_dt


def load_matches_from_json():
    """Load match data from worldcup.json.
    
    Returns:
        list: List of tuples (group_letter, home_code, away_code, kickoff_utc)
              All 72 group-stage matches in order as listed in JSON
    """
    json_dir = _get_json_dir()
    matches_file = json_dir / "worldcup.json"
    
    with open(matches_file) as f:
        wc_data = json.load(f)
    
    # Load teams to build team name -> code mapping
    teams_file = json_dir / "worldcup.teams.json"
    with open(teams_file) as f:
        teams_data = json.load(f)
    
    team_name_to_code = {team["name"]: team["fifa_code"] for team in teams_data}
    
    # Extract group-stage matches only (those with a "group" field)
    matches = []
    for match_data in wc_data["matches"]:
        if match_data.get("group") is None:
            continue  # Skip knockout matches
        
        group_str = match_data["group"]  # "Group A", "Group B", etc.
        group_letter = group_str.replace("Group ", "")
        
        team1_name = match_data["team1"]
        team2_name = match_data["team2"]
        
        # Look up team codes
        home_code = team_name_to_code.get(team1_name)
        away_code = team_name_to_code.get(team2_name)
        
        if not home_code or not away_code:
            raise ValueError(
                f"Team mapping failed: {team1_name} -> {home_code}, "
                f"{team2_name} -> {away_code}"
            )
        
        # Parse kickoff time
        kickoff_utc = _parse_kickoff_utc(match_data["date"], match_data["time"])
        
        matches.append((group_letter, home_code, away_code, kickoff_utc))
    
    return matches


def verify_fixture_data():
    """Verify loaded fixture data for consistency.
    
    Raises:
        AssertionError: If data does not meet expectations
    """
    groups = load_teams_from_json()
    matches = load_matches_from_json()
    
    # Verify 12 groups, 4 teams per group
    assert len(groups) == 12, f"Expected 12 groups, got {len(groups)}"
    for group_letter in "ABCDEFGHIJKL":
        assert group_letter in groups, f"Group {group_letter} missing"
        assert len(groups[group_letter]) == 4, \
            f"Group {group_letter} has {len(groups[group_letter])} teams, expected 4"
    
    # Verify 72 group-stage matches
    assert len(matches) == 72, f"Expected 72 group-stage matches, got {len(matches)}"
    
    # Verify each match has valid group and teams
    all_teams = {code for group_codes in groups.values() for code in group_codes}
    for group_letter, home_code, away_code, kickoff_utc in matches:
        assert group_letter in groups, \
            f"Match references invalid group {group_letter}"
        assert home_code in all_teams, \
            f"Match home team {home_code} not in any group"
        assert away_code in all_teams, \
            f"Match away team {away_code} not in any group"
        assert home_code in groups[group_letter], \
            f"Match: {home_code} not in group {group_letter}"
        assert away_code in groups[group_letter], \
            f"Match: {away_code} not in group {group_letter}"
        assert isinstance(kickoff_utc, datetime), \
            f"Invalid kickoff type for {home_code} vs {away_code}"
    
    # Verify no duplicate team pairs (each pairing appears once)
    match_pairs = set()
    for group_letter, home_code, away_code, _ in matches:
        pair = (group_letter, tuple(sorted([home_code, away_code])))
        assert pair not in match_pairs, \
            f"Duplicate match: {home_code} vs {away_code} in {group_letter}"
        match_pairs.add(pair)


if __name__ == "__main__":
    # Quick test
    print("Loading teams...")
    groups = load_teams_from_json()
    print(f"  Loaded {len(groups)} groups with {sum(len(t) for t in groups.values())} teams")
    
    print("\nLoading matches...")
    matches = load_matches_from_json()
    print(f"  Loaded {len(matches)} group-stage matches")
    
    print("\nVerifying fixture data...")
    verify_fixture_data()
    print("  ✅ All checks passed")
