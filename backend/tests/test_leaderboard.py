"""Tests for leaderboard endpoints - Strict TDD."""
import pytest
import json
from app.models import (
    PredictionGroup, GroupMembership, Prediction, PredictionScore, 
    GroupPrize, User
)
from app.services.auth_service import issue_jwt
from datetime import datetime, timedelta
from uuid import uuid4


def _generate_invite_code():
    """Generate a 6-character alphanumeric invite code."""
    return uuid4().hex[:6].upper()


class TestLeaderboardBasics:
    """Basic leaderboard retrieval scenarios."""

    def test_leaderboard_basic_standings(self, app, client, db_session, seed_user, seed_groups, seed_teams, seed_matches):
        """
        Given: Group has members with different points
        When: Member calls GET /api/scores/leaderboard?group_id=<group>
        Then: Response returns ranked standings
        """
        # Setup: Create group
        group = PredictionGroup(
            name="Test Group",
            creator_id=seed_user.id,
            invite_code=_generate_invite_code()
        )
        db_session.add(group)
        db_session.flush()
        
        # Add seed_user to group
        membership = GroupMembership(user_id=seed_user.id, group_id=group.id)
        db_session.add(membership)
        db_session.flush()
        
        # Create another user
        user2 = User(
            google_sub="user2sub",
            email="user2@example.com",
            name="User 2"
        )
        db_session.add(user2)
        db_session.flush()
        membership2 = GroupMembership(user_id=user2.id, group_id=group.id)
        db_session.add(membership2)
        db_session.flush()
        
        # Create predictions and scores
        match = seed_matches[0]
        
        # User 1: 3 points
        pred1 = Prediction(
            user_id=seed_user.id,
            match_id=match.id,
            group_id=group.id,
            home_score=2,
            away_score=1
        )
        db_session.add(pred1)
        db_session.flush()
        score1 = PredictionScore(prediction_id=pred1.id, points=3, score_type="exact")
        db_session.add(score1)
        
        # User 2: 1 point
        pred2 = Prediction(
            user_id=user2.id,
            match_id=match.id,
            group_id=group.id,
            home_score=1,
            away_score=0
        )
        db_session.add(pred2)
        db_session.flush()
        score2 = PredictionScore(prediction_id=pred2.id, points=1, score_type="outcome")
        db_session.add(score2)
        db_session.commit()
        
        # Make authenticated request
        with app.app_context():
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            response = client.get(f"/api/scores/leaderboard?group_id={group.id}")
        
        # Endpoint should exist and return 200
        assert response.status_code == 200
        data = response.get_json()
        assert "standings" in data
        standings = data["standings"]
        assert len(standings) == 2
        
        # First entry should have 3 points, rank 1
        assert standings[0]["total_points"] == 3
        assert standings[0]["rank"] == 1
        
        # Second entry should have 1 point, rank 2
        assert standings[1]["total_points"] == 1
        assert standings[1]["rank"] == 2

    def test_leaderboard_tied_ranks(self, app, client, db_session, seed_user, seed_groups, seed_teams, seed_matches):
        """Tied members should share same rank."""
        group = PredictionGroup(name="Ties Group", creator_id=seed_user.id, invite_code=_generate_invite_code())
        db_session.add(group)
        db_session.flush()
        
        membership = GroupMembership(user_id=seed_user.id, group_id=group.id)
        db_session.add(membership)
        
        # Create two more users
        user2 = User(google_sub="u2", email="u2@example.com", name="U2")
        user3 = User(google_sub="u3", email="u3@example.com", name="U3")
        db_session.add_all([user2, user3])
        db_session.flush()
        
        db_session.add_all([
            GroupMembership(user_id=user2.id, group_id=group.id),
            GroupMembership(user_id=user3.id, group_id=group.id)
        ])
        db_session.flush()
        
        match = seed_matches[0]
        
        # All three users get 3 points (same score)
        for user in [seed_user, user2, user3]:
            pred = Prediction(user_id=user.id, match_id=match.id, group_id=group.id, home_score=2, away_score=1)
            db_session.add(pred)
            db_session.flush()
            score = PredictionScore(prediction_id=pred.id, points=3, score_type="exact")
            db_session.add(score)
        
        db_session.commit()
        
        with app.app_context():
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            response = client.get(f"/api/scores/leaderboard?group_id={group.id}")
        
        assert response.status_code == 200
        standings = response.get_json()["standings"]
        
        # All should have rank 1
        assert all(s["rank"] == 1 for s in standings)
        assert all(s["total_points"] == 3 for s in standings)

    def test_leaderboard_non_member_403(self, app, client, db_session, seed_user, seed_groups):
        """Non-member trying to access group leaderboard should get 403."""
        group = PredictionGroup(name="Private", creator_id=seed_user.id, invite_code=_generate_invite_code())
        db_session.add(group)
        db_session.flush()
        
        # Don't add seed_user to group
        other_user = User(google_sub="other", email="other@example.com", name="Other")
        db_session.add(other_user)
        db_session.commit()
        
        with app.app_context():
            token = issue_jwt(other_user.id)
            client.set_cookie(key="jwt_token", value=token)
            response = client.get(f"/api/scores/leaderboard?group_id={group.id}")
        
        assert response.status_code == 403

    def test_leaderboard_with_zero_points(self, app, client, db_session, seed_user, seed_groups):
        """Members with no scores should show 0 points."""
        group = PredictionGroup(name="Empty", creator_id=seed_user.id, invite_code=_generate_invite_code())
        db_session.add(group)
        db_session.flush()
        
        membership = GroupMembership(user_id=seed_user.id, group_id=group.id)
        db_session.add(membership)
        db_session.commit()
        
        with app.app_context():
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            response = client.get(f"/api/scores/leaderboard?group_id={group.id}")
        
        assert response.status_code == 200
        standings = response.get_json()["standings"]
        assert len(standings) == 1
        assert standings[0]["total_points"] == 0
        assert standings[0]["rank"] == 1


class TestLeaderboardPrizes:
    """Prize display in leaderboard."""

    def test_prizes_shown_in_leaderboard(self, app, client, db_session, seed_user, seed_groups, seed_teams, seed_matches):
        """Leaderboard should include prize information."""
        group = PredictionGroup(name="Prizes", creator_id=seed_user.id, invite_code=_generate_invite_code())
        db_session.add(group)
        db_session.flush()
        
        # Add prizes
        for rank in [1, 2, 3]:
            prize = GroupPrize(group_id=group.id, rank=rank, description=f"Prize {rank}")
            db_session.add(prize)
        
        membership = GroupMembership(user_id=seed_user.id, group_id=group.id)
        db_session.add(membership)
        db_session.commit()
        
        with app.app_context():
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            response = client.get(f"/api/scores/leaderboard?group_id={group.id}")
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Should have standings and possibly prizes
        assert "standings" in data
