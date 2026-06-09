"""User model."""
import uuid
from datetime import datetime
from app.extensions import db


class User(db.Model):
    """User entity for FIFA 2026 prediction app."""
    
    __tablename__ = "users"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    google_sub = db.Column(db.String(255), unique=True, nullable=True, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    picture_url = db.Column(db.String(500))
    password_hash = db.Column(db.String(255), nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    prediction_groups = db.relationship(
        "PredictionGroup",
        backref="creator",
        foreign_keys="PredictionGroup.creator_id",
        lazy=True
    )
    group_memberships = db.relationship(
        "GroupMembership",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )
    predictions = db.relationship(
        "Prediction",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User {self.email}>"
