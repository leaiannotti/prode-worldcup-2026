"""Tests for prediction distribution endpoint."""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4


def _invite_code():
    return uuid4().hex[:6].upper()


def _auth_client(app, client, user_id):
    from app.services.auth_service import issue_jwt
    token = issue_jwt(user_id)
    client.set_cookie(key="jwt_token", value=token)
    return client


def _make_match(db_session, seed_groups, seed_teams, deadline_offset_hours):
    """Create a match whose deadline is now + offset_hours (negative = in past)."""
    from app.models import Match

    now = datetime.utcnow()
    deadline = now + timedelta(hours=deadline_offset_hours)
    kickoff = deadline + timedelta(hours=24)
    match = Match(
        home_team_id=seed_teams[0].id,
        away_team_id=seed_teams[1].id,
        world_cup_group_id=seed_groups[0].id,
        kickoff_utc=kickoff,
        deadline_utc=deadline,
        status="scheduled",
    )
    db_session.add(match)
    db_session.commit()
    return match


class TestDistributionEndpoint:
    """Integration tests for GET /api/matches/<id>/distribution."""

    def test_distribution_unauthenticated(self, client, seed_groups, seed_teams, db_session):
        """Endpoint requires authentication."""
        response = client.get("/api/matches/999/distribution")
        assert response.status_code == 401

    def test_distribution_match_not_found(
        self, app, client, seed_user, seed_groups
    ):
        """Non-existent match → 404."""
        with app.app_context():
            _auth_client(app, client, seed_user.id)
            response = client.get("/api/matches/99999/distribution")

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_distribution_pre_deadline(
        self, app, client, db_session, seed_user, seed_groups, seed_teams
    ):
        """Before deadline → {available: false, reason: pre_deadline} with 200."""
        with app.app_context():
            match = _make_match(db_session, seed_groups, seed_teams, deadline_offset_hours=+48)
            match_id = match.id

            _auth_client(app, client, seed_user.id)
            response = client.get(f"/api/matches/{match_id}/distribution")

        assert response.status_code == 200
        data = response.get_json()
        assert data["available"] is False
        assert data["reason"] == "pre_deadline"

    def test_distribution_post_deadline_no_predictions(
        self, app, client, db_session, seed_user, seed_groups, seed_teams
    ):
        """After deadline with 0 predictions → available:true, all pcts 0."""
        with app.app_context():
            match = _make_match(db_session, seed_groups, seed_teams, deadline_offset_hours=-1)
            match_id = match.id

            _auth_client(app, client, seed_user.id)
            response = client.get(f"/api/matches/{match_id}/distribution")

        assert response.status_code == 200
        data = response.get_json()
        assert data["available"] is True
        assert data["match_id"] == match_id
        assert data["total_predictions"] == 0
        assert data["home_win_pct"] == 0
        assert data["draw_pct"] == 0
        assert data["away_win_pct"] == 0

    def test_distribution_post_deadline(
        self, app, client, db_session, seed_user, seed_groups, seed_teams
    ):
        """After deadline: percentages reflect actual predictions."""
        from app.models import Prediction, PredictionGroup, GroupMembership, User

        with app.app_context():
            match = _make_match(db_session, seed_groups, seed_teams, deadline_offset_hours=-1)
            match_id = match.id

            group = PredictionGroup(
                name="Dist Group",
                creator_id=seed_user.id,
                invite_code=_invite_code(),
            )
            db_session.add(group)
            db_session.flush()

            # 10 unique users: 5 home wins (1-0), 2 draws (0-0), 3 away wins (0-1)
            users = []
            for i in range(10):
                u = User(
                    google_sub=f"dist-u{i}",
                    email=f"dist-u{i}@example.com",
                    name=f"DU{i}",
                )
                db_session.add(u)
                users.append(u)
            db_session.flush()

            for i, u in enumerate(users):
                db_session.add(GroupMembership(
                    user_id=u.id, group_id=group.id, role="member"
                ))
                if i < 5:
                    home, away = 1, 0  # home win
                elif i < 7:
                    home, away = 0, 0  # draw
                else:
                    home, away = 0, 1  # away win

                db_session.add(Prediction(
                    user_id=u.id,
                    match_id=match_id,
                    group_id=group.id,
                    home_score=home,
                    away_score=away,
                ))
            db_session.commit()

            _auth_client(app, client, seed_user.id)
            response = client.get(f"/api/matches/{match_id}/distribution")

        assert response.status_code == 200
        data = response.get_json()
        assert data["available"] is True
        assert data["total_predictions"] == 10
        assert data["home_win_pct"] == 50.0
        assert data["draw_pct"] == 20.0
        assert data["away_win_pct"] == 30.0
        # Must sum to 100
        total = data["home_win_pct"] + data["draw_pct"] + data["away_win_pct"]
        assert abs(total - 100.0) < 0.01

    def test_distribution_deduplication(
        self, app, client, db_session, seed_user, seed_groups, seed_teams
    ):
        """User in 3 groups counts as 1 vote, not 3."""
        from app.models import Prediction, PredictionGroup, GroupMembership, User

        with app.app_context():
            match = _make_match(db_session, seed_groups, seed_teams, deadline_offset_hours=-1)
            match_id = match.id

            # single user predicted in 3 groups (all home wins)
            multi_user = User(
                google_sub="dedup-user",
                email="dedup@example.com",
                name="Dedup User",
            )
            db_session.add(multi_user)
            db_session.flush()

            for i in range(3):
                grp = PredictionGroup(
                    name=f"Dedup Group {i}",
                    creator_id=seed_user.id,
                    invite_code=_invite_code(),
                )
                db_session.add(grp)
                db_session.flush()
                db_session.add(GroupMembership(
                    user_id=multi_user.id, group_id=grp.id, role="member"
                ))
                db_session.add(Prediction(
                    user_id=multi_user.id,
                    match_id=match_id,
                    group_id=grp.id,
                    home_score=1,
                    away_score=0,
                ))
            db_session.commit()

            _auth_client(app, client, seed_user.id)
            response = client.get(f"/api/matches/{match_id}/distribution")

        assert response.status_code == 200
        data = response.get_json()
        # multi_user should count as 1, not 3
        assert data["total_predictions"] == 1
        assert data["home_win_pct"] == 100.0
