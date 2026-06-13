"""Groups blueprint tests — TDD cycle for prediction groups."""
import pytest
import json
import uuid
from datetime import datetime, timedelta
from app.models import User, PredictionGroup, GroupMembership, GroupPrize
from app.extensions import db


class TestGroupSchemas:
    """Test Pydantic schemas for group requests/responses."""
    
    def test_create_group_request_requires_name(self):
        """CreateGroupRequest schema requires name field."""
        from app.schemas.group import CreateGroupRequest
        
        # Should accept valid name
        request = CreateGroupRequest(name="Oficina")
        assert request.name == "Oficina"
        
        # Should reject missing name via Pydantic validation
        with pytest.raises(Exception):  # ValidationError
            CreateGroupRequest(name="")
    
    def test_group_response_schema_includes_required_fields(self):
        """GroupResponse schema includes id, name, invite_code, created_at."""
        from app.schemas.group import GroupResponse
        
        group_data = {
            "id": str(uuid.uuid4()),
            "name": "Oficina",
            "invite_code": "ABC123",
            "created_at": datetime.utcnow().isoformat()
        }
        schema = GroupResponse.model_validate(group_data)
        
        assert schema.name == "Oficina"
        assert schema.invite_code == "ABC123"
    
    def test_member_response_schema_includes_user_info(self):
        """MemberResponse schema includes user_id, name, picture, role, joined_at."""
        from app.schemas.group import MemberResponse
        
        member_data = {
            "user_id": str(uuid.uuid4()),
            "name": "Test User",
            "picture": "https://example.com/pic.jpg",
            "role": "admin",
            "joined_at": datetime.utcnow().isoformat()
        }
        schema = MemberResponse.model_validate(member_data)
        
        assert schema.name == "Test User"
        assert schema.role == "admin"
    
    def test_prize_request_schema_validates_rank_and_description(self):
        """PrizeRequest schema validates rank (1-3) and description (1-255 chars)."""
        from app.schemas.group import PrizeRequest
        
        # Valid prize
        prize = PrizeRequest(rank=1, description="First place prize")
        assert prize.rank == 1
        assert prize.description == "First place prize"
        
        # Invalid rank (should fail validation)
        with pytest.raises(Exception):  # ValidationError
            PrizeRequest(rank=4, description="Invalid")
    
    def test_patch_prizes_request_schema_trims_and_validates(self):
        """PatchPrizesRequest trims whitespace and rejects empty strings after trim."""
        from app.schemas.group import PatchPrizesRequest
        
        # Valid: all fields
        req = PatchPrizesRequest(first="Pizza", second="Beer", third="Cookie")
        assert req.first == "Pizza"
        assert req.second == "Beer"
        assert req.third == "Cookie"
        
        # Valid: partial fields
        req = PatchPrizesRequest(first="Asado")
        assert req.first == "Asado"
        assert req.second is None
        assert req.third is None
        
        # Trim whitespace
        req = PatchPrizesRequest(first="  Asado  ")
        assert req.first == "Asado"
        
        # Empty after trim should fail
        with pytest.raises(Exception):  # ValidationError
            PatchPrizesRequest(first="   ")
        
        # Too long should fail
        with pytest.raises(Exception):  # ValidationError
            PatchPrizesRequest(first="x" * 201)


class TestGroupService:
    """Test group service functions (if created)."""
    
    # Placeholder for service-level tests
    # Group operations are tightly coupled with Flask request context,
    # so we'll test mostly via blueprint integration tests


