"""Prediction group models."""
import uuid
from datetime import datetime
from app.extensions import db


class PredictionGroup(db.Model):
    """Prediction group for a set of users."""
    
    __tablename__ = "prediction_groups"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    creator_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    invite_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    memberships = db.relationship(
        "GroupMembership",
        backref="group",
        lazy=True,
        cascade="all, delete-orphan"
    )
    prizes = db.relationship(
        "GroupPrize",
        backref="group",
        lazy=True,
        order_by="GroupPrize.rank",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<PredictionGroup {self.name}>"


class GroupMembership(db.Model):
    """User membership in a prediction group."""
    
    __tablename__ = "group_memberships"
    
    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id"),
        primary_key=True
    )
    group_id = db.Column(
        db.String(36),
        db.ForeignKey("prediction_groups.id"),
        primary_key=True
    )
    role = db.Column(
        db.String(20),
        nullable=False,
        default="member"
    )  # admin, member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<GroupMembership {self.user_id} in {self.group_id}>"


class GroupPrize(db.Model):
    """Prize tier for a prediction group."""
    
    __tablename__ = "group_prizes"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(
        db.String(36),
        db.ForeignKey("prediction_groups.id"),
        nullable=False,
        index=True
    )
    rank = db.Column(db.Integer, nullable=False)  # 1, 2, or 3
    description = db.Column(db.String(255), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint("group_id", "rank", name="uq_group_rank"),
        db.CheckConstraint("rank BETWEEN 1 AND 3", name="ck_rank_1_3"),
    )
    
    def __repr__(self):
        return f"<GroupPrize {self.group_id} rank {self.rank}>"
