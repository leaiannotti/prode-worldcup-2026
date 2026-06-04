"""Authentication blueprint (stub for Phase 2)."""
from flask import Blueprint

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Phase 2 will implement:
# - GET /login (Google OAuth redirect)
# - GET /callback (OAuth code exchange)
# - GET /me (current user info)
# - POST /logout (clear session)
