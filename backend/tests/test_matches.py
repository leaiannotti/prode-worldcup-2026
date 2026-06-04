"""Tests for matches blueprint."""
import pytest
from datetime import datetime, timedelta


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
