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
    
    # Register blueprints
    with app.app_context():
        from app.blueprints.auth import auth_bp
        app.register_blueprint(auth_bp)
    
    # Register CLI commands
    from app.seed import seed_command
    app.cli.add_command(seed_command)
    
    @app.before_request
    def before_request():
        """Create tables if they don't exist (for dev)."""
        db.create_all()
    
    return app
