"""Lost-report endpoints for /api/v1. Implements the §6.1 privacy rule."""

from datetime import date

from flask import g, jsonify, request

from ...extensions import db
from ...models import LostReport
from . import api_v1_bp
from .auth_helpers import api_login_required


_LOST_PUBLIC_FIELDS = ("report_id", "item_name", "category", "photo_path", "created_at", "status")


def _serialize_lost_report_for(viewer, report):
    """Apply the §6.1 privacy rule: full payload to owner/staff, public-fields-only to others."""
    full = report.to_dict()
    if viewer.user_id == report.user_id or viewer.role in ("staff", "admin"):
        return full
    return {k: full[k] for k in _LOST_PUBLIC_FIELDS}


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


@api_v1_bp.route("/lost-reports", methods=["GET"])
@api_login_required
def list_lost_reports():
    page, per_page = _parse_pagination()
    query = LostReport.query.order_by(LostReport.created_at.desc())
    if request.args.get("mine") == "1":
        query = query.filter_by(user_id=g.current_api_user.user_id)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "data": [_serialize_lost_report_for(g.current_api_user, r) for r in pagination.items],
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
    }), 200


@api_v1_bp.route("/lost-reports/<int:report_id>", methods=["GET"])
@api_login_required
def get_lost_report(report_id):
    report = LostReport.query.get(report_id)
    if report is None:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"data": _serialize_lost_report_for(g.current_api_user, report)}), 200


@api_v1_bp.route("/lost-reports", methods=["POST"])
@api_login_required
def create_lost_report():
    payload = request.get_json(silent=True) or {}
    fields = {}
    item_name = (payload.get("item_name") or "").strip()
    if not item_name:
        fields["item_name"] = "is required"
    date_lost = _parse_date(payload.get("date_lost"), "date_lost", fields)
    if fields:
        return jsonify({"error": "validation_failed", "fields": fields}), 400
    report = LostReport(
        user_id=g.current_api_user.user_id,
        item_name=item_name,
        description=(payload.get("description") or "").strip() or None,
        category=(payload.get("category") or "").strip() or None,
        location=(payload.get("location") or "").strip() or None,
        date_lost=date_lost,
        photo_path=None,
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({"data": report.to_dict()}), 201


@api_v1_bp.route("/lost-reports/<int:report_id>", methods=["PUT"])
@api_login_required
def update_lost_report(report_id):
    report = LostReport.query.get(report_id)
    if report is None:
        return jsonify({"error": "not_found"}), 404
    if report.user_id != g.current_api_user.user_id and g.current_api_user.role not in ("staff", "admin"):
        return jsonify({"error": "forbidden"}), 403
    payload = request.get_json(silent=True) or {}
    fields = {}
    if "item_name" in payload:
        name = (payload["item_name"] or "").strip()
        if not name:
            fields["item_name"] = "cannot be empty"
        else:
            report.item_name = name
    if "description" in payload:
        report.description = (payload["description"] or "").strip() or None
    if "category" in payload:
        report.category = (payload["category"] or "").strip() or None
    if "location" in payload:
        report.location = (payload["location"] or "").strip() or None
    if "date_lost" in payload:
        parsed = _parse_date(payload["date_lost"], "date_lost", fields)
        if "date_lost" not in fields:
            report.date_lost = parsed
    if "status" in payload:
        if payload["status"] not in ("reported", "matched", "claimed", "closed"):
            fields["status"] = "must be one of: reported, matched, claimed, closed"
        else:
            report.status = payload["status"]
    if fields:
        db.session.rollback()
        return jsonify({"error": "validation_failed", "fields": fields}), 400
    db.session.commit()
    return jsonify({"data": report.to_dict()}), 200


@api_v1_bp.route("/lost-reports/<int:report_id>", methods=["DELETE"])
@api_login_required
def delete_lost_report(report_id):
    report = LostReport.query.get(report_id)
    if report is None:
        return jsonify({"error": "not_found"}), 404
    if report.user_id != g.current_api_user.user_id and g.current_api_user.role not in ("staff", "admin"):
        return jsonify({"error": "forbidden"}), 403
    db.session.delete(report)
    db.session.commit()
    return ("", 204)
