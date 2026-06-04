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
