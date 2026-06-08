"""Seed command for loading FIFA 2026 fixture data from local JSON files."""
import click
from datetime import timedelta
from app.extensions import db
from app.models import WorldCupGroup, Team, Match
from app.fixture_data import GROUPS_DATA, MATCHES_DATA

# FIFA country code → ISO 3166-1 alpha-2 code for flagcdn.com URLs
FIFA_TO_ISO2 = {
    "ARG": "ar", "AUS": "au", "BRA": "br", "CAN": "ca", "CHI": "cl",
    "CHN": "cn", "CMR": "cm", "COL": "co", "CRC": "cr", "CRO": "hr",
    "DEN": "dk", "ECU": "ec", "EGY": "eg", "ENG": "gb-eng", "ESP": "es",
    "FRA": "fr", "GER": "de", "GHA": "gh", "IRN": "ir", "ITA": "it",
    "JAM": "jm", "JPN": "jp", "KOR": "kr", "KSA": "sa", "MAR": "ma",
    "MEX": "mx", "NED": "nl", "NGA": "ng", "NZL": "nz", "PAN": "pa",
    "PAR": "py", "PER": "pe", "POL": "pl", "POR": "pt", "QAT": "qa",
    "RSA": "za", "RUS": "ru", "SCO": "gb-sct", "SEN": "sn", "SRB": "rs",
    "SUI": "ch", "TUN": "tn", "URU": "uy", "USA": "us", "WAL": "gb-wls",
    "CIV": "ci", "ALG": "dz", "NOR": "no", "SWE": "se",
    # WC 2026 additions
    "CZE": "cz", "BIH": "ba", "HAI": "ht", "TUR": "tr", "CUW": "cw",
    "BEL": "be", "CPV": "cv", "IRQ": "iq", "AUT": "at", "JOR": "jo",
    "COD": "cd", "UZB": "uz",
}


def get_flag_url(fifa_code: str) -> str | None:
    """Return flagcdn.com URL for a FIFA team code, or None if not mapped."""
    iso2 = FIFA_TO_ISO2.get(fifa_code)
    if not iso2:
        print(f"WARNING: No ISO2 mapping for {fifa_code}")
        return None
    return f"https://flagcdn.com/w80/{iso2}.png"


def load_seed_data(session):
    """Load seed data into database (idempotent).
    
    Data is sourced from local JSON files:
    - jsons/worldcup.json — all 72 group-stage matches
    - jsons/worldcup.teams.json — group composition and metadata
    
    All matches are loaded exactly as defined in the JSON source.
    No algorithmic generation is used.
    """
    from app.json_loader import load_team_names_from_json
    team_names = load_team_names_from_json()
    
    # 1. Upsert groups (A–L)
    for group_letter in "ABCDEFGHIJKL":
        existing = session.query(WorldCupGroup).filter_by(name=group_letter).first()
        if not existing:
            group = WorldCupGroup(name=group_letter)
            session.add(group)
    session.commit()
    
    # 2. Upsert teams (with name and flag_url)
    groups_map = {g.name: g for g in session.query(WorldCupGroup).all()}
    
    for group_name, team_codes in GROUPS_DATA.items():
        group = groups_map[group_name]
        for code in team_codes:
            existing = session.query(Team).filter_by(code=code).first()
            if not existing:
                team = Team(
                    code=code,
                    world_cup_group_id=group.id,
                    name=team_names.get(code, ""),
                    flag_url=get_flag_url(code),
                )
                session.add(team)
            else:
                # Update name and flag_url on existing records
                existing.name = team_names.get(code, existing.name)
                existing.flag_url = get_flag_url(code)
    session.commit()
    
    # 3. Upsert matches (all 72 from JSON)
    teams_map = {t.code: t for t in session.query(Team).all()}
    
    for group_name, home_code, away_code, kickoff_utc in MATCHES_DATA:
        home_team = teams_map.get(home_code)
        away_team = teams_map.get(away_code)
        group = groups_map[group_name]
        
        if home_team and away_team:
            # Check if match already exists
            existing = session.query(Match).filter_by(
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                world_cup_group_id=group.id
            ).first()
            
            if not existing:
                deadline_utc = kickoff_utc - timedelta(hours=1)
                
                match = Match(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    world_cup_group_id=group.id,
                    kickoff_utc=kickoff_utc,
                    deadline_utc=deadline_utc,
                    status="scheduled"
                )
                session.add(match)
    
    session.commit()


@click.command("seed")
def seed_command():
    """Load FIFA 2026 group-stage fixture data from local JSON files."""
    from app import create_app
    from app.extensions import db
    
    app = create_app()
    with app.app_context():
        load_seed_data(db.session)
        
        # Verify counts
        groups_count = db.session.query(WorldCupGroup).count()
        teams_count = db.session.query(Team).count()
        matches_count = db.session.query(Match).count()
        
        click.echo(f"✅ Seed complete: {groups_count} groups, {teams_count} teams, {matches_count} matches")
