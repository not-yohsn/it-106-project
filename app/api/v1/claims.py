"""Claim endpoints for /api/v1. Implements the §6.2 status-transition rules."""

from datetime import datetime

from flask import g, jsonify, request

from ...extensions import db
from ...models import Claim, Match
from . import api_v1_bp
from .auth_helpers import api_login_required, api_staff_required


_ALLOWED_TRANSITIONS = {
    "pending": {"approved", "rejected"},
    "approved": {"released"},
    "rejected": set(),
    "released": set(),
}


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


@api_v1_bp.route("/claims", methods=["GET"])
@api_login_required
def list_claims():
    page, per_page = _parse_pagination()
    query = Claim.query.order_by(Claim.submitted_at.desc())
    if g.current_api_user.role not in ("staff", "admin"):
        query = query.filter_by(claimant_id=g.current_api_user.user_id)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "data": [c.to_dict() for c in pagination.items],
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
    }), 200


@api_v1_bp.route("/claims/<int:claim_id>", methods=["GET"])
@api_login_required
def get_claim(claim_id):
    claim = Claim.query.get(claim_id)
    if claim is None:
        return jsonify({"error": "not_found"}), 404
    if claim.claimant_id != g.current_api_user.user_id and g.current_api_user.role not in ("staff", "admin"):
        return jsonify({"error": "forbidden"}), 403
    return jsonify({"data": claim.to_dict()}), 200


@api_v1_bp.route("/claims", methods=["POST"])
@api_login_required
def create_claim():
    payload = request.get_json(silent=True) or {}
    fields = {}
    match_id = payload.get("match_id")
    if not match_id:
        fields["match_id"] = "is required"
    if fields:
        return jsonify({"error": "validation_failed", "fields": fields}), 400
    if Match.query.get(match_id) is None:
        return jsonify({
            "error": "validation_failed",
            "fields": {"match_id": "no such match"},
        }), 400
    claim = Claim(
        match_id=match_id,
        claimant_id=g.current_api_user.user_id,
        notes=(payload.get("notes") or "").strip() or None,
        status="pending",
    )
    db.session.add(claim)
    db.session.commit()
    return jsonify({"data": claim.to_dict()}), 201


@api_v1_bp.route("/claims/<int:claim_id>", methods=["PUT"])
@api_staff_required
def update_claim(claim_id):
    claim = Claim.query.get(claim_id)
    if claim is None:
        return jsonify({"error": "not_found"}), 404
    payload = request.get_json(silent=True) or {}

    if "notes" in payload:
        claim.notes = (payload["notes"] or "").strip() or None

    if "status" in payload:
        new_status = payload["status"]
        if new_status not in ("pending", "approved", "rejected", "released"):
            db.session.rollback()
            return jsonify({
                "error": "validation_failed",
                "fields": {"status": "must be one of: pending, approved, rejected, released"},
            }), 400
        if new_status != claim.status:
            if new_status not in _ALLOWED_TRANSITIONS[claim.status]:
                db.session.rollback()
                return jsonify({
                    "error": "invalid_transition",
                    "fields": {"status": f"cannot move from {claim.status} to {new_status}"},
                }), 400
            claim.status = new_status
            if new_status in ("approved", "released"):
                claim.verified_by = g.current_api_user.user_id
            if new_status in ("approved", "rejected", "released"):
                claim.resolved_at = datetime.utcnow()

    db.session.commit()
    return jsonify({"data": claim.to_dict()}), 200


@api_v1_bp.route("/claims/<int:claim_id>", methods=["DELETE"])
@api_staff_required
def delete_claim(claim_id):
    claim = Claim.query.get(claim_id)
    if claim is None:
        return jsonify({"error": "not_found"}), 404
    db.session.delete(claim)
    db.session.commit()
    return ("", 204)
