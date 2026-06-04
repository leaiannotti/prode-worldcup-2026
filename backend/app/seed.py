"""Seed command for loading FIFA 2026 fixture data."""
import click
from datetime import datetime, timedelta, timezone
from app.extensions import db
from app.models import WorldCupGroup, Team, Match


# FIFA 2026 group-stage fixture data (simplified seed)
# 12 groups × 4 teams = 48 teams total
GROUPS_DATA = {
    "A": ["ARG", "PAR", "MAU", "CAN"],
    "B": ["ENG", "USA", "IRA", "WAL"],
    "C": ["MEX", "POL", "SAU", "ECU"],
    "D": ["FRA", "NED", "SEN", "EGY"],
    "E": ["ESP", "GER", "JAP", "CRC"],
    "F": ["BEL", "CRO", "MAR", "SVN"],
    "G": ["BRA", "SUI", "CMR", "SRB"],
    "H": ["POR", "URU", "KOR", "GHA"],
    "I": ["ITA", "SWE", "ALB", "UZB"],
    "J": ["AUS", "DEN", "TUN", "PER"],
    "K": ["SCO", "HUN", "SVK", "ROM"],
    "L": ["GRE", "CZE", "NOR", "ISL"],
}

def generate_group_matches():
    """
    Generate 72 group-stage matches.
    Each group has 4 teams, creating 6 matches per group (C(4,2) = 6).
    12 groups × 6 matches = 72 total.
    Format: (group_name, home_code, away_code, match_number)
    """
    matches = []
    base_kickoff_day = 1
    
    for group_letter in "ABCDEFGHIJKL":
        teams = GROUPS_DATA[group_letter]
        match_num = 1
        
        # Round-robin: each team plays every other team
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                home_team = teams[i]
                away_team = teams[j]
                
                # Alternate days and times for realism
                day_offset = (match_num - 1) // 2 + 1
                hour = 13 if match_num % 2 == 1 else 16
                
                matches.append((group_letter, home_team, away_team, day_offset + base_kickoff_day, hour))
                match_num += 1
        
        base_kickoff_day += 3  # Each group's matches span ~3 days
    
    return matches


MATCHES_DATA = generate_group_matches()


def load_seed_data(session):
    """Load seed data into database (idempotent)."""
    
    # 1. Upsert groups
    for group_letter in "ABCDEFGHIJKL":
        existing = session.query(WorldCupGroup).filter_by(name=group_letter).first()
        if not existing:
            group = WorldCupGroup(name=group_letter)
            session.add(group)
    session.commit()
    
    # 2. Upsert teams
    groups_map = {g.name: g for g in session.query(WorldCupGroup).all()}
    
    for group_name, team_codes in GROUPS_DATA.items():
        group = groups_map[group_name]
        for code in team_codes:
            existing = session.query(Team).filter_by(code=code).first()
            if not existing:
                team = Team(code=code, world_cup_group_id=group.id)
                session.add(team)
    session.commit()
    
    # 3. Upsert matches
    teams_map = {t.code: t for t in session.query(Team).all()}
    base_kickoff = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
    
    match_idx = 0
    for group_name, home_code, away_code, days, hour in MATCHES_DATA:
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
                kickoff = base_kickoff + timedelta(days=days, hours=hour-12)
                deadline = kickoff - timedelta(hours=24)
                
                match = Match(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    world_cup_group_id=group.id,
                    kickoff_utc=kickoff,
                    deadline_utc=deadline,
                    status="scheduled"
                )
                session.add(match)
            match_idx += 1
    
    session.commit()


@click.command("seed")
def seed_command():
    """Load FIFA 2026 group-stage fixture data."""
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
