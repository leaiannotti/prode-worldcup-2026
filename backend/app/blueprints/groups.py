"""Groups blueprint — prediction group management."""
import uuid
from flask import Blueprint, request, jsonify, g
from app.extensions import db
from app.models import PredictionGroup, GroupMembership, GroupPrize, User
from app.schemas.group import (
    CreateGroupRequest,
    JoinGroupRequest,
    SetPrizesRequest,
    GroupResponse,
    GroupDetailResponse,
    MemberResponse,
    PrizeResponse,
)
from app.middleware.auth import jwt_required
from pydantic import ValidationError

bp = Blueprint("groups", __name__, url_prefix="/api/groups")


def _generate_invite_code():
    """Generate a 6-8 character alphanumeric invite code."""
    return uuid.uuid4().hex[:6].upper()


def _is_group_member(user_id: str, group_id: str) -> bool:
    """Check if user is a member of the group."""
    return GroupMembership.query.filter_by(
        user_id=user_id, group_id=group_id
    ).first() is not None


def _is_group_owner(user_id: str, group_id: str) -> bool:
    """Check if user is the owner/creator of the group."""
    group = PredictionGroup.query.get(group_id)
    if not group:
        return False
    return group.creator_id == user_id


def _group_to_response(group: PredictionGroup) -> GroupResponse:
    """Build a GroupResponse including the live member count."""
    member_count = GroupMembership.query.filter_by(group_id=group.id).count()
    response = GroupResponse.model_validate(group)
    response.member_count = member_count
    return response


@bp.route("", methods=["POST"])
@jwt_required
def create_group():
    """Create a new prediction group. POST /api/groups"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "invalid_request"}), 422
        
        # Validate request schema
        req = CreateGroupRequest(**data)
    except ValidationError as e:
        return jsonify({"error": "invalid_request", "details": str(e)}), 422
    except Exception:
        return jsonify({"error": "invalid_request"}), 422
    
    # Check for duplicate name
    existing = PredictionGroup.query.filter_by(name=req.name).first()
    if existing:
        return jsonify({"error": "group_name_taken"}), 409
    
    # Create group with current user as creator
    user_id = g.current_user.id
    invite_code = _generate_invite_code()
    
    # Ensure unique invite code
    while PredictionGroup.query.filter_by(invite_code=invite_code).first():
        invite_code = _generate_invite_code()
    
    group = PredictionGroup(
        name=req.name,
        creator_id=user_id,
        invite_code=invite_code,
    )
    db.session.add(group)
    db.session.commit()
    
    # Add creator as admin member
    membership = GroupMembership(
        user_id=user_id,
        group_id=group.id,
        role="admin",
    )
    db.session.add(membership)
    db.session.commit()
    
    # Save prizes if provided
    if req.prizes:
        from app.models.group import GroupPrize
        for prize_req in req.prizes:
            if prize_req.description.strip():
                prize = GroupPrize(
                    group_id=group.id,
                    rank=prize_req.rank,
                    description=prize_req.description.strip(),
                )
                db.session.add(prize)
        db.session.commit()

    # Emit activity event
    from app.services.activity_service import emit_event
    emit_event(
        user_id=user_id,
        event_type="group_created",
        group_id=group.id,
        payload={"group_name": group.name},
    )
    db.session.commit()

    # Return group response
    response = _group_to_response(group)
    return jsonify(response.model_dump()), 201


@bp.route("/join", methods=["POST"])
@jwt_required
def join_group():
    """Join a group using invite code. POST /api/groups/join"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "invalid_request"}), 422
        
        req = JoinGroupRequest(**data)
    except ValidationError as e:
        return jsonify({"error": "invalid_request", "details": str(e)}), 422
    except Exception:
        return jsonify({"error": "invalid_request"}), 422
    
    # Find group by invite code
    group = PredictionGroup.query.filter_by(invite_code=req.invite_code).first()
    if not group:
        return jsonify({"error": "group_not_found"}), 404
    
    user_id = g.current_user.id
    
    # Check if already member
    existing = GroupMembership.query.filter_by(
        user_id=user_id, group_id=group.id
    ).first()
    if existing:
        return jsonify({"error": "already_a_member"}), 409
    
    # Add as member
    membership = GroupMembership(
        user_id=user_id,
        group_id=group.id,
        role="member",
    )
    db.session.add(membership)
    db.session.commit()

    # Emit activity event (best-effort — never blocks join)
    from app.services.activity_service import emit_event
    emit_event(
        user_id=user_id,
        event_type="group_joined",
        group_id=group.id,
        payload={"group_name": group.name},
    )
    db.session.commit()

    response = _group_to_response(group)
    return jsonify(response.model_dump()), 200


@bp.route("", methods=["GET"])
@jwt_required
def list_groups():
    """List user's groups. GET /api/groups"""
    user_id = g.current_user.id

    # Get all groups user is member of
    memberships = GroupMembership.query.filter_by(user_id=user_id).all()
    group_ids = [m.group_id for m in memberships]

    groups = PredictionGroup.query.filter(
        PredictionGroup.id.in_(group_ids)
    ).all() if group_ids else []

    responses = [_group_to_response(g).model_dump() for g in groups]
    return jsonify(responses), 200


