"""Auth middleware for JWT validation."""
from functools import wraps
from flask import request, jsonify, g
from app.services.auth_service import get_current_user


def jwt_required(f):
    """Decorator to require a valid JWT token.
    
    Validates the JWT from cookies, sets g.current_user on success.
    Returns 401 on missing, expired, or invalid token.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from cookies
        token = request.cookies.get("jwt_token")
        
        # Debug: log all cookies
        if not token:
            print(f"DEBUG: No jwt_token cookie. Request path: {request.path}")
            print(f"DEBUG: All cookies: {request.cookies}")
        
        if not token:
            return jsonify({"error": "missing_token"}), 401
        
        try:
            # Validate and get user
            user = get_current_user(token)
            g.current_user = user
            return f(*args, **kwargs)
        
        except ValueError as e:
            error_msg = str(e)
            return jsonify({"error": error_msg}), 401
        
        except Exception as e:
            # Catch unexpected errors
            print(f"DEBUG jwt_required unexpected error: {type(e).__name__}: {e}")
            return jsonify({"error": "invalid_token"}), 401
    
    return decorated_function