class TestGroupBlueprint:
    """Test group blueprint routes."""
    
    def test_create_group_returns_201_with_group_object(self, app, client, seed_user):
        """POST /api/groups creates a group and returns 201 with group object."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            response = client.post(
                "/api/groups",
                data=json.dumps({"name": "Oficina"}),
                content_type="application/json"
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data["name"] == "Oficina"
            assert "invite_code" in data
            assert "id" in data
            assert "created_at" in data
            
            # Verify creator is owner
            group = PredictionGroup.query.filter_by(id=data["id"]).first()
            assert group is not None
            assert group.creator_id == seed_user.id
            membership = GroupMembership.query.filter_by(
                group_id=group.id,
                user_id=seed_user.id
            ).first()
            assert membership is not None
            assert membership.role == "admin"

    def test_create_group_with_prizes_returns_prizes(self, app, client, seed_user):
        """POST /api/groups with prizes returns the created prize tiers."""
        from app.services.auth_service import issue_jwt

        with app.app_context():
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)

            response = client.post(
                "/api/groups",
                data=json.dumps({
                    "name": "Prize League",
                    "prizes": [
                        {"rank": 1, "description": "Winner pizza"},
                        {"rank": 2, "description": "Runner-up beer"},
                    ],
                }),
                content_type="application/json"
            )

            assert response.status_code == 201
            data = json.loads(response.data)
            assert data["prizes"] == [
                {"rank": 1, "description": "Winner pizza"},
                {"rank": 2, "description": "Runner-up beer"},
            ]
    
    def test_create_group_with_duplicate_name_returns_409(self, app, client, seed_user):
        """POST /api/groups with duplicate name returns 409."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            token = issue_jwt(seed_user.id)
            
            # Create first group
            group1 = PredictionGroup(
                name="Oficina",
                invite_code="ABC123",
                creator_id=seed_user.id
            )
            db.session.add(group1)
            db.session.commit()
            
            # Try to create duplicate
            client.set_cookie(key="jwt_token", value=token)
            response = client.post(
                "/api/groups",
                data=json.dumps({"name": "Oficina"}),
                content_type="application/json"
            )
            
            assert response.status_code == 409
            data = json.loads(response.data)
            assert data.get("error") == "group_name_taken"
    
    def test_create_group_with_missing_name_returns_422(self, app, client, seed_user):
        """POST /api/groups with missing name returns 422."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            response = client.post(
                "/api/groups",
                data=json.dumps({}),
                content_type="application/json"
            )
            
            assert response.status_code == 422
    
    def test_create_group_without_auth_returns_401(self, client):
        """POST /api/groups without JWT returns 401."""
        response = client.post(
            "/api/groups",
            data=json.dumps({"name": "Oficina"}),
            content_type="application/json"
        )
        
        assert response.status_code == 401
    
    def test_join_group_with_valid_invite_code_returns_200(self, app, client, seed_user):
        """POST /api/groups/join with valid invite code returns 200."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            # Create a group
            another_user = User(
                google_sub="other-sub",
                email="other@example.com",
                name="Other User",
                picture_url="https://example.com/other.jpg"
            )
            db.session.add(another_user)
            db.session.commit()
            
            group = PredictionGroup(
                name="Shared Group",
                invite_code="SHARE123",
                creator_id=another_user.id
            )
            db.session.add(group)
            db.session.commit()
            
            # Join as seed_user
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            response = client.post(
                "/api/groups/join",
                data=json.dumps({"invite_code": "SHARE123"}),
                content_type="application/json"
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["name"] == "Shared Group"
            
            # Verify membership created
            membership = GroupMembership.query.filter_by(
                group_id=group.id,
                user_id=seed_user.id
            ).first()
            assert membership is not None
            assert membership.role == "member"
    
    def test_join_group_when_already_member_returns_409(self, app, client, seed_user):
        """POST /api/groups/join when already member returns 409."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            # Create group with seed_user as member
            group = PredictionGroup(
                name="My Group",
                invite_code="MYGRP12",
                creator_id=seed_user.id
            )
            db.session.add(group)
            db.session.commit()
            
            membership = GroupMembership(
                user_id=seed_user.id,
                group_id=group.id,
                role="admin"
            )
            db.session.add(membership)
            db.session.commit()
            
            # Try to join again
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            response = client.post(
                "/api/groups/join",
                data=json.dumps({"invite_code": "MYGRP12"}),
                content_type="application/json"
            )
            
            assert response.status_code == 409
            data = json.loads(response.data)
            assert data.get("error") == "already_a_member"
    
    def test_join_group_with_invalid_code_returns_404(self, app, client, seed_user):
        """POST /api/groups/join with invalid code returns 404."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            response = client.post(
                "/api/groups/join",
                data=json.dumps({"invite_code": "BADCODE"}),
                content_type="application/json"
            )
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data.get("error") == "group_not_found"
    
    def test_list_groups_returns_user_groups(self, app, client, seed_user):
        """GET /api/groups returns groups user is member of."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            # Create two groups
            group1 = PredictionGroup(
                name="Group 1",
                invite_code="GRP001",
                creator_id=seed_user.id
            )
            group2 = PredictionGroup(
                name="Group 2",
                invite_code="GRP002",
                creator_id=seed_user.id
            )
            db.session.add_all([group1, group2])
            db.session.commit()
            
            # Add seed_user to group1
            membership = GroupMembership(
                user_id=seed_user.id,
                group_id=group1.id,
                role="admin"
            )
            db.session.add(membership)
            db.session.commit()
            
            # List groups
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            response = client.get("/api/groups")
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["name"] == "Group 1"

    def test_list_groups_includes_prizes(self, app, client, seed_user):
        """GET /api/groups includes prize tiers for detail modal cards."""
        from app.services.auth_service import issue_jwt

        with app.app_context():
            group = PredictionGroup(
                name="Prize List Group",
                invite_code="PRZLST",
                creator_id=seed_user.id
            )
            db.session.add(group)
            db.session.commit()

            membership = GroupMembership(
                user_id=seed_user.id,
                group_id=group.id,
                role="admin"
            )
            prize = GroupPrize(
                group_id=group.id,
                rank=1,
                description="Winner dinner"
            )
            db.session.add_all([membership, prize])
            db.session.commit()

            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)

            response = client.get("/api/groups")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data[0]["prizes"] == [
                {"rank": 1, "description": "Winner dinner"}
            ]
    
    def test_get_group_detail_returns_group_object(self, app, client, seed_user):
        """GET /api/groups/{id} returns group details for member."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            # Create group with seed_user as member
            group = PredictionGroup(
                name="Detail Group",
                invite_code="DETAIL1",
                creator_id=seed_user.id
            )
            db.session.add(group)
            db.session.commit()
            
            membership = GroupMembership(
                user_id=seed_user.id,
                group_id=group.id,
                role="admin"
            )
            db.session.add(membership)
            db.session.commit()
            
            # Get group detail
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            response = client.get(f"/api/groups/{group.id}")
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["name"] == "Detail Group"
    
    def test_get_group_when_not_member_returns_403(self, app, client, seed_user):
        """GET /api/groups/{id} returns 403 when not member."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            # Create group with different creator
            other_user = User(
                google_sub="other-sub",
                email="other@example.com",
                name="Other User",
                picture_url="https://example.com/other.jpg"
            )
            db.session.add(other_user)
            db.session.commit()
            
            group = PredictionGroup(
                name="Private Group",
                invite_code="PRIVATE1",
                creator_id=other_user.id
            )
            db.session.add(group)
            db.session.commit()
            
            # Try to access as seed_user
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            response = client.get(f"/api/groups/{group.id}")
            
            assert response.status_code == 403
    
    def test_get_group_members_returns_member_list(self, app, client, seed_user):
        """GET /api/groups/{id}/members returns member list."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            # Create group
            group = PredictionGroup(
                name="Members Group",
                invite_code="MEMB001",
                creator_id=seed_user.id
            )
            db.session.add(group)
            db.session.commit()
            
            # Add seed_user as admin
            membership = GroupMembership(
                user_id=seed_user.id,
                group_id=group.id,
                role="admin"
            )
            db.session.add(membership)
            db.session.commit()
            
            # Get members
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            response = client.get(f"/api/groups/{group.id}/members")
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) >= 1
            assert any(m["user_id"] == seed_user.id for m in data)
    
    def test_get_group_members_when_not_member_returns_403(self, app, client, seed_user):
        """GET /api/groups/{id}/members returns 403 when not member."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            # Create group with different creator
            other_user = User(
                google_sub="other-sub",
                email="other@example.com",
                name="Other User",
                picture_url="https://example.com/other.jpg"
            )
            db.session.add(other_user)
            db.session.commit()
            
            group = PredictionGroup(
                name="Other Group",
                invite_code="OTHER01",
                creator_id=other_user.id
            )
            db.session.add(group)
            db.session.commit()
            
            # Try to access as seed_user
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            response = client.get(f"/api/groups/{group.id}/members")
            
            assert response.status_code == 403
    
    def test_set_prizes_as_owner_returns_200(self, app, client, seed_user):
        """PUT /api/groups/{id}/prizes as owner returns 200."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            # Create group with seed_user as owner
            group = PredictionGroup(
                name="Prize Group",
                invite_code="PRIZE01",
                creator_id=seed_user.id
            )
            db.session.add(group)
            db.session.commit()
            
            membership = GroupMembership(
                user_id=seed_user.id,
                group_id=group.id,
                role="admin"
            )
            db.session.add(membership)
            db.session.commit()
            
            # Set prizes
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            prizes_data = {
                "prizes": [
                    {"rank": 1, "description": "First place"},
                    {"rank": 2, "description": "Second place"},
                    {"rank": 3, "description": "Third place"}
                ]
            }
            
            response = client.put(
                f"/api/groups/{group.id}/prizes",
                data=json.dumps(prizes_data),
                content_type="application/json"
            )
            
            assert response.status_code == 200
            
            # Verify prizes stored
            prizes = GroupPrize.query.filter_by(group_id=group.id).all()
            assert len(prizes) == 3
    
    def test_set_prizes_as_non_owner_returns_403(self, app, client, seed_user):
        """PUT /api/groups/{id}/prizes as non-owner returns 403."""
        from app.services.auth_service import issue_jwt
        
        with app.app_context():
            # Create group with different owner
            other_user = User(
                google_sub="other-sub",
                email="other@example.com",
                name="Other User",
                picture_url="https://example.com/other.jpg"
            )
            db.session.add(other_user)
            db.session.commit()
            
            group = PredictionGroup(
                name="Owned Group",
                invite_code="OWNED01",
                creator_id=other_user.id
            )
            db.session.add(group)
            db.session.commit()
            
            # Add seed_user as member (not owner)
            membership = GroupMembership(
                user_id=seed_user.id,
                group_id=group.id,
                role="member"
            )
            db.session.add(membership)
            db.session.commit()
            
            # Try to set prizes
            token = issue_jwt(seed_user.id)
            client.set_cookie(key="jwt_token", value=token)
            
            prizes_data = {
                "prizes": [
                    {"rank": 1, "description": "First place"}
                ]
            }
            
            response = client.put(
                f"/api/groups/{group.id}/prizes",
                data=json.dumps(prizes_data),
                content_type="application/json"
            )
            
            assert response.status_code == 403


