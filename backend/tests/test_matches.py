"""Tests for matches blueprint."""
import pytest
from datetime import datetime, timedelta


def _make_auth_client(app, client, user):
    """Set JWT cookie on client for authenticated requests."""
    from app.services.auth_service import issue_jwt
    token = issue_jwt(user.id)
    client.set_cookie(key="jwt_token", value=token)
    return client


class TestMatchFiltering:
    """Integration tests for match status and limit filtering."""

    def test_list_matches_upcoming_only(
        self, app, client, seed_user, db_session, seed_groups, seed_teams
    ):
        """GET /api/matches?status=upcoming returns only scheduled matches."""
        with app.app_context():
            from app.models import Match

            # Create a scheduled and a finished match
            base = datetime.utcnow() + timedelta(days=2)
            m_sched = Match(
                home_team_id=seed_teams[0].id,
                away_team_id=seed_teams[1].id,
                world_cup_group_id=seed_groups[0].id,
                kickoff_utc=base,
                deadline_utc=base - timedelta(hours=24),
                status="scheduled",
            )
            m_fin = Match(
                home_team_id=seed_teams[2].id,
                away_team_id=seed_teams[3].id,
                world_cup_group_id=seed_groups[0].id,
                kickoff_utc=base + timedelta(hours=1),
                deadline_utc=base + timedelta(hours=1) - timedelta(hours=24),
                status="finished",
            )
            db_session.add_all([m_sched, m_fin])
            db_session.commit()

            sched_id = m_sched.id
            fin_id = m_fin.id

            _make_auth_client(app, client, seed_user)
            response = client.get("/api/matches?status=upcoming")

        assert response.status_code == 200
        data = response.get_json()
        assert all(m["status"] == "scheduled" for m in data)
        # finished match must not appear
        ids = [m["id"] for m in data]
        assert sched_id in ids
        assert fin_id not in ids

    def test_list_matches_with_limit(
        self, app, client, seed_user, db_session, seed_groups, seed_teams
    ):
        """GET /api/matches?limit=3 returns at most 3 matches."""
        with app.app_context():
            from app.models import Match

            base = datetime.utcnow() + timedelta(days=2)
            for i in range(5):
                m = Match(
                    home_team_id=seed_teams[0].id,
                    away_team_id=seed_teams[1].id,
                    world_cup_group_id=seed_groups[0].id,
                    kickoff_utc=base + timedelta(hours=i),
                    deadline_utc=base + timedelta(hours=i) - timedelta(hours=24),
                    status="scheduled",
                )
                db_session.add(m)
            db_session.commit()

            _make_auth_client(app, client, seed_user)
            response = client.get("/api/matches?limit=3")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 3

    def test_list_matches_upcoming_with_limit(
        self, app, client, seed_user, db_session, seed_groups, seed_teams
    ):
        """GET /api/matches?status=upcoming&limit=2 returns ≤2 scheduled matches."""
        with app.app_context():
            from app.models import Match

            base = datetime.utcnow() + timedelta(days=2)
            for i in range(4):
                status = "scheduled" if i < 3 else "finished"
                m = Match(
                    home_team_id=seed_teams[0].id,
                    away_team_id=seed_teams[1].id,
                    world_cup_group_id=seed_groups[0].id,
                    kickoff_utc=base + timedelta(hours=i),
                    deadline_utc=base + timedelta(hours=i) - timedelta(hours=24),
                    status=status,
                )
                db_session.add(m)
            db_session.commit()

            _make_auth_client(app, client, seed_user)
            response = client.get("/api/matches?status=upcoming&limit=2")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert all(m["status"] == "scheduled" for m in data)

    def test_list_matches_combined_filters(
        self, app, client, seed_user, db_session, seed_groups, seed_teams
    ):
        """status + group filter: only scheduled matches in specified group."""
        with app.app_context():
            from app.models import Match

            base = datetime.utcnow() + timedelta(days=2)
            # Group A match — scheduled
            m_a = Match(
                home_team_id=seed_teams[0].id,
                away_team_id=seed_teams[1].id,
                world_cup_group_id=seed_groups[0].id,
                kickoff_utc=base,
                deadline_utc=base - timedelta(hours=24),
                status="scheduled",
            )
            # Group B match — scheduled
            m_b = Match(
                home_team_id=seed_teams[4].id,
                away_team_id=seed_teams[5].id,
                world_cup_group_id=seed_groups[1].id,
                kickoff_utc=base,
                deadline_utc=base - timedelta(hours=24),
                status="scheduled",
            )
            db_session.add_all([m_a, m_b])
            db_session.commit()

            m_a_id = m_a.id
            m_b_id = m_b.id
            group_a_name = seed_groups[0].name

            _make_auth_client(app, client, seed_user)
            response = client.get(f"/api/matches?status=upcoming&group={group_a_name}")

        assert response.status_code == 200
        data = response.get_json()
        ids = [m["id"] for m in data]
        assert m_a_id in ids
        assert m_b_id not in ids

    def test_list_matches_invalid_limit_returns_400(
        self, app, client, seed_user, seed_groups
    ):
        """GET /api/matches?limit=-1 returns 400."""
        with app.app_context():
            _make_auth_client(app, client, seed_user)
            response = client.get("/api/matches?limit=-1")

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "invalid_limit"

    def test_list_matches_invalid_limit_zero_returns_400(
        self, app, client, seed_user, seed_groups
    ):
        """GET /api/matches?limit=0 returns 400."""
        with app.app_context():
            _make_auth_client(app, client, seed_user)
            response = client.get("/api/matches?limit=0")

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "invalid_limit"

    def test_list_matches_invalid_limit_string_returns_400(
        self, app, client, seed_user, seed_groups
    ):
        """GET /api/matches?limit=abc returns 400."""
        with app.app_context():
            _make_auth_client(app, client, seed_user)
            response = client.get("/api/matches?limit=abc")

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "invalid_limit"

    def test_list_matches_invalid_status_returns_400(
        self, app, client, seed_user, seed_groups
    ):
        """GET /api/matches?status=bogus returns 400."""
        with app.app_context():
            _make_auth_client(app, client, seed_user)
            response = client.get("/api/matches?status=bogus_status")

        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "invalid_status"

    def test_list_matches_no_filters_unchanged(
        self, app, client, seed_user, seed_matches
    ):
        """GET /api/matches without new params returns all matches (backward compat)."""
        with app.app_context():
            _make_auth_client(app, client, seed_user)
            response = client.get("/api/matches")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == len(seed_matches)


