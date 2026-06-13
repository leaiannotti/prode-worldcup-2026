import pytest
from app import create_app
from app.extensions import db
from app.models import User, WorldCupGroup, Team, Match
from datetime import datetime, timedelta


@pytest.fixture(scope="function")
def app():
    """Create application for testing with a clean DB per test."""
    _app = create_app("testing")

    with _app.app_context():
        db.create_all()
        yield _app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Database session for tests — same context as the app fixture."""
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
    """Create 48 teams across 12 groups (4 teams per group for 12 groups)."""
    teams = []
    team_codes = [
        "ARG", "PAR", "URY", "CAN",
        "ENG", "USA", "IRA", "WAL",
        "MEX", "POL", "AUS", "SAU",
        "FRA", "NED", "SEN", "EQG",
        "ESP", "GER", "JAP", "CRC",
        "BEL", "CRO", "MAR", "CMR",
        "BRA", "SUI", "SRB", "ECU",
        "POR", "URU", "KOR", "GHA",
        "ITA", "SVN", "DAN", "TUN",
        "NZL", "NOR", "SWE", "CZE",
        "ROU", "SVK", "GRC", "BIH",
        "ISL", "ALB", "AUT", "HUN",
    ]

    # Create 4 teams for each of 12 groups
    for idx, group in enumerate(seed_groups):
        group_start = idx * 4
        group_end = group_start + 4
        group_codes = team_codes[group_start:group_end]

        for code in group_codes:
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
    """Create 48 group-stage matches (6 per group, 8 groups tested)."""
    matches = []
    # For testing: create 6 matches per group for first 8 groups (48 total)
    # 4 teams per group gives C(4,2) = 6 unique match-ups
    match_count = 0
    # Make kickoff sufficiently far in future so deadline is also in future
    # Business rule: deadline_utc = kickoff_utc - 1h
    kickoff = datetime.utcnow() + timedelta(days=2)

    for group in seed_groups:
        teams_in_group = [t for t in seed_teams if t.world_cup_group_id == group.id]

        # Create round-robin matches for this group (4 teams = 6 matches)
        for i, home_team in enumerate(teams_in_group):
            for away_team in teams_in_group[i+1:]:
                match = Match(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    world_cup_group_id=group.id,
                    kickoff_utc=kickoff,
                    deadline_utc=kickoff - timedelta(hours=1),
                    status="scheduled"
                )
                matches.append(match)
                match_count += 1
                kickoff += timedelta(hours=1)

    db_session.add_all(matches)
    db_session.commit()
    return matches
