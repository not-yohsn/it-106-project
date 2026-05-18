"""Notification endpoints for /api/v1. Owner-only access."""

from flask import g, jsonify, request

from ...extensions import db
from ...models import Notification
from . import api_v1_bp
from .auth_helpers import api_login_required


def _parse_pagination():
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


@api_v1_bp.route("/notifications", methods=["GET"])
@api_login_required
def list_notifications():
    page, per_page = _parse_pagination()
    pagination = (
        Notification.query.filter_by(user_id=g.current_api_user.user_id)
        .order_by(Notification.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return jsonify({
        "data": [n.to_dict() for n in pagination.items],
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
    }), 200


@api_v1_bp.route("/notifications/<int:notification_id>", methods=["GET"])
@api_login_required
def get_notification(notification_id):
    notif = Notification.query.get(notification_id)
    if notif is None:
        return jsonify({"error": "not_found"}), 404
    if notif.user_id != g.current_api_user.user_id:
        return jsonify({"error": "forbidden"}), 403
    return jsonify({"data": notif.to_dict()}), 200


@api_v1_bp.route("/notifications/<int:notification_id>", methods=["PUT"])
@api_login_required
def update_notification(notification_id):
    notif = Notification.query.get(notification_id)
    if notif is None:
        return jsonify({"error": "not_found"}), 404
    if notif.user_id != g.current_api_user.user_id:
        return jsonify({"error": "forbidden"}), 403
    payload = request.get_json(silent=True) or {}
    if "is_read" in payload:
        notif.is_read = bool(payload["is_read"])
    db.session.commit()
    return jsonify({"data": notif.to_dict()}), 200


@api_v1_bp.route("/notifications/<int:notification_id>", methods=["DELETE"])
@api_login_required
def delete_notification(notification_id):
    notif = Notification.query.get(notification_id)
    if notif is None:
        return jsonify({"error": "not_found"}), 404
    if notif.user_id != g.current_api_user.user_id:
        return jsonify({"error": "forbidden"}), 403
    db.session.delete(notif)
    db.session.commit()
    return ("", 204)
