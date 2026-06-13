import os
from flask import Flask
from app.extensions import db, migrate, oauth, cors


def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")
    
    # Determine CORS origin from env (REQ-7)
    frontend_url = os.getenv("FRONTEND_URL")
    if not frontend_url and os.getenv("FLASK_ENV") == "production":
        raise RuntimeError("FRONTEND_URL is required in production")
    origin = frontend_url or "http://localhost:5173"
    
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
    cors.init_app(app, resources={r"/api/*": {
        "origins": [origin],
        "supports_credentials": True,
    }})
    
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
        from app.blueprints.admin import bp as admin_bp
        from app.blueprints.version import bp as version_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(groups_bp)
        app.register_blueprint(matches_bp)
        app.register_blueprint(predictions_bp)
        app.register_blueprint(webhook_bp)
        app.register_blueprint(scores_bp, url_prefix="/api/scores")
        app.register_blueprint(activity_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(version_bp)
    
    # Register CLI commands
    from app.seed import seed_command
    app.cli.add_command(seed_command)

    @app.route("/health", methods=["GET"])
    def health():
        """Health endpoint for smoke tests (T-12-ter)."""
        return {"status": "ok"}, 200

    @app.before_request
    def before_request():
        """Create tables if they don't exist (for dev)."""
        db.create_all()

    # Auto-seed on first run if the DB has no match data (skipped in testing)
    if config_name != "testing":
        with app.app_context():
            db.create_all()
            from app.models import Match
            if db.session.query(Match).count() == 0:
                from app.seed import load_seed_data
                load_seed_data(db.session)

    return app
