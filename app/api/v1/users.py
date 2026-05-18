"""User-resource endpoints for /api/v1."""

from flask import g, jsonify, request

from ...extensions import db
from ...models import User
from . import api_v1_bp
from .auth_helpers import api_admin_required, api_login_required


def _parse_pagination():
    """Read ?page & ?per_page with sane defaults and clamping."""
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = int(request.args.get("per_page", 20))
    except (TypeError, ValueError):
        per_page = 20
    per_page = max(1, min(per_page, 100))
    return page, per_page


@api_v1_bp.route("/me", methods=["GET"])
@api_login_required
def me():
    return jsonify({"data": g.current_api_user.to_dict()}), 200


@api_v1_bp.route("/users", methods=["GET"])
@api_admin_required
def list_users():
    page, per_page = _parse_pagination()
    pagination = User.query.order_by(User.user_id.asc()).paginate(
        page=page, per_page=per_page, error_out=False,
    )
    return jsonify({
        "data": [u.to_dict() for u in pagination.items],
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
    }), 200


@api_v1_bp.route("/users/<int:user_id>", methods=["GET"])
@api_login_required
def get_user(user_id):
    if g.current_api_user.user_id != user_id and g.current_api_user.role != "admin":
        return jsonify({"error": "forbidden"}), 403
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"data": user.to_dict()}), 200


@api_v1_bp.route("/users/<int:user_id>", methods=["PUT"])
@api_admin_required
def update_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "not_found"}), 404
    payload = request.get_json(silent=True) or {}
    fields = {}
    if "name" in payload:
        name = (payload["name"] or "").strip()
        if not name:
            fields["name"] = "cannot be empty"
        else:
            user.name = name
    if "email" in payload:
        email = (payload["email"] or "").strip().lower()
        if not email:
            fields["email"] = "cannot be empty"
        else:
            user.email = email
    if "phone" in payload:
        user.phone = (payload["phone"] or "").strip() or None
    if "role" in payload:
        role = payload["role"]
        if role not in ("student", "staff", "admin"):
            fields["role"] = "must be one of: student, staff, admin"
        else:
            user.role = role
    if fields:
        db.session.rollback()
        return jsonify({"error": "validation_failed", "fields": fields}), 400
    db.session.commit()
    return jsonify({"data": user.to_dict()}), 200


@api_v1_bp.route("/users/<int:user_id>", methods=["DELETE"])
@api_admin_required
def delete_user(user_id):
    if g.current_api_user.user_id == user_id:
        return jsonify({
            "error": "forbidden",
            "detail": "an admin cannot delete their own account via the API",
        }), 403
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "not_found"}), 404
    db.session.delete(user)
    db.session.commit()
    return ("", 204)
