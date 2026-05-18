"""POST /auth/login and POST /auth/logout for the /api/v1 API."""

from flask import jsonify, request

from ...extensions import db
from ...models import User
from . import api_v1_bp
from .auth_helpers import api_login_required, _resolve_current_api_user


@api_v1_bp.route("/auth/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    if not email or not password:
        return jsonify({
            "error": "validation_failed",
            "fields": {
                "email": "is required" if not email else None,
                "password": "is required" if not password else None,
            },
        }), 400

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return jsonify({"error": "invalid_credentials"}), 401

    raw_token = user.set_api_token()
    db.session.commit()
    return jsonify({"token": raw_token, "user": user.to_dict()}), 200


@api_v1_bp.route("/auth/logout", methods=["POST"])
@api_login_required
def logout():
    user = _resolve_current_api_user()
    if user is not None:
        user.clear_api_token()
        db.session.commit()
    return ("", 204)
