import os
from flask import Flask
from app.extensions import db, migrate, oauth


def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")
    
    app = Flask(__name__)
    
    # Load configuration
    if config_name == "testing":
        from app.config import TestingConfig
        app.config.from_object(TestingConfig)
    elif config_name == "production":
        from app.config import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from app.config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    oauth.init_app(app)
    
    # Configure Google OAuth
    oauth.register(
        "google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"}
    )
    
    # Register blueprints
    with app.app_context():
        from app.blueprints.auth import auth_bp
        from app.blueprints.groups import bp as groups_bp
        from app.blueprints.matches import bp as matches_bp
        from app.blueprints.predictions import bp as predictions_bp
        from app.blueprints.webhook import bp as webhook_bp
        from app.blueprints.scores import scores_bp
        from app.blueprints.activity import bp as activity_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(groups_bp)
        app.register_blueprint(matches_bp)
        app.register_blueprint(predictions_bp)  # now at /api/predictions
        app.register_blueprint(webhook_bp)
        app.register_blueprint(scores_bp, url_prefix="/api/scores")
        app.register_blueprint(activity_bp)
    
    # Register CLI commands
    from app.seed import seed_command
    app.cli.add_command(seed_command)

    @app.before_request
    def before_request():
        """Create tables if they don't exist (for dev)."""
        db.create_all()

    # Auto-seed on first run if the DB has no match data
    with app.app_context():
        db.create_all()
        from app.models import Match
        if db.session.query(Match).count() == 0:
            from app.seed import load_seed_data
            load_seed_data(db.session)

    return app
