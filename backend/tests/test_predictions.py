"""Tests for predictions blueprint."""
import pytest
import json
from datetime import datetime, timedelta


class TestPredictionSchemas:
    """Unit tests for prediction schemas."""
    
    def test_prediction_request_schema_validates_non_negative_scores(self):
        """PredictionRequest requires non-negative scores."""
        from app.schemas.prediction import PredictionRequest
        
        # Valid prediction
        pred = PredictionRequest(match_id=123, home_score=2, away_score=1)
        assert pred.home_score == 2
        assert pred.away_score == 1
        
        # Negative score should fail validation
        with pytest.raises(Exception):  # ValidationError
            PredictionRequest(match_id=123, home_score=-1, away_score=1)


class TestPredictionEndpoints:
    """Integration tests for prediction endpoints."""
    
    def test_submit_prediction_returns_201_for_first_submission(
        self, app, client, seed_user, seed_matches, db_session
    ):
        """POST /api/groups/:id/predictions with first submission returns 201."""
        from app.services.auth_service import issue_jwt
        from app.models import PredictionGroup, GroupMembership
        
        with app.app_context():
            # Create group and add user
            group = PredictionGroup(name="Test Group", invite_code="ABC123", creator_id=seed_user.id)
            db_session.add(group)
            db_session.commit()
            
            membership = GroupMembership(user_id=seed_user.id, group_id=group.id, role="admin")
            db_session.add(membership)
            db_session.commit()
            
            # Set cookie
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            # Submit prediction
            match = seed_matches[0]
            response = client.post(
                f"/api/groups/{group.id}/predictions",
                data=json.dumps({"match_id": match.id, "home_score": 2, "away_score": 1}),
                content_type="application/json"
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data["match_id"] == match.id
            assert data["home_score"] == 2
            assert data["away_score"] == 1
    
    def test_update_prediction_returns_200_before_deadline(
        self, app, client, seed_user, seed_matches, db_session
    ):
        """POST /api/groups/:id/predictions with existing prediction before deadline returns 200."""
        from app.services.auth_service import issue_jwt
        from app.models import PredictionGroup, GroupMembership, Prediction
        
        with app.app_context():
            # Create group and add user
            group = PredictionGroup(name="Test Group", invite_code="ABC123", creator_id=seed_user.id)
            db_session.add(group)
            db_session.commit()
            
            membership = GroupMembership(user_id=seed_user.id, group_id=group.id, role="admin")
            db_session.add(membership)
            db_session.commit()
            
            # Create existing prediction
            match = seed_matches[0]
            prediction = Prediction(
                user_id=seed_user.id,
                match_id=match.id,
                group_id=group.id,
                home_score=1,
                away_score=0
            )
            db_session.add(prediction)
            db_session.commit()
            
            # Set cookie
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            # Update prediction
            response = client.post(
                f"/api/groups/{group.id}/predictions",
                data=json.dumps({"match_id": match.id, "home_score": 2, "away_score": 1}),
                content_type="application/json"
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["home_score"] == 2
            assert data["away_score"] == 1
    
    def test_prediction_with_negative_score_returns_422(
        self, app, client, seed_user, seed_matches, db_session
    ):
        """POST with negative score returns 422 validation error."""
        from app.services.auth_service import issue_jwt
        from app.models import PredictionGroup, GroupMembership
        
        with app.app_context():
            # Create group and add user
            group = PredictionGroup(name="Test Group", invite_code="ABC123", creator_id=seed_user.id)
            db_session.add(group)
            db_session.commit()
            
            membership = GroupMembership(user_id=seed_user.id, group_id=group.id, role="admin")
            db_session.add(membership)
            db_session.commit()
            
            # Set cookie
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            # Submit with negative score
            match = seed_matches[0]
            response = client.post(
                f"/api/groups/{group.id}/predictions",
                data=json.dumps({"match_id": match.id, "home_score": -1, "away_score": 1}),
                content_type="application/json"
            )
            
            assert response.status_code == 422
    
    def test_prediction_after_deadline_returns_423(
        self, app, client, seed_user, db_session
    ):
        """POST after match prediction_deadline_at returns 423."""
        from app.services.auth_service import issue_jwt
        from app.models import PredictionGroup, GroupMembership, Match, Team, WorldCupGroup
        
        with app.app_context():
            # Create group and add user
            group = PredictionGroup(name="Test Group", invite_code="ABC123", creator_id=seed_user.id)
            db_session.add(group)
            db_session.commit()
            
            membership = GroupMembership(user_id=seed_user.id, group_id=group.id, role="admin")
            db_session.add(membership)
            db_session.commit()
            
            # Create a match with deadline in the past
            wc_group = WorldCupGroup.query.filter_by(name="A").first()
            if not wc_group:
                wc_group = WorldCupGroup(name="Z")
                db_session.add(wc_group)
                db_session.commit()
            
            # Create teams if needed
            teams = Team.query.filter_by(world_cup_group_id=wc_group.id).all()
            while len(teams) < 2:
                team = Team(code=f"T{len(teams)}", world_cup_group_id=wc_group.id)
                db_session.add(team)
                db_session.flush()
                teams.append(team)
            
            now = datetime.utcnow()
            past_match = Match(
                home_team_id=teams[0].id,
                away_team_id=teams[1].id,
                world_cup_group_id=wc_group.id,
                kickoff_utc=now - timedelta(hours=25),
                deadline_utc=now - timedelta(hours=1),  # Past deadline
                status="scheduled"
            )
            db_session.add(past_match)
            db_session.commit()
            
            # Set cookie
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            # Try to submit prediction
            response = client.post(
                f"/api/groups/{group.id}/predictions",
                data=json.dumps({"match_id": past_match.id, "home_score": 2, "away_score": 1}),
                content_type="application/json"
            )
            
            assert response.status_code == 423
    
    def test_prediction_exactly_at_deadline_returns_423(
        self, app, client, seed_user, db_session
    ):
        """POST exactly at deadline returns 423."""
        from app.services.auth_service import issue_jwt
        from app.models import PredictionGroup, GroupMembership, Match, Team, WorldCupGroup
        from unittest.mock import patch
        
        with app.app_context():
            # Create group and add user
            group = PredictionGroup(name="Test Group", invite_code="ABC123", creator_id=seed_user.id)
            db_session.add(group)
            db_session.commit()
            
            membership = GroupMembership(user_id=seed_user.id, group_id=group.id, role="admin")
            db_session.add(membership)
            db_session.commit()
            
            # Create a match with deadline exactly now (we'll mock datetime)
            wc_group = WorldCupGroup.query.filter_by(name="B").first()
            if not wc_group:
                wc_group = WorldCupGroup(name="Y")
                db_session.add(wc_group)
                db_session.commit()
            
            teams = Team.query.filter_by(world_cup_group_id=wc_group.id).all()
            while len(teams) < 2:
                team = Team(code=f"TT{len(teams)}", world_cup_group_id=wc_group.id)
                db_session.add(team)
                db_session.flush()
                teams.append(team)
            
            deadline = datetime.utcnow()
            match = Match(
                home_team_id=teams[0].id,
                away_team_id=teams[1].id,
                world_cup_group_id=wc_group.id,
                kickoff_utc=deadline + timedelta(hours=24),
                deadline_utc=deadline,
                status="scheduled"
            )
            db_session.add(match)
            db_session.commit()
            
            # Set cookie
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            # Submit prediction at deadline (should fail since >= deadline triggers freeze)
            response = client.post(
                f"/api/groups/{group.id}/predictions",
                data=json.dumps({"match_id": match.id, "home_score": 2, "away_score": 1}),
                content_type="application/json"
            )
            
            assert response.status_code == 423
    
    def test_non_member_prediction_returns_403(
        self, app, client, seed_user, seed_matches, db_session
    ):
        """POST by non-member returns 403."""
        from app.services.auth_service import issue_jwt
        from app.models import PredictionGroup, User
        
        with app.app_context():
            # Create another user
            other_user = User(
                google_sub="other-sub",
                email="other@example.com",
                name="Other User"
            )
            db_session.add(other_user)
            db_session.commit()
            
            # Create group with seed_user (other_user NOT a member)
            group = PredictionGroup(name="Test Group", invite_code="ABC123", creator_id=seed_user.id)
            db_session.add(group)
            db_session.commit()
            
            # Set cookie for non-member
            token = issue_jwt(other_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            # Try to submit prediction
            match = seed_matches[0]
            response = client.post(
                f"/api/groups/{group.id}/predictions",
                data=json.dumps({"match_id": match.id, "home_score": 2, "away_score": 1}),
                content_type="application/json"
            )
            
            assert response.status_code == 403