@bp.route("/<group_id>", methods=["GET"])
@jwt_required
def get_group(group_id):
    """Get group detail. GET /api/groups/{id}"""
    user_id = g.current_user.id
    
    # Check membership
    if not _is_group_member(user_id, group_id):
        return jsonify({"error": "forbidden"}), 403
    
    group = PredictionGroup.query.get(group_id)
    if not group:
        return jsonify({"error": "not_found"}), 404
    
    # Build detail response with members and prizes
    members_data = []
    for membership in group.memberships:
        user = User.query.get(membership.user_id)
        if user:
            member = MemberResponse(
                user_id=user.id,
                name=user.name,
                picture=user.picture_url,
                role=membership.role,
                joined_at=membership.joined_at,
            )
            members_data.append(member.model_dump())
    
    prizes_data = []
    for prize in group.prizes:
        prize_resp = PrizeResponse(
            rank=prize.rank,
            description=prize.description,
        )
        prizes_data.append(prize_resp.model_dump())
    
    detail = GroupDetailResponse(
        id=group.id,
        name=group.name,
        invite_code=group.invite_code,
        created_at=group.created_at,
        creator_id=group.creator_id,
        members=members_data,
        prizes=prizes_data,
    )
    return jsonify(detail.model_dump()), 200


@bp.route("/<group_id>/members", methods=["GET"])
@jwt_required
def get_group_members(group_id):
    """Get group members. GET /api/groups/{id}/members"""
    user_id = g.current_user.id
    
    # Check membership
    if not _is_group_member(user_id, group_id):
        return jsonify({"error": "forbidden"}), 403
    
    group = PredictionGroup.query.get(group_id)
    if not group:
        return jsonify({"error": "not_found"}), 404
    
    # Get members
    members_data = []
    for membership in group.memberships:
        user = User.query.get(membership.user_id)
        if user:
            member = MemberResponse(
                user_id=user.id,
                name=user.name,
                picture=user.picture_url,
                role=membership.role,
                joined_at=membership.joined_at,
            )
            members_data.append(member.model_dump())
    
    return jsonify(members_data), 200


@bp.route("/<group_id>/prizes", methods=["PUT"])
@jwt_required
def set_group_prizes(group_id):
    """Set group prizes (owner only). PUT /api/groups/{id}/prizes"""
    user_id = g.current_user.id
    
    # Check owner
    if not _is_group_owner(user_id, group_id):
        return jsonify({"error": "forbidden"}), 403
    
    group = PredictionGroup.query.get(group_id)
    if not group:
        return jsonify({"error": "not_found"}), 404
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "invalid_request"}), 422
        
        req = SetPrizesRequest(**data)
    except ValidationError as e:
        return jsonify({"error": "invalid_request", "details": str(e)}), 422
    except Exception:
        return jsonify({"error": "invalid_request"}), 422
    
    # Delete existing prizes
    GroupPrize.query.filter_by(group_id=group_id).delete()
    
    # Create new prizes
    for prize_req in req.prizes:
        prize = GroupPrize(
            group_id=group_id,
            rank=prize_req.rank,
            description=prize_req.description,
        )
        db.session.add(prize)
    
    db.session.commit()
    
    return jsonify({"success": True}), 200


@bp.route("/<group_id>/leave", methods=["POST"])
@jwt_required
def leave_group(group_id):
    """Leave a group. POST /api/groups/:id/leave — non-admins only."""
    user_id = g.current_user.id

    group = PredictionGroup.query.get(group_id)
    if not group:
        return jsonify({"error": "not_found"}), 404

    membership = GroupMembership.query.filter_by(
        user_id=user_id, group_id=group_id
    ).first()
    if not membership:
        return jsonify({"error": "not_member"}), 403

    if membership.role == "admin":
        return jsonify({"error": "admin_cannot_leave"}), 403

    db.session.delete(membership)
    db.session.commit()

    return jsonify({"success": True}), 200


@bp.route("/<group_id>", methods=["DELETE"])
@jwt_required
def delete_group(group_id):
    """DELETE /api/groups/:id — delete a group (admin only)."""
    user_id = g.current_user.id

    group = PredictionGroup.query.get(group_id)
    if not group:
        return jsonify({"error": "not_found"}), 404

    membership = GroupMembership.query.filter_by(
        user_id=user_id, group_id=group_id
    ).first()
    if not membership or membership.role != "admin":
        return jsonify({"error": "forbidden"}), 403

    # Cascade delete everything related
    from app.models import GroupPrize, GroupMembership as GM, Prediction
    GroupPrize.query.filter_by(group_id=group_id).delete()
    GM.query.filter_by(group_id=group_id).delete()
    db.session.delete(group)
    db.session.commit()

    return jsonify({"success": True}), 200
