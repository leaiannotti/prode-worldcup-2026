"""Tests for my-standing endpoint."""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta


def _invite_code():
    return uuid4().hex[:6].upper()


def _make_token(app, user_id):
    from app.services.auth_service import issue_jwt
    return issue_jwt(user_id)


def _auth_client(app, client, user_id):
    token = _make_token(app, user_id)
    client.set_cookie(key="jwt_token", value=token)
    return client


class TestMyStanding:
    """Integration tests for GET /api/scores/my-standing."""

    def test_my_standing_unauthenticated_returns_401(self, client):
        """Endpoint requires authentication."""
        response = client.get("/api/scores/my-standing")
        assert response.status_code == 401

    def test_my_standing_no_groups(self, app, client, seed_user):
        """User with no group memberships returns empty array."""
        with app.app_context():
            _auth_client(app, client, seed_user.id)
            response = client.get("/api/scores/my-standing")

        assert response.status_code == 200
        data = response.get_json()
        assert data == []

    def test_my_standing_single_group(
        self, app, client, db_session, seed_user, seed_groups, seed_teams, seed_matches
    ):
        """User in one group gets one standing entry with correct fields."""
        from app.models import PredictionGroup, GroupMembership

        with app.app_context():
            group = PredictionGroup(
                name="Solo Group",
                creator_id=seed_user.id,
                invite_code=_invite_code(),
            )
            db_session.add(group)
            db_session.flush()
            db_session.add(GroupMembership(
                user_id=seed_user.id, group_id=group.id, role="admin"
            ))
            db_session.commit()

            _auth_client(app, client, seed_user.id)
            response = client.get("/api/scores/my-standing")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        entry = data[0]
        assert "group_id" in entry
        assert entry["group_name"] == "Solo Group"
        assert entry["rank"] == 1
        assert entry["total_points"] == 0
        assert entry["member_count"] == 1

    def test_my_standing_multiple_groups(
        self, app, client, db_session, seed_user, seed_groups, seed_teams, seed_matches
    ):
        """User in two groups sees one entry per group."""
        from app.models import PredictionGroup, GroupMembership

        with app.app_context():
            g1 = PredictionGroup(
                name="Family League",
                creator_id=seed_user.id,
                invite_code=_invite_code(),
            )
            g2 = PredictionGroup(
                name="Office Heroes",
                creator_id=seed_user.id,
                invite_code=_invite_code(),
            )
            db_session.add_all([g1, g2])
            db_session.flush()
            db_session.add_all([
                GroupMembership(user_id=seed_user.id, group_id=g1.id, role="admin"),
                GroupMembership(user_id=seed_user.id, group_id=g2.id, role="admin"),
            ])
            db_session.commit()

            _auth_client(app, client, seed_user.id)
            response = client.get("/api/scores/my-standing")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        group_names = {entry["group_name"] for entry in data}
        assert "Family League" in group_names
        assert "Office Heroes" in group_names

    def test_my_standing_rank_calculation(
        self, app, client, db_session, seed_user, seed_groups, seed_teams, seed_matches
    ):
        """Rank reflects the user's position in the group by points."""
        from app.models import (
            PredictionGroup, GroupMembership, Prediction, PredictionScore, User
        )

        with app.app_context():
            # user2 will have more points than seed_user
            user2 = User(
                google_sub="u2-rank",
                email="u2rank@example.com",
                name="User2",
            )
            db_session.add(user2)
            db_session.flush()

            group = PredictionGroup(
                name="Rank Test",
                creator_id=seed_user.id,
                invite_code=_invite_code(),
            )
            db_session.add(group)
            db_session.flush()

            db_session.add_all([
                GroupMembership(user_id=seed_user.id, group_id=group.id, role="admin"),
                GroupMembership(user_id=user2.id, group_id=group.id, role="member"),
            ])
            db_session.flush()

            match = seed_matches[0]

            # seed_user: 0 points (no scores)
            pred1 = Prediction(
                user_id=seed_user.id,
                match_id=match.id,
                group_id=group.id,
                home_score=1,
                away_score=0,
            )
            # user2: 3 points
            pred2 = Prediction(
                user_id=user2.id,
                match_id=match.id,
                group_id=group.id,
                home_score=2,
                away_score=0,
            )
            db_session.add_all([pred1, pred2])
            db_session.flush()

            db_session.add(PredictionScore(
                prediction_id=pred2.id, points=3, score_type="exact"
            ))
            db_session.commit()

            _auth_client(app, client, seed_user.id)
            response = client.get("/api/scores/my-standing")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        entry = data[0]
        # seed_user has fewer points → rank 2
        assert entry["rank"] == 2
        assert entry["total_points"] == 0

    def test_my_standing_rank_ties(
        self, app, client, db_session, seed_user, seed_groups, seed_teams, seed_matches
    ):
        """Tied users share the same rank."""
        from app.models import (
            PredictionGroup, GroupMembership, Prediction, PredictionScore, User
        )

        with app.app_context():
            user2 = User(
                google_sub="u2-tie",
                email="u2tie@example.com",
                name="User2Tie",
            )
            db_session.add(user2)
            db_session.flush()

            group = PredictionGroup(
                name="Ties",
                creator_id=seed_user.id,
                invite_code=_invite_code(),
            )
            db_session.add(group)
            db_session.flush()

            db_session.add_all([
                GroupMembership(user_id=seed_user.id, group_id=group.id, role="admin"),
                GroupMembership(user_id=user2.id, group_id=group.id, role="member"),
            ])
            db_session.flush()

            match = seed_matches[0]
            # Both users get 3 points
            for u in [seed_user, user2]:
                pred = Prediction(
                    user_id=u.id,
                    match_id=match.id,
                    group_id=group.id,
                    home_score=1,
                    away_score=0,
                )
                db_session.add(pred)
                db_session.flush()
                db_session.add(PredictionScore(
                    prediction_id=pred.id, points=3, score_type="exact"
                ))
            db_session.commit()

            _auth_client(app, client, seed_user.id)
            response = client.get("/api/scores/my-standing")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        # Both have same points — seed_user should be rank 1
        assert data[0]["rank"] == 1
        assert data[0]["total_points"] == 3
