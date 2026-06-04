"""Test seed data generation and idempotency.

Strict TDD Mode: All tests written first, then implementation.
All seed data must be JSON-sourced; no algorithmic generation.
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.models import WorldCupGroup, Team, Match
from app.seed import load_seed_data


class TestSeedDataCreation:
    """Test suite for seed data generation (JSON source only)."""
    
    def test_seed_creates_12_groups(self, app, db_session):
        """Scenario 1: Seed creates exactly 12 FIFA 2026 groups (A–L)."""
        with app.app_context():
            load_seed_data(db_session)
            
            groups = db_session.query(WorldCupGroup).all()
            assert len(groups) == 12, f"Expected 12 groups, got {len(groups)}"
            
            # Verify all groups A-L exist
            group_names = {g.name for g in groups}
            expected = set("ABCDEFGHIJKL")
            assert group_names == expected, f"Groups {group_names} do not match {expected}"
    
    def test_seed_creates_48_teams(self, app, db_session):
        """Scenario 2: Seed creates exactly 48 teams (4 per group)."""
        with app.app_context():
            load_seed_data(db_session)
            
            teams = db_session.query(Team).all()
            assert len(teams) == 48, f"Expected 48 teams, got {len(teams)}"
            
            # Verify each group has exactly 4 teams
            groups = db_session.query(WorldCupGroup).all()
            for group in groups:
                group_teams = db_session.query(Team).filter_by(
                    world_cup_group_id=group.id
                ).all()
                assert len(group_teams) == 4, \
                    f"Group {group.name} has {len(group_teams)} teams, expected 4"
    
    def test_seed_creates_72_matches(self, app, db_session):
        """Scenario 3: Seed creates exactly 72 group-stage matches (JSON source).
        
        No algorithmic generation. All 72 matches come from jsons/worldcup.json.
        Each match must have deadline_utc = kickoff_utc - 24h.
        """
        with app.app_context():
            load_seed_data(db_session)
            
            matches = db_session.query(Match).all()
            assert len(matches) == 72, \
                f"Expected exactly 72 group-stage matches, got {len(matches)}"
            
            # Verify each match has deadline = kickoff - 24h
            for match in matches:
                expected_deadline = match.kickoff_utc - timedelta(hours=24)
                assert match.deadline_utc == expected_deadline, \
                    f"Match {match.id} deadline {match.deadline_utc} != " \
                    f"expected {expected_deadline}"
    
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


class TestSeedDataCorrectness:
    """Test suite for verifying real 2026 FIFA World Cup data (JSON-sourced)."""
    
    def test_group_a_composition(self, app, db_session):
        """Verify Group A has correct teams: Mexico, South Korea, Czech Republic, South Africa."""
        with app.app_context():
            load_seed_data(db_session)
            
            group_a = db_session.query(WorldCupGroup).filter_by(name="A").first()
            assert group_a is not None
            
            teams = db_session.query(Team).filter_by(world_cup_group_id=group_a.id).all()
            team_codes = {t.code for t in teams}
            
            # JSON source: MEX, RSA (not ZAF), KOR, CZE
            expected_teams = {"MEX", "RSA", "KOR", "CZE"}
            assert team_codes == expected_teams, \
                f"Group A teams {team_codes} do not match JSON source {expected_teams}"
    
    def test_group_c_composition(self, app, db_session):
        """Verify Group C has correct teams: Brazil, Morocco, Haiti, Scotland."""
        with app.app_context():
            load_seed_data(db_session)
            
            group_c = db_session.query(WorldCupGroup).filter_by(name="C").first()
            assert group_c is not None
            
            teams = db_session.query(Team).filter_by(world_cup_group_id=group_c.id).all()
            team_codes = {t.code for t in teams}
            
            # JSON source: BRA, MAR, HAI, SCO
            expected_teams = {"BRA", "MAR", "HAI", "SCO"}
            assert team_codes == expected_teams, \
                f"Group C teams {team_codes} do not match JSON source {expected_teams}"
    
    def test_opening_match_mexico_vs_south_africa(self, app, db_session):
        """Verify opening match (Match 1) from JSON: Mexico vs South Africa.
        
        JSON source: 2026-06-11, 13:00 UTC-6 (Mexico City)
        Converts to: 2026-06-11, 19:00 UTC
        """
        with app.app_context():
            load_seed_data(db_session)
            
            # Find Group A teams
            group_a = db_session.query(WorldCupGroup).filter_by(name="A").first()
            mexico = db_session.query(Team).filter_by(
                code="MEX", 
                world_cup_group_id=group_a.id
            ).first()
            south_africa = db_session.query(Team).filter_by(
                code="RSA",
                world_cup_group_id=group_a.id
            ).first()
            
            assert mexico is not None, "Mexico (MEX) not found in Group A"
            assert south_africa is not None, "South Africa (RSA) not found in Group A"
            
            # Find opening match (Mexico home, South Africa away)
            opening_match = db_session.query(Match).filter_by(
                home_team_id=mexico.id,
                away_team_id=south_africa.id,
                world_cup_group_id=group_a.id
            ).first()
            
            assert opening_match is not None, \
                "Opening match Mexico vs South Africa not found in database"
            
            # Verify date/time from JSON: 2026-06-11 13:00 UTC-6 = 2026-06-11 19:00 UTC
            expected_kickoff = datetime(2026, 6, 11, 19, 0, 0)
            assert opening_match.kickoff_utc == expected_kickoff, \
                f"Opening match kickoff {opening_match.kickoff_utc} != " \
                f"JSON source {expected_kickoff}"
    
    def test_group_b_match_canada_vs_bosnia(self, app, db_session):
        """Verify Match 7 from JSON: Canada vs Bosnia & Herzegovina.
        
        JSON source: 2026-06-12, 15:00 UTC-4 (Toronto)
        Converts to: 2026-06-12, 19:00 UTC
        """
        with app.app_context():
            load_seed_data(db_session)
            
            # Find Group B teams
            group_b = db_session.query(WorldCupGroup).filter_by(name="B").first()
            canada = db_session.query(Team).filter_by(
                code="CAN",
                world_cup_group_id=group_b.id
            ).first()
            bosnia = db_session.query(Team).filter_by(
                code="BIH",
                world_cup_group_id=group_b.id
            ).first()
            
            assert canada is not None, "Canada (CAN) not found in Group B"
            assert bosnia is not None, "Bosnia & Herzegovina (BIH) not found in Group B"
            
            # Find match
            match = db_session.query(Match).filter_by(
                home_team_id=canada.id,
                away_team_id=bosnia.id,
                world_cup_group_id=group_b.id
            ).first()
            
            assert match is not None, \
                "Match Canada vs Bosnia not found in database"
            
            # JSON: 2026-06-12 15:00 UTC-4 = 2026-06-12 19:00 UTC
            expected_kickoff = datetime(2026, 6, 12, 19, 0, 0)
            assert match.kickoff_utc == expected_kickoff, \
                f"Match kickoff {match.kickoff_utc} != JSON source {expected_kickoff}"
    
    def test_group_c_match_brazil_vs_morocco(self, app, db_session):
        """Verify Match 13 from JSON: Brazil vs Morocco.
        
        JSON source: 2026-06-13, 18:00 UTC-4 (New York area)
        Converts to: 2026-06-13, 22:00 UTC
        """
        with app.app_context():
            load_seed_data(db_session)
            
            # Find Group C teams
            group_c = db_session.query(WorldCupGroup).filter_by(name="C").first()
            brazil = db_session.query(Team).filter_by(
                code="BRA",
                world_cup_group_id=group_c.id
            ).first()
            morocco = db_session.query(Team).filter_by(
                code="MAR",
                world_cup_group_id=group_c.id
            ).first()
            
            assert brazil is not None, "Brazil (BRA) not found in Group C"
            assert morocco is not None, "Morocco (MAR) not found in Group C"
            
            # Find match
            match = db_session.query(Match).filter_by(
                home_team_id=brazil.id,
                away_team_id=morocco.id,
                world_cup_group_id=group_c.id
            ).first()
            
            assert match is not None, \
                "Match Brazil vs Morocco not found in database"
            
            # JSON: 2026-06-13 18:00 UTC-4 = 2026-06-13 22:00 UTC
            expected_kickoff = datetime(2026, 6, 13, 22, 0, 0)
            assert match.kickoff_utc == expected_kickoff, \
                f"Match kickoff {match.kickoff_utc} != JSON source {expected_kickoff}"
    
    def test_no_duplicate_teams_across_groups(self, app, db_session):
        """Verify no team appears in multiple groups (data integrity check)."""
        with app.app_context():
            load_seed_data(db_session)
            
            all_teams = db_session.query(Team).all()
            team_codes = [t.code for t in all_teams]
            
            # Check for duplicates
            assert len(team_codes) == len(set(team_codes)), \
                f"Duplicate teams found in database"
    
    def test_all_72_matches_from_json_source(self, app, db_session):
        """Verify all 72 matches are from JSON source, not algorithmically generated.
        
        This test validates that every match in the database comes from
        jsons/worldcup.json exactly as specified.
        """
        with app.app_context():
            # Load JSON directly to compare
            from app.json_loader import load_matches_from_json
            json_matches = load_matches_from_json()
            
            load_seed_data(db_session)
            
            # Query all matches
            db_matches = db_session.query(Match).all()
            assert len(db_matches) == 72, \
                f"Expected 72 matches from JSON, got {len(db_matches)}"
            
            # Build a set of (home_code, away_code, kickoff_utc) tuples from DB
            # and compare to JSON
            db_match_tuples = set()
            for match in db_matches:
                home_code = match.home_team.code
                away_code = match.away_team.code
                db_match_tuples.add((home_code, away_code, match.kickoff_utc))
            
            # Build set from JSON
            json_match_tuples = set()
            for group_name, home_code, away_code, kickoff_utc in json_matches:
                json_match_tuples.add((home_code, away_code, kickoff_utc))
            
            # Compare
            assert db_match_tuples == json_match_tuples, \
                f"Database matches do not match JSON source"
