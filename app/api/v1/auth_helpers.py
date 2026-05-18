"""Auth decorators for the /api/v1/* endpoints.

Resolution order on every request:
  1. Bearer token in Authorization header -> hash-compare against users.api_token_hash
  2. Flask-Login session cookie -> read current_user
  3. Reject with 401
"""

from functools import wraps

from flask import g, jsonify, request
from flask_login import current_user

from ...models import User


def _resolve_current_api_user():
    """Return the User identified by Bearer token or session, or None."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        raw_token = auth_header[len("Bearer "):].strip()
        if raw_token:
            users_with_tokens = User.query.filter(User.api_token_hash.isnot(None)).all()
            for u in users_with_tokens:
                if u.check_api_token(raw_token):
                    return u
    if current_user.is_authenticated:
        return current_user
    return None


def api_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = _resolve_current_api_user()
        if user is None:
            return jsonify({"error": "authentication_required"}), 401
        g.current_api_user = user
        return view(*args, **kwargs)
    return wrapped


def api_staff_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = _resolve_current_api_user()
        if user is None:
            return jsonify({"error": "authentication_required"}), 401
        if user.role not in ("staff", "admin"):
            return jsonify({"error": "forbidden"}), 403
        g.current_api_user = user
        return view(*args, **kwargs)
    return wrapped


def api_admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = _resolve_current_api_user()
        if user is None:
            return jsonify({"error": "authentication_required"}), 401
        if user.role != "admin":
            return jsonify({"error": "forbidden"}), 403
        g.current_api_user = user
        return view(*args, **kwargs)
    return wrapped
