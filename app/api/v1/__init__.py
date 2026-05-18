from flask import Blueprint, jsonify, request

api_v1_bp = Blueprint("api_v1", __name__)


@api_v1_bp.app_errorhandler(404)
def _not_found(error):
    if request.path.startswith("/api/v1/"):
        return jsonify({"error": "not_found"}), 404
    return error


@api_v1_bp.app_errorhandler(405)
def _method_not_allowed(error):
    if request.path.startswith("/api/v1/"):
        return jsonify({"error": "method_not_allowed"}), 405
    return error


@api_v1_bp.app_errorhandler(500)
def _internal_error(error):
    if request.path.startswith("/api/v1/"):
        return jsonify({"error": "internal_server_error"}), 500
    return error


# Resource module imports — each module attaches its routes to api_v1_bp on import.
# auth_helpers is NOT imported here; it is imported by the individual resource modules.
from . import auth, users, lost_reports  # noqa: E402,F401
