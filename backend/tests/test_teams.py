"""Tests for team identity — name and flag_url fields."""
import pytest


class TestTeamModel:
    """Unit tests for Team model fields."""

    def test_team_has_name_and_flag_url(self, db_session, seed_groups):
        """Team model accepts name and flag_url on creation."""
        from app.models import Team

        team = Team(
            code="ARG",
            world_cup_group_id=seed_groups[0].id,
            name="Argentina",
            flag_url="https://flagcdn.com/w80/ar.png",
        )
        db_session.add(team)
        db_session.commit()

        fetched = db_session.query(Team).filter_by(code="ARG").first()
        assert fetched.name == "Argentina"
        assert fetched.flag_url == "https://flagcdn.com/w80/ar.png"

    def test_team_flag_url_is_nullable(self, db_session, seed_groups):
        """flag_url can be null — missing ISO2 mappings must not block seeding."""
        from app.models import Team

        team = Team(
            code="XYZ",
            world_cup_group_id=seed_groups[0].id,
            name="Unknown FC",
            flag_url=None,
        )
        db_session.add(team)
        db_session.commit()

        fetched = db_session.query(Team).filter_by(code="XYZ").first()
        assert fetched.flag_url is None
        assert fetched.name == "Unknown FC"

    def test_team_name_defaults_to_empty_string_when_not_provided(
        self, db_session, seed_groups
    ):
        """Team.name has server_default '' — existing rows survive migration."""
        from app.models import Team

        # Create without explicit name — relies on server_default or model default
        team = Team(
            code="TST",
            world_cup_group_id=seed_groups[0].id,
        )
        db_session.add(team)
        db_session.commit()

        fetched = db_session.query(Team).filter_by(code="TST").first()
        # name must be a string (empty or set by default) — not None
        assert fetched.name is not None
        assert isinstance(fetched.name, str)


class TestTeamSerialization:
    """Integration tests: match endpoints include team name and flag_url."""

    def _make_token(self, app, user):
        from app.services.auth_service import issue_jwt
        return issue_jwt(user.id)

    def test_match_response_includes_team_name(
        self, app, client, seed_user, seed_matches, db_session
    ):
        """GET /api/matches response includes name in home_team and away_team."""
        with app.app_context():
            # Give the first match's teams proper names
            match = seed_matches[0]
            match.home_team.name = "Argentina"
            match.away_team.name = "Brazil"
            db_session.commit()

            token = self._make_token(app, seed_user)
            client.set_cookie(key="jwt_token", value=token)
            response = client.get("/api/matches")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) > 0
        first = data[0]
        assert "name" in first["home_team"]
        assert "name" in first["away_team"]

    def test_match_response_includes_flag_url(
        self, app, client, seed_user, seed_matches, db_session
    ):
        """GET /api/matches response includes flag_url in home_team and away_team."""
        with app.app_context():
            match = seed_matches[0]
            match.home_team.flag_url = "https://flagcdn.com/w80/ar.png"
            match.away_team.flag_url = "https://flagcdn.com/w80/br.png"
            db_session.commit()

            token = self._make_token(app, seed_user)
            client.set_cookie(key="jwt_token", value=token)
            response = client.get("/api/matches")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) > 0
        first = data[0]
        assert "flag_url" in first["home_team"]
        assert "flag_url" in first["away_team"]

    def test_match_detail_includes_team_name_and_flag_url(
        self, app, client, seed_user, seed_matches, db_session
    ):
        """GET /api/matches/<id> response includes name and flag_url."""
        with app.app_context():
            match = seed_matches[0]
            match.home_team.name = "Spain"
            match.home_team.flag_url = "https://flagcdn.com/w80/es.png"
            match.away_team.name = "Germany"
            match.away_team.flag_url = "https://flagcdn.com/w80/de.png"
            db_session.commit()

            token = self._make_token(app, seed_user)
            client.set_cookie(key="jwt_token", value=token)
            response = client.get(f"/api/matches/{match.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["home_team"]["name"] == "Spain"
        assert data["home_team"]["flag_url"] == "https://flagcdn.com/w80/es.png"
        assert data["away_team"]["name"] == "Germany"
        assert data["away_team"]["flag_url"] == "https://flagcdn.com/w80/de.png"
