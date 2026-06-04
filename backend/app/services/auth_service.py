"""Authentication service for JWT and user management."""
from datetime import datetime, timedelta
from typing import Dict, Any
import jwt
from flask import current_app, Flask
from app.extensions import db
from app.models import User


def upsert_user(google_info: Dict[str, Any]) -> User:
    """Create or update a user from Google OAuth info.
    
    Args:
        google_info: Dict with keys 'sub', 'email', 'name', 'picture'
        
    Returns:
        User object (created or updated)
    """
    google_sub = google_info.get("sub")
    email = google_info.get("email")
    name = google_info.get("name")
    picture = google_info.get("picture")
    
    # Try to find existing user by google_sub
    user = db.session.query(User).filter_by(google_sub=google_sub).first()
    
    if user:
        # Update existing user
        user.name = name
        user.picture_url = picture
        user.last_login_at = datetime.utcnow()
    else:
        # Create new user
        user = User(
            google_sub=google_sub,
            email=email,
            name=name,
            picture_url=picture,
            last_login_at=datetime.utcnow()
        )
        db.session.add(user)
    
    db.session.commit()
    return user


def issue_jwt(user_id: str) -> str:
    """Generate a signed JWT token for a user.
    
    Args:
        user_id: UUID of the user
        
    Returns:
        Signed JWT token string
    """
    issued_at = datetime.utcnow()
    expires_at = issued_at + current_app.config["JWT_EXPIRATION"]
    
    payload = {
        "user_id": user_id,
        "iat": issued_at,
        "exp": expires_at
    }
    
    token = jwt.encode(
        payload,
        current_app.config["JWT_SECRET"],
        algorithm="HS256"
    )
    
    return token


def set_jwt_cookie(response, token: str):
    """Set JWT token as httpOnly cookie on response.
    
    Args:
        response: Flask response object
        token: JWT token string
    """
    response.set_cookie(
        "jwt_token",
        token,
        httponly=True,
        secure=True,  # HTTPS only in production
        samesite="Lax",
        max_age=int(7 * 24 * 60 * 60)  # 7 days in seconds
    )


def validate_jwt(token: str) -> Dict[str, Any]:
    """Validate and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dict
        
    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET"],
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("token_expired")
    except (jwt.InvalidSignatureError, jwt.DecodeError):
        raise ValueError("invalid_token")


def get_current_user(token: str) -> User:
    """Get the current user from a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        User object
        
    Raises:
        ValueError: If token is invalid or user not found
    """
    payload = validate_jwt(token)
    user_id = payload.get("user_id")
    
    if not user_id:
        raise ValueError("invalid_token")
    
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        raise ValueError("user_not_found")
    
    return user