class TestMatchSchemas:
    """Unit tests for match schemas."""
    
    def test_match_response_valid(self, db_session, seed_matches):
        """Test MatchResponse with valid match data."""
        from app.schemas.match import MatchResponse
        from app.models import Match, Team, WorldCupGroup
        
        match = seed_matches[0]
        
        # Should not raise
        response = MatchResponse.model_validate(match)
        assert response.id == match.id
        assert response.kickoff_at == match.kickoff_utc
        assert response.prediction_deadline_at == match.deadline_utc
        assert response.status == match.status
        assert response.home_score == match.home_score
        assert response.away_score == match.away_score


class TestMatchEndpoints:
    """Integration tests for match endpoints."""
    
    def test_list_matches_by_group_returns_group_matches(
        self, app, client, seed_user, seed_matches, db_session
    ):
        """GET /api/matches?group=A returns matches for group A."""
        # Create JWT for authenticated request
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            # Get group A from seed
            group_a_matches = [m for m in seed_matches if m.group.name == "A"]
            assert len(group_a_matches) > 0
            
            response = client.get("/api/matches?group=A")
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == len(group_a_matches)
        # All matches should be sorted by kickoff_utc
        assert data[0]["kickoff_at"] <= data[-1]["kickoff_at"]
    
    def test_list_matches_by_date_filters_correctly(
        self, app, client, seed_user, seed_matches, db_session
    ):
        """GET /api/matches?date=YYYY-MM-DD filters by UTC date."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            # Pick a date from seed
            first_match = seed_matches[0]
            date_str = first_match.kickoff_utc.strftime("%Y-%m-%d")
            
            # Count matches on that date
            expected_count = len([
                m for m in seed_matches
                if m.kickoff_utc.date() == first_match.kickoff_utc.date()
            ])
            
            response = client.get(f"/api/matches?date={date_str}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == expected_count
    
    def test_list_matches_invalid_group_returns_400(
        self, app, client, seed_user, seed_matches
    ):
        """GET /api/matches?group=Z returns 400 for invalid group."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            response = client.get("/api/matches?group=Z")
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data or "invalid_group" in str(data).lower()
    
    def test_match_detail_returns_correct_shape(
        self, app, client, seed_user, seed_matches
    ):
        """GET /api/matches/:id returns full match detail."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            match = seed_matches[0]
            response = client.get(f"/api/matches/{match.id}")
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify shape
        assert "id" in data
        assert "group" in data or "world_cup_group_id" in data
        assert "home_team" in data
        assert "away_team" in data
        assert "kickoff_at" in data
        assert "prediction_deadline_at" in data
        assert "status" in data
        assert "home_score" in data
        assert "away_score" in data
    
    def test_list_matches_requires_auth(self, client):
        """GET /api/matches without JWT returns 401."""
        response = client.get("/api/matches")
        
        assert response.status_code == 401
    
    def test_match_detail_requires_auth(self, client, seed_matches):
        """GET /api/matches/:id without JWT returns 401."""
        match = seed_matches[0]
        response = client.get(f"/api/matches/{match.id}")
        
        assert response.status_code == 401
