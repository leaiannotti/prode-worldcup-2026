"""Tests for score history endpoints - Strict TDD."""
import pytest
import json
from app.models import (
    PredictionGroup, GroupMembership, Prediction, PredictionScore, 
    User, Match
)
from app.services.auth_service import issue_jwt
from datetime import datetime, timedelta
from uuid import uuid4


def _generate_invite_code():
    """Generate a 6-character alphanumeric invite code."""
    return uuid4().hex[:6].upper()


class TestHistoryBasics:
    """Score history retrieval scenarios."""

    def test_history_returns_predictions(self, app, client, db_session, seed_user, seed_groups, seed_teams, seed_matches):
        """
        Given: User has made predictions in a group
        When: User calls GET /api/scores/history?group_id=<group>
        Then: Returns list of predictions with scores
        """
        group = PredictionGroup(name="History Group", creator_id=seed_user.id, invite_code=_generate_invite_code())
        db_session.add(group)
        db_session.flush()
        
        membership = GroupMembership(user_id=seed_user.id, group_id=group.id)
        db_session.add(membership)
        db_session.flush()
        
        # Create prediction with score
        match = seed_matches[0]
        match.status = "finished"
        match.home_score = 2
        match.away_score = 1
        
        pred = Prediction(
            user_id=seed_user.id,
            match_id=match.id,
            home_score=2,
            away_score=1
        )
        db_session.add(pred)
        db_session.flush()
        
        score = PredictionScore(prediction_id=pred.id, points=3, score_type="exact")
        db_session.add(score)
        db_session.commit()
        
        with app.app_context():
            token = issue_jwt(seed_user.id)
        
        client.set_cookie(key="jwt_token", value=token)
        response = client.get(f"/api/scores/history?group_id={group.id}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert "history" in data
        history = data["history"]
        assert len(history) == 1
        assert history[0]["points"] == 3
        assert history[0]["prediction"]["home_score"] == 2

    def test_history_includes_unscored(self, app, client, db_session, seed_user, seed_groups, seed_teams, seed_matches):
        """Unscored predictions should be included with points=null."""
        group = PredictionGroup(name="Mixed", creator_id=seed_user.id, invite_code=_generate_invite_code())
        db_session.add(group)
        db_session.flush()
        
        membership = GroupMembership(user_id=seed_user.id, group_id=group.id)
        db_session.add(membership)
        db_session.flush()
        
        match1 = seed_matches[0]
        match2 = seed_matches[1]
        
        # Match 1: finished and scored
        match1.status = "finished"
        match1.home_score = 2
        match1.away_score = 1
        
        pred1 = Prediction(user_id=seed_user.id, match_id=match1.id, home_score=2, away_score=1)
        db_session.add(pred1)
        db_session.flush()
        score1 = PredictionScore(prediction_id=pred1.id, points=3, score_type="exact")
        db_session.add(score1)
        
        # Match 2: pending (no score)
        pred2 = Prediction(user_id=seed_user.id, match_id=match2.id, home_score=1, away_score=0)
        db_session.add(pred2)
        db_session.commit()
        
        with app.app_context():
            token = issue_jwt(seed_user.id)
        
        client.set_cookie(key="jwt_token", value=token)
        response = client.get(f"/api/scores/history?group_id={group.id}")
        
        assert response.status_code == 200
        history = response.get_json()["history"]
        assert len(history) == 2
        
        scored = [h for h in history if h["points"] is not None]
        unscored = [h for h in history if h["points"] is None]
        
        assert len(scored) == 1
        assert len(unscored) == 1
        assert scored[0]["points"] == 3
        assert unscored[0]["actual_result"] is None

    def test_history_empty_list_no_predictions(self, app, client, db_session, seed_user, seed_groups):
        """User with no predictions should get empty history."""
        group = PredictionGroup(name="Empty", creator_id=seed_user.id, invite_code=_generate_invite_code())
        db_session.add(group)
        db_session.flush()
        
        membership = GroupMembership(user_id=seed_user.id, group_id=group.id)
        db_session.add(membership)
        db_session.commit()
        
        with app.app_context():
            token = issue_jwt(seed_user.id)
        
        client.set_cookie(key="jwt_token", value=token)
        response = client.get(f"/api/scores/history?group_id={group.id}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["history"] == []

    def test_history_non_member_403(self, app, client, db_session, seed_user, seed_groups):
        """Non-member should get 403."""
        group = PredictionGroup(name="Private", creator_id=seed_user.id, invite_code=_generate_invite_code())
        db_session.add(group)
        db_session.flush()
        
        other_user = User(google_sub="other", email="other@example.com", name="Other")
        db_session.add(other_user)
        db_session.commit()
        
        with app.app_context():
            token = issue_jwt(other_user.id)
        
        client.set_cookie(key="jwt_token", value=token)
        response = client.get(f"/api/scores/history?group_id={group.id}")
        
        assert response.status_code == 403

    def test_history_chronological_order(self, app, client, db_session, seed_user, seed_groups, seed_teams, seed_matches):
        """History should be ordered by kickoff_at ASC."""
        group = PredictionGroup(name="Chrono", creator_id=seed_user.id, invite_code=_generate_invite_code())
        db_session.add(group)
        db_session.flush()
        
        membership = GroupMembership(user_id=seed_user.id, group_id=group.id)
        db_session.add(membership)
        db_session.flush()
        
        # Create predictions for multiple matches
        for i, match in enumerate(seed_matches[:3]):
            match.status = "finished"
            match.home_score = i
            match.away_score = 0
            
            pred = Prediction(user_id=seed_user.id, match_id=match.id, home_score=i, away_score=0)
            db_session.add(pred)
            db_session.flush()
            score = PredictionScore(prediction_id=pred.id, points=3, score_type="exact")
            db_session.add(score)
        
        db_session.commit()
        
        with app.app_context():
            token = issue_jwt(seed_user.id)
        
        client.set_cookie(key="jwt_token", value=token)
        response = client.get(f"/api/scores/history?group_id={group.id}")
        
        assert response.status_code == 200
        history = response.get_json()["history"]
        
        # Verify chronological order
        kickoffs = [h["match"]["kickoff_utc"] for h in history]
        assert kickoffs == sorted(kickoffs, reverse=True)
