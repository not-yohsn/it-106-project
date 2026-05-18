"""Match endpoints for /api/v1. Matches link a LostReport <-> FoundItem."""

from flask import g, jsonify, request

from ...extensions import db
from ...models import FoundItem, LostReport, Match
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


@api_v1_bp.route("/matches", methods=["GET"])
@api_login_required
def list_matches():
    page, per_page = _parse_pagination()
    pagination = (
        Match.query.order_by(Match.matched_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return jsonify({
        "data": [m.to_dict() for m in pagination.items],
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
    }), 200


@api_v1_bp.route("/matches/<int:match_id>", methods=["GET"])
@api_login_required
def get_match(match_id):
    match = Match.query.get(match_id)
    if match is None:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"data": match.to_dict()}), 200


@api_v1_bp.route("/matches", methods=["POST"])
@api_staff_required
def create_match():
    payload = request.get_json(silent=True) or {}
    fields = {}
    lost_id = payload.get("lost_report_id")
    found_id = payload.get("found_item_id")
    if not lost_id:
        fields["lost_report_id"] = "is required"
    if not found_id:
        fields["found_item_id"] = "is required"
    if fields:
        return jsonify({"error": "validation_failed", "fields": fields}), 400

    if LostReport.query.get(lost_id) is None:
        fields["lost_report_id"] = "no such lost report"
    if FoundItem.query.get(found_id) is None:
        fields["found_item_id"] = "no such found item"
    if Match.query.filter_by(lost_report_id=lost_id).first() is not None:
        fields["lost_report_id"] = "already matched to a found item"
    if Match.query.filter_by(found_item_id=found_id).first() is not None:
        fields["found_item_id"] = "already matched to a lost report"
    if fields:
        return jsonify({"error": "validation_failed", "fields": fields}), 400

    confidence = payload.get("confidence_score")
    try:
        confidence = float(confidence) if confidence is not None else None
    except (TypeError, ValueError):
        return jsonify({
            "error": "validation_failed",
            "fields": {"confidence_score": "must be a number"},
        }), 400

    match = Match(
        lost_report_id=lost_id,
        found_item_id=found_id,
        confidence_score=confidence,
    )
    db.session.add(match)
    # Flip statuses so the rest of the system reflects the match.
    LostReport.query.get(lost_id).status = "matched"
    FoundItem.query.get(found_id).status = "matched"
    db.session.commit()
    return jsonify({"data": match.to_dict()}), 201


@api_v1_bp.route("/matches/<int:match_id>", methods=["DELETE"])
@api_staff_required
def delete_match(match_id):
    match = Match.query.get(match_id)
    if match is None:
        return jsonify({"error": "not_found"}), 404
    # Roll the related items back to "reported"/"logged" on dissolution.
    if match.lost_report is not None:
        match.lost_report.status = "reported"
    if match.found_item is not None:
        match.found_item.status = "logged"
    db.session.delete(match)
    db.session.commit()
    return ("", 204)
