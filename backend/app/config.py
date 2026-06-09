import os
from datetime import timedelta


class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.getenv("JWT_SECRET", "jwt-secret-key")
    JWT_EXPIRATION = timedelta(days=7)


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://prode:prode@localhost:5432/prode_worldcup"
    )
    SQLALCHEMY_ECHO = True
    OAUTH_REDIRECT_URI = os.getenv(
        "OAUTH_REDIRECT_URI",
        "http://localhost:5173/api/auth/callback"
    )


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_ECHO = False
    OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")
