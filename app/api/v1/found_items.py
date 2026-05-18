"""Found-item endpoints for /api/v1."""

from datetime import date

from flask import g, jsonify, request

from ...extensions import db
from ...models import FoundItem
from . import api_v1_bp
from .auth_helpers import api_login_required, api_staff_required


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


def _parse_date(value, field_name, fields):
    if value is None or value == "":
        return None
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        fields[field_name] = "must be YYYY-MM-DD"
        return None


@api_v1_bp.route("/found-items", methods=["GET"])
@api_login_required
def list_found_items():
    page, per_page = _parse_pagination()
    pagination = (
        FoundItem.query.order_by(FoundItem.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return jsonify({
        "data": [item.to_dict() for item in pagination.items],
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
    }), 200


@api_v1_bp.route("/found-items/<int:item_id>", methods=["GET"])
@api_login_required
def get_found_item(item_id):
    item = FoundItem.query.get(item_id)
    if item is None:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"data": item.to_dict()}), 200


@api_v1_bp.route("/found-items", methods=["POST"])
@api_login_required
def create_found_item():
    payload = request.get_json(silent=True) or {}
    fields = {}
    item_name = (payload.get("item_name") or "").strip()
    if not item_name:
        fields["item_name"] = "is required"
    date_found = _parse_date(payload.get("date_found"), "date_found", fields)
    if fields:
        return jsonify({"error": "validation_failed", "fields": fields}), 400
    item = FoundItem(
        finder_id=payload.get("finder_id"),
        logged_by=g.current_api_user.user_id,
        item_name=item_name,
        description=(payload.get("description") or "").strip() or None,
        category=(payload.get("category") or "").strip() or None,
        location_found=(payload.get("location_found") or "").strip() or None,
        date_found=date_found,
        photo_path=None,
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"data": item.to_dict()}), 201


@api_v1_bp.route("/found-items/<int:item_id>", methods=["PUT"])
@api_staff_required
def update_found_item(item_id):
    item = FoundItem.query.get(item_id)
    if item is None:
        return jsonify({"error": "not_found"}), 404
    payload = request.get_json(silent=True) or {}
    fields = {}
    if "item_name" in payload:
        name = (payload["item_name"] or "").strip()
        if not name:
            fields["item_name"] = "cannot be empty"
        else:
            item.item_name = name
    if "description" in payload:
        item.description = (payload["description"] or "").strip() or None
    if "category" in payload:
        item.category = (payload["category"] or "").strip() or None
    if "location_found" in payload:
        item.location_found = (payload["location_found"] or "").strip() or None
    if "date_found" in payload:
        parsed = _parse_date(payload["date_found"], "date_found", fields)
        if "date_found" not in fields:
            item.date_found = parsed
    if "status" in payload:
        if payload["status"] not in ("logged", "matched", "released"):
            fields["status"] = "must be one of: logged, matched, released"
        else:
            item.status = payload["status"]
    if fields:
        db.session.rollback()
        return jsonify({"error": "validation_failed", "fields": fields}), 400
    db.session.commit()
    return jsonify({"data": item.to_dict()}), 200


@api_v1_bp.route("/found-items/<int:item_id>", methods=["DELETE"])
@api_staff_required
def delete_found_item(item_id):
    item = FoundItem.query.get(item_id)
    if item is None:
        return jsonify({"error": "not_found"}), 404
    db.session.delete(item)
    db.session.commit()
    return ("", 204)
