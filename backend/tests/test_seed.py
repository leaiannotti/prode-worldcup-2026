"""Test seed data generation and idempotency."""
import pytest
from app.models import WorldCupGroup, Team, Match
from app.seed import load_seed_data


class TestSeedDataCreation:
    """Test suite for seed data generation (matches/Fixture Seed scenarios 1-3)."""
    
    def test_seed_creates_12_groups(self, app, db_session):
        """Scenario 1: Seed creates exactly 12 FIFA 2026 groups (A–L)."""
        with app.app_context():
            load_seed_data(db_session)
            
            groups = db_session.query(WorldCupGroup).all()
            assert len(groups) == 12
            
            # Verify all groups A-L exist
            group_names = {g.name for g in groups}
            expected = set("ABCDEFGHIJKL")
            assert group_names == expected
    
    def test_seed_creates_48_teams(self, app, db_session):
        """Scenario 2: Seed creates exactly 48 teams (4 per group)."""
        with app.app_context():
            load_seed_data(db_session)
            
            teams = db_session.query(Team).all()
            assert len(teams) == 48
            
            # Verify each group has 4 teams
            groups = db_session.query(WorldCupGroup).all()
            for group in groups:
                group_teams = db_session.query(Team).filter_by(
                    world_cup_group_id=group.id
                ).all()
                assert len(group_teams) == 4
    
    def test_seed_creates_72_matches(self, app, db_session):
        """Scenario 3: Seed creates exactly 72 group-stage matches with deadline = kickoff - 24h."""
        with app.app_context():
            load_seed_data(db_session)
            
            matches = db_session.query(Match).all()
            assert len(matches) == 72
            
            # Verify each match has deadline = kickoff - 24h
            for match in matches:
                from datetime import timedelta
                expected_deadline = match.kickoff_utc - timedelta(hours=24)
                assert match.deadline_utc == expected_deadline
    
    def test_seed_is_idempotent(self, app, db_session):
        """Scenario 4: Re-running seed is safe and idempotent (no duplicate rows)."""
        with app.app_context():
            # First load
            load_seed_data(db_session)
            
            first_groups = db_session.query(WorldCupGroup).count()
            first_teams = db_session.query(Team).count()
            first_matches = db_session.query(Match).count()
            
            # Second load
            load_seed_data(db_session)
            
            second_groups = db_session.query(WorldCupGroup).count()
            second_teams = db_session.query(Team).count()
            second_matches = db_session.query(Match).count()
            
            # Counts must not increase
            assert first_groups == second_groups == 12
            assert first_teams == second_teams == 48
            assert first_matches == second_matches == 72
