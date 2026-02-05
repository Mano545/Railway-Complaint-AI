"""
Authentication routes: register, login, JWT-protected user info.
"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import User
from config import ROLE_USER, ROLES
from services.auth_service import hash_password, verify_password, create_access_token, decode_token

auth_bp = Blueprint("auth", __name__)


def _require_auth():
    """Extract and validate JWT from Authorization header. Returns (user_id, email, role) or None."""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None
    return payload.get("sub"), payload.get("email"), payload.get("role")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user (role=user by default)."""
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    full_name = (data.get("full_name") or data.get("fullName") or "").strip()
    if not email:
        return jsonify({"error": "Email is required"}), 400
    if not password or len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if not full_name:
        return jsonify({"error": "Full name is required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409
    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=ROLE_USER,
    )
    db.session.add(user)
    db.session.commit()
    token = create_access_token(user.id, user.email, user.role)
    return jsonify({
        "success": True,
        "user": user.to_dict(include_email=True),
        "accessToken": token,
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login and return JWT."""
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        return jsonify({"error": "Invalid email or password"}), 401
    if not user.is_active:
        return jsonify({"error": "Account is disabled"}), 403
    token = create_access_token(user.id, user.email, user.role)
    return jsonify({
        "success": True,
        "user": user.to_dict(include_email=True),
        "accessToken": token,
    })


@auth_bp.route("/me", methods=["GET"])
def me():
    """Return current user from JWT."""
    auth = _require_auth()
    if not auth:
        return jsonify({"error": "Unauthorized"}), 401
    user_id_str, email, _ = auth
    user = User.query.get(int(user_id_str))
    if not user or user.email != email:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"success": True, "user": user.to_dict(include_email=True)})
