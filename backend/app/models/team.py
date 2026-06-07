"""Team and group models."""
from app.extensions import db


class WorldCupGroup(db.Model):
    """FIFA 2026 World Cup group (A through L)."""
    
    __tablename__ = "world_cup_groups"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(1), unique=True, nullable=False, index=True)
    
    # Relationships
    teams = db.relationship(
        "Team",
        backref="group",
        lazy=True,
        cascade="all, delete-orphan"
    )
    matches = db.relationship(
        "Match",
        backref="group",
        lazy=True,
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<WorldCupGroup {self.name}>"


class Team(db.Model):
    """National team competing in FIFA 2026."""
    
    __tablename__ = "teams"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(3), unique=True, nullable=False, index=True)
    world_cup_group_id = db.Column(
        db.Integer,
        db.ForeignKey("world_cup_groups.id"),
        nullable=False,
        index=True
    )
    name = db.Column(db.String(100), nullable=False, server_default="")
    flag_url = db.Column(db.String(500), nullable=True)
    
    # Relationships
    home_matches = db.relationship(
        "Match",
        foreign_keys="Match.home_team_id",
        backref="home_team",
        lazy=True
    )
    away_matches = db.relationship(
        "Match",
        foreign_keys="Match.away_team_id",
        backref="away_team",
        lazy=True
    )
    
    def __repr__(self):
        return f"<Team {self.code}>"
