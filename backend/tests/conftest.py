import pytest
from app import create_app
from app.extensions import db
from app.models import User, WorldCupGroup, Team, Match
from datetime import datetime, timedelta


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")
    
    with app.app_context():
        # Create all tables before tests
        db.create_all()
        yield app
        # Clean up after tests
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Database session for tests."""
    with app.app_context():
        yield db.session


@pytest.fixture
def seed_user(db_session):
    """Create a test user."""
    user = User(
        google_sub="test-google-sub",
        email="test@example.com",
        name="Test User",
        picture_url="https://example.com/pic.jpg"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def seed_groups(db_session):
    """Create 12 FIFA 2026 groups."""
    groups = [
        WorldCupGroup(name=letter)
        for letter in "ABCDEFGHIJKL"
    ]
    db_session.add_all(groups)
    db_session.commit()
    return groups


@pytest.fixture
def seed_teams(db_session, seed_groups):
    """Create 48 teams across 12 groups."""
    teams = []
    team_data = {
        "A": ["ARG", "PAR", "URY", "CAN"],
        "B": ["ENG", "USA", "IRA", "WAL"],
        "C": ["MEX", "POL", "ARG", "SAU"],
        "D": ["FRA", "NED", "SEN", "EQG"],
        "E": ["ESP", "GER", "JAP", "CRC"],
        "F": ["BEL", "CRO", "MAR", "CAN"],
        "G": ["BRA", "SUI", "CMR", "SRB"],
        "H": ["POR", "URU", "KOR", "GHA"],
    }
    
    # Use first 8 groups for seed data (48 teams / 8 groups = 6 teams per group)
    for idx, group in enumerate(seed_groups[:8]):
        for code in team_data.get(group.name, ["TM1", "TM2", "TM3", "TM4"]):
            team = Team(
                code=code,
                world_cup_group_id=group.id
            )
            teams.append(team)
    
    db_session.add_all(teams)
    db_session.commit()
    return teams


@pytest.fixture
def seed_matches(db_session, seed_groups, seed_teams):
    """Create 72 group-stage matches."""
    matches = []
    # For testing: create 72 matches across groups
    group_idx = 0
    match_count = 0
    kickoff = datetime.utcnow() + timedelta(days=1)
    
    while match_count < 72 and group_idx < len(seed_groups):
        group = seed_groups[group_idx]
        teams_in_group = [t for t in seed_teams if t.world_cup_group_id == group.id]
        
        # Create round-robin matches for this group (6 teams = 15 matches)
        for i, home_team in enumerate(teams_in_group):
            for away_team in teams_in_group[i+1:]:
                if match_count >= 72:
                    break
                
                match = Match(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    world_cup_group_id=group.id,
                    kickoff_utc=kickoff,
                    deadline_utc=kickoff - timedelta(hours=24),
                    status="scheduled"
                )
                matches.append(match)
                match_count += 1
                kickoff += timedelta(hours=1)
        
        group_idx += 1
    
    db_session.add_all(matches)
    db_session.commit()
    return matches
