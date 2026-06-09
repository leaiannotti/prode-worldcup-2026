"""Auth blueprint for authentication endpoints."""
from flask import Blueprint, jsonify, redirect, request, current_app, url_for
from app.extensions import oauth, db
from app.middleware.auth import jwt_required
from app.services.auth_service import upsert_user, issue_jwt, set_jwt_cookie, register_email_user, login_email_user
from app.schemas.auth import UserResponse, EmailRegisterRequest, EmailLoginRequest
from app import create_app

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["GET"])
def login():
    """Redirect to Google OAuth consent screen."""
    redirect_uri = current_app.config.get(
        "OAUTH_REDIRECT_URI",
        url_for("auth.callback", _external=True)
    )
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/callback", methods=["GET"])
def callback():
    """Handle OAuth callback from Google.
    
    Exchanges auth code for user info, upserts user, and sets JWT cookie.
    """
    try:
        # Exchange code for token (Authlib handles this)
        token = oauth.google.authorize_access_token()
    except Exception as e:
        # State mismatch or other OAuth error
        return jsonify({"error": "invalid_oauth_request"}), 400
    
    # Extract user info from token
    user_info = token.get("userinfo")
    if not user_info:
        return jsonify({"error": "missing_user_info"}), 400
    
    # Upsert user in database
    user = upsert_user({
        "sub": user_info.get("sub"),
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "picture": user_info.get("picture")
    })
    
    # Issue JWT
    jwt_token = issue_jwt(user.id)
    
    # Create response and set cookie
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
    print(f"DEBUG FRONTEND_URL: {frontend_url}", flush=True)
    response = redirect(f"{frontend_url}/dashboard")
    set_jwt_cookie(response, jwt_token)
    
    return response


@auth_bp.route("/me", methods=["GET"])
@jwt_required
def me():
    """Get current user info.
    
    Requires valid JWT token. Returns user details.
    """
    from flask import g
    
    user = g.current_user
    schema = UserResponse.model_validate({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "picture": user.picture_url
    })
    
    return jsonify(schema.model_dump()), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user with email and password."""
    try:
        body = EmailRegisterRequest.model_validate(request.get_json() or {})
    except Exception as e:
        return jsonify({"error": "invalid_request", "detail": str(e)}), 400

    try:
        user = register_email_user(body.email, body.password, body.name)
    except ValueError as e:
        if str(e) == "email_already_registered":
            return jsonify({"error": "email_already_registered"}), 409
        return jsonify({"error": str(e)}), 400

    jwt_token = issue_jwt(user.id)
    response = jsonify(UserResponse.model_validate({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "picture": user.picture_url,
    }).model_dump())
    set_jwt_cookie(response, jwt_token)
    return response, 201


@auth_bp.route("/login-email", methods=["POST"])
def login_email():
    """Authenticate with email and password."""
    try:
        body = EmailLoginRequest.model_validate(request.get_json() or {})
    except Exception as e:
        return jsonify({"error": "invalid_request", "detail": str(e)}), 400

    try:
        user = login_email_user(body.email, body.password)
    except ValueError:
        return jsonify({"error": "invalid_credentials"}), 401

    jwt_token = issue_jwt(user.id)
    response = jsonify(UserResponse.model_validate({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "picture": user.picture_url,
    }).model_dump())
    set_jwt_cookie(response, jwt_token)
    return response, 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required
def logout():
    """Logout by clearing JWT cookie.
    
    Requires valid JWT token.
    """
    response = jsonify({}), 200
    # Actually we need to return a response object to set cookie
    response_obj = jsonify({})
    response_obj.set_cookie(
        "jwt_token",
        "",
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=0  # Clear cookie
    )
    return response_obj, 200