class TestPatchPrizes:
    """Test PATCH /api/groups/:id/prizes — member or admin can edit prizes."""

    def _auth_client(self, app, client, user_id):
        """Authenticate test client with JWT cookie."""
        from app.services.auth_service import issue_jwt
        token = issue_jwt(user_id)
        client.set_cookie(key="jwt_token", value=token)
        return client

    def _create_group_with_member(self, db_session, user, prizes=None):
        """Create a group with user as member, optional prizes."""
        group = PredictionGroup(
            name="Patch Test Group",
            invite_code="PATCH01",
            creator_id=user.id,
        )
        db_session.add(group)
        db_session.commit()

        membership = GroupMembership(
            user_id=user.id,
            group_id=group.id,
            role="member",
        )
        db_session.add(membership)
        db_session.commit()

        if prizes:
            for rank, description in prizes:
                prize = GroupPrize(
                    group_id=group.id,
                    rank=rank,
                    description=description,
                )
                db_session.add(prize)
            db_session.commit()

        return group

    def test_patch_prizes_as_member_returns_200(self, app, client, db_session, seed_user):
        """Member can PATCH prizes and gets 200 with changed array."""
        with app.app_context():
            group = self._create_group_with_member(
                db_session, seed_user, prizes=[(1, "Pizza")]
            )
            self._auth_client(app, client, seed_user.id)

            response = client.patch(
                f"/api/groups/{group.id}/prizes",
                json={"first": "Asado"},
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["changed"] == [{"rank": 1, "previous": "Pizza", "new": "Asado"}]

    def test_patch_prizes_as_admin_non_member_returns_200(self, app, client, db_session, seed_user):
        """Admin (not member) can PATCH prizes and gets 200 with changed array + DB state."""
        from app.middleware.auth import ADMIN_EMAILS
        from app.models.activity import ActivityEvent

        with app.app_context():
            # Create admin user
            admin_user = User(
                google_sub="admin-sub",
                email=list(ADMIN_EMAILS)[0],
                name="Admin User",
                picture_url="https://example.com/admin.jpg",
            )
            db_session.add(admin_user)
            db_session.commit()

            # Create group WITHOUT admin as member
            group = PredictionGroup(
                name="Admin Test Group",
                invite_code="ADMIN01",
                creator_id=seed_user.id,
            )
            db_session.add(group)
            db_session.commit()

            self._auth_client(app, client, admin_user.id)
            response = client.patch(
                f"/api/groups/{group.id}/prizes",
                json={"first": "Admin Prize"},
            )

            assert response.status_code == 200
            data = response.get_json()

            # 1. changed array reflects the newly created prize (no prior rank 1)
            assert data["changed"] == [{"rank": 1, "previous": None, "new": "Admin Prize"}]

            # 2. Activity event payload confirms actor_is_admin
            events = ActivityEvent.query.filter_by(
                group_id=group.id, event_type="prize_changed"
            ).all()
            assert len(events) == 1
            assert events[0].payload["actor_is_admin"] is True
            assert events[0].payload["rank"] == 1
            assert events[0].payload["previous_value"] is None
            assert events[0].payload["new_value"] == "Admin Prize"

            # 3. DB query confirms GroupPrize was actually persisted
            prizes = GroupPrize.query.filter_by(group_id=group.id).all()
            assert len(prizes) == 1
            assert prizes[0].rank == 1
            assert prizes[0].description == "Admin Prize"

    def test_patch_prizes_as_non_member_returns_403(self, app, client, db_session, seed_user):
        """Non-member non-admin gets 403 on PATCH."""
        with app.app_context():
            other_user = User(
                google_sub="other-sub",
                email="other@example.com",
                name="Other User",
                picture_url="https://example.com/other.jpg",
            )
            db_session.add(other_user)
            db_session.commit()

            group = PredictionGroup(
                name="Private Group",
                invite_code="PRIV01",
                creator_id=other_user.id,
            )
            db_session.add(group)
            db_session.commit()

            self._auth_client(app, client, seed_user.id)
            response = client.patch(
                f"/api/groups/{group.id}/prizes",
                json={"first": "Hacker Prize"},
            )

            assert response.status_code == 403
            assert response.get_json()["error"] == "forbidden"

    def test_patch_prizes_too_long_returns_422(self, app, client, db_session, seed_user):
        """Prize description > 200 chars returns 422."""
        with app.app_context():
            group = self._create_group_with_member(db_session, seed_user)
            self._auth_client(app, client, seed_user.id)

            response = client.patch(
                f"/api/groups/{group.id}/prizes",
                json={"first": "x" * 201},
            )

            assert response.status_code == 422
            assert response.get_json()["error"] == "invalid_request"

    def test_patch_prizes_empty_after_trim_returns_422(self, app, client, db_session, seed_user):
        """Prize description empty after trim returns 422."""
        with app.app_context():
            group = self._create_group_with_member(db_session, seed_user)
            self._auth_client(app, client, seed_user.id)

            response = client.patch(
                f"/api/groups/{group.id}/prizes",
                json={"first": "   "},
            )

            assert response.status_code == 422
            assert response.get_json()["error"] == "invalid_request"

    def test_patch_prizes_missing_key_ignored(self, app, client, db_session, seed_user):
        """Missing rank keys are ignored; only provided keys evaluated."""
        with app.app_context():
            group = self._create_group_with_member(
                db_session, seed_user, prizes=[(1, "A"), (2, "B")]
            )
            self._auth_client(app, client, seed_user.id)

            response = client.patch(
                f"/api/groups/{group.id}/prizes",
                json={"first": "Asado"},
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["changed"] == [{"rank": 1, "previous": "A", "new": "Asado"}]

    def test_patch_prizes_noop_returns_empty_changed(self, app, client, db_session, seed_user):
        """All ranks unchanged → 200 with empty changed array, no events."""
        from app.models.activity import ActivityEvent

        with app.app_context():
            group = self._create_group_with_member(
                db_session, seed_user,
                prizes=[(1, "A"), (2, "B"), (3, "C")],
            )
            self._auth_client(app, client, seed_user.id)

            response = client.patch(
                f"/api/groups/{group.id}/prizes",
                json={"first": "A", "second": "B", "third": "C"},
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["changed"] == []

            # No prize_changed events should be emitted
            events = ActivityEvent.query.filter_by(
                group_id=group.id, event_type="prize_changed"
            ).all()
            assert len(events) == 0

    def test_patch_prizes_two_changes_emits_two_events(self, app, client, db_session, seed_user):
        """Two prizes changed → two prize_changed events with correct payload."""
        from app.models.activity import ActivityEvent

        with app.app_context():
            group = self._create_group_with_member(
                db_session, seed_user,
                prizes=[(1, "A"), (2, "B"), (3, "C")],
            )
            self._auth_client(app, client, seed_user.id)

            response = client.patch(
                f"/api/groups/{group.id}/prizes",
                json={"first": "X", "second": "Y"},
            )

            assert response.status_code == 200
            data = response.get_json()
            assert len(data["changed"]) == 2

            events = ActivityEvent.query.filter_by(
                group_id=group.id, event_type="prize_changed"
            ).order_by(ActivityEvent.payload["rank"].asc()).all()
            assert len(events) == 2

            # Check event payloads
            payloads = [e.payload for e in events]
            assert any(
                p["rank"] == 1 and p["previous_value"] == "A" and p["new_value"] == "X"
                for p in payloads
            )
            assert any(
                p["rank"] == 2 and p["previous_value"] == "B" and p["new_value"] == "Y"
                for p in payloads
            )
            assert all(p["actor_is_admin"] is False for p in payloads)

    def test_patch_prizes_admin_event_payload(self, app, client, db_session, seed_user):
        """Admin PATCH emits prize_changed with actor_is_admin=True."""
        from app.middleware.auth import ADMIN_EMAILS
        from app.models.activity import ActivityEvent

        with app.app_context():
            admin_user = User(
                google_sub="admin-sub",
                email=list(ADMIN_EMAILS)[0],
                name="Admin User",
                picture_url="https://example.com/admin.jpg",
            )
            db_session.add(admin_user)
            db_session.commit()

            group = PredictionGroup(
                name="Admin Event Group",
                invite_code="ADEV01",
                creator_id=seed_user.id,
            )
            db_session.add(group)
            db_session.commit()

            prize = GroupPrize(
                group_id=group.id,
                rank=1,
                description="Old",
            )
            db_session.add(prize)
            db_session.commit()

            self._auth_client(app, client, admin_user.id)
            response = client.patch(
                f"/api/groups/{group.id}/prizes",
                json={"first": "New"},
            )

            assert response.status_code == 200

            events = ActivityEvent.query.filter_by(
                group_id=group.id, event_type="prize_changed"
            ).all()
            assert len(events) == 1
            assert events[0].payload["actor_is_admin"] is True
