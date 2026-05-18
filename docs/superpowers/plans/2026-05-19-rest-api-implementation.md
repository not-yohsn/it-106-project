# REST API Layer (M2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The implementer should also follow the `/vibecode` workflow: scan `engineering/` and `engineering-team/` (especially `senior-backend`, `code-reviewer`) for any patterns that apply, and cite the files consulted in the final report.

**Goal:** Build the `/api/v1/*` JSON blueprint required by PDF §V.3 — Bearer-token auth (with session-cookie fallback), `to_dict()` serialization on every model, ~24 CRUD endpoints across six resources, paginated lists, structured error envelopes.

**Architecture:** New `app/api/v1/` blueprint mounted at `/api/v1`. Resource-per-file layout (auth, users, lost_reports, found_items, matches, claims, notifications). Auth helpers centralize the dual Bearer/session check. Models gain `to_dict()` methods and User gains token-management helpers. One DB schema change: `users.api_token_hash` column. No new Python packages.

**Tech Stack:** Flask 3, Flask-Login, SQLAlchemy, Werkzeug (password hashing for both passwords and tokens), Python `secrets` module. MySQL 8 backend.

**Spec:** [docs/superpowers/specs/2026-05-19-rest-api-design.md](../specs/2026-05-19-rest-api-design.md)

---

## Verification approach

This project has no pytest setup and no existing tests. Per the spec, M3 is a separate milestone for Postman/Thunder Client testing.

For per-task verification, the implementer runs **one shell command**:

```
python -c "from app import create_app; app = create_app(); [print(rule) for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule) if rule.rule.startswith('/api/v1')]"
```

This lists every `/api/v1/*` route registered with Flask. The implementer compares the output against the task's expected route list. No live DB is required — `create_app()` configures the SQLAlchemy URI but doesn't connect until a query runs.

Task 14 (the final task) builds a manual-test cheatsheet of `curl` commands the user runs against a live `python run.py` server to confirm real end-to-end behavior.

---

## File map

```
Created:
  app/api/__init__.py
  app/api/v1/__init__.py
  app/api/v1/auth.py
  app/api/v1/auth_helpers.py
  app/api/v1/users.py
  app/api/v1/lost_reports.py
  app/api/v1/found_items.py
  app/api/v1/matches.py
  app/api/v1/claims.py
  app/api/v1/notifications.py
  docs/api-smoke-test.md

Modified:
  app/models.py          (add to_dict on all 7 models + token helpers on User)
  app/__init__.py        (register the new blueprint)
  database/schema.sql    (add api_token_hash column to users table)
```

---

## Task 1: Database schema change

**Files:**
- Modify: `database/schema.sql`

- [ ] **Step 1: Inspect the current `users` table definition in `database/schema.sql`**

Run: `grep -nE "CREATE TABLE.*users|api_token_hash" "database/schema.sql"`

Expected: one match line containing `CREATE TABLE` for the `users` table. Zero matches for `api_token_hash` (the column does not yet exist).

- [ ] **Step 2: Add the `api_token_hash` column to the `users` CREATE TABLE block in `database/schema.sql`**

Open `database/schema.sql`, find the `users` table's column list, and add a new column line immediately after the existing `password_hash` column declaration. The new line is:

```sql
  api_token_hash VARCHAR(255) NULL,
```

(Comma at the end — it is one of several columns, not the last one. Confirm placement: it should sit between `password_hash` and the next column / before any `PRIMARY KEY` clause.)

- [ ] **Step 3: Verify the column is present**

Run: `grep -nE "api_token_hash" "database/schema.sql"`

Expected: one match line — `  api_token_hash VARCHAR(255) NULL,` inside the `users` CREATE TABLE.

- [ ] **Step 4: Note the migration command for the live DB**

Add a comment immediately above the `users` CREATE TABLE block in `database/schema.sql` so anyone re-running the schema on an existing DB knows the upgrade path. Insert this comment line:

```sql
-- Note: existing databases must also run `ALTER TABLE users ADD COLUMN api_token_hash VARCHAR(255) NULL;` before the M2 API will function.
```

- [ ] **Step 5: Commit**

```
git add database/schema.sql
git commit -m "feat(db): add users.api_token_hash for M2 REST API auth tokens"
```

> **Note for the user:** After this task is done, run the `ALTER TABLE` statement once in phpMyAdmin against your local DB. This is the only manual step in M2.

---

## Task 2: Add `to_dict()` to every model + token helpers on User

**Files:**
- Modify: `app/models.py`

- [ ] **Step 1: Add the `api_token_hash` column declaration to the `User` class**

In `app/models.py`, find the `User` class. Inside the class body, after the `password_hash` column declaration line (`password_hash = db.Column(db.String(255), nullable=False)`), add:

```python
    api_token_hash = db.Column(db.String(255), nullable=True)
```

- [ ] **Step 2: Add three `User` API-token helpers**

Inside the `User` class, after the existing `check_password` method, add:

```python
    def set_api_token(self):
        """Generate, hash-store, and return a new raw token. Replaces any prior token."""
        import secrets
        raw_token = secrets.token_hex(32)
        self.api_token_hash = generate_password_hash(raw_token)
        return raw_token

    def clear_api_token(self):
        self.api_token_hash = None

    def check_api_token(self, raw_token):
        if not self.api_token_hash:
            return False
        return check_password_hash(self.api_token_hash, raw_token)
```

- [ ] **Step 3: Add `to_dict()` to the `User` class**

Inside the `User` class, after the three token helpers above, add:

```python
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
        }
```

(Note: `password_hash` and `api_token_hash` are deliberately omitted — these must never leak to API responses.)

- [ ] **Step 4: Add `to_dict()` to the `Finder` class**

Inside the `Finder` class, after the `found_items` relationship line, add:

```python
    def to_dict(self):
        return {
            "finder_id": self.finder_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
        }
```

- [ ] **Step 5: Add `to_dict()` to the `LostReport` class**

Inside the `LostReport` class, after the `match` relationship line, add:

```python
    def to_dict(self):
        return {
            "report_id": self.report_id,
            "user_id": self.user_id,
            "item_name": self.item_name,
            "description": self.description,
            "category": self.category,
            "location": self.location,
            "date_lost": self.date_lost.isoformat() if self.date_lost else None,
            "photo_path": self.photo_path,
            "status": self.status,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
        }
```

- [ ] **Step 6: Add `to_dict()` to the `FoundItem` class**

Inside the `FoundItem` class, after the `match` relationship line, add:

```python
    def to_dict(self):
        return {
            "item_id": self.item_id,
            "finder_id": self.finder_id,
            "logged_by": self.logged_by,
            "item_name": self.item_name,
            "description": self.description,
            "category": self.category,
            "location_found": self.location_found,
            "date_found": self.date_found.isoformat() if self.date_found else None,
            "photo_path": self.photo_path,
            "status": self.status,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
        }
```

- [ ] **Step 7: Add `to_dict()` to the `Match` class**

Inside the `Match` class, after the `claims` relationship line, add:

```python
    def to_dict(self):
        return {
            "match_id": self.match_id,
            "lost_report_id": self.lost_report_id,
            "found_item_id": self.found_item_id,
            "matched_at": self.matched_at.isoformat() + "Z" if self.matched_at else None,
            "confidence_score": self.confidence_score,
        }
```

- [ ] **Step 8: Add `to_dict()` to the `Claim` class**

Inside the `Claim` class, after the `verifier` relationship line, add:

```python
    def to_dict(self):
        return {
            "claim_id": self.claim_id,
            "match_id": self.match_id,
            "claimant_id": self.claimant_id,
            "verified_by": self.verified_by,
            "status": self.status,
            "notes": self.notes,
            "submitted_at": self.submitted_at.isoformat() + "Z" if self.submitted_at else None,
            "resolved_at": self.resolved_at.isoformat() + "Z" if self.resolved_at else None,
        }
```

- [ ] **Step 9: Add `to_dict()` to the `Notification` class**

Inside the `Notification` class, after the `user` relationship line, add:

```python
    def to_dict(self):
        return {
            "notification_id": self.notification_id,
            "user_id": self.user_id,
            "title": self.title,
            "body": self.body,
            "link": self.link,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
        }
```

- [ ] **Step 10: Verify the file parses and all 7 `to_dict` methods exist**

Run: `python -c "from app.models import User, Finder, LostReport, FoundItem, Match, Claim, Notification; print('OK', all(hasattr(cls, 'to_dict') for cls in [User, Finder, LostReport, FoundItem, Match, Claim, Notification]))"`

Expected output: `OK True`

Then: `python -c "from app.models import User; print(hasattr(User, 'set_api_token'), hasattr(User, 'clear_api_token'), hasattr(User, 'check_api_token'))"`

Expected output: `True True True`

- [ ] **Step 11: Commit**

```
git add app/models.py
git commit -m "feat(models): add to_dict() to all 7 models + User API-token helpers"
```

---

## Task 3: Create the API blueprint scaffold

**Files:**
- Create: `app/api/__init__.py`
- Create: `app/api/v1/__init__.py`

- [ ] **Step 1: Create the marker file `app/api/__init__.py`**

Write to `app/api/__init__.py`:

```python
```

(File is empty. It only exists to make `app.api` an importable package.)

- [ ] **Step 2: Create the v1 blueprint module `app/api/v1/__init__.py` with error handlers**

Write to `app/api/v1/__init__.py`:

```python
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


# Resource module imports go here once the modules exist (Tasks 7-13).
# auth_helpers is imported by individual resource modules, not registered here.
```

- [ ] **Step 3: Verify the blueprint imports cleanly**

Run: `python -c "from app.api.v1 import api_v1_bp; print(api_v1_bp.name)"`

Expected output: `api_v1`

- [ ] **Step 4: Commit**

```
git add app/api/__init__.py app/api/v1/__init__.py
git commit -m "feat(api): scaffold /api/v1 blueprint with JSON error handlers"
```

---

## Task 4: Register the API blueprint in the app factory

**Files:**
- Modify: `app/__init__.py`

- [ ] **Step 1: Add the API blueprint registration**

In `app/__init__.py`, find the existing block of `app.register_blueprint(...)` calls (lines 28-35 currently). Immediately after the last one (`app.register_blueprint(admin_bp, url_prefix="/admin")`), add:

```python
    from .api.v1 import api_v1_bp
    app.register_blueprint(api_v1_bp, url_prefix="/api/v1")
```

(Indentation: 4 spaces — these lines sit inside `create_app()`.)

- [ ] **Step 2: Verify the app boots and the blueprint is registered**

Run: `python -c "from app import create_app; app = create_app(); print([bp for bp in app.blueprints])"`

Expected output includes `'api_v1'`. Full list will be:
`['auth', 'main', 'reports', 'found', 'matches', 'claims', 'notifications', 'admin', 'api_v1']`

- [ ] **Step 3: Verify the blueprint has no routes yet (only error handlers)**

Run: `python -c "from app import create_app; app = create_app(); print([str(r) for r in app.url_map.iter_rules() if str(r).startswith('/api/v1')])"`

Expected output: `[]` (empty list — no routes are attached yet; that's Tasks 7-13).

- [ ] **Step 4: Commit**

```
git add app/__init__.py
git commit -m "feat(api): register /api/v1 blueprint with the Flask app factory"
```

---

## Task 5: Auth helpers (decorators)

**Files:**
- Create: `app/api/v1/auth_helpers.py`

- [ ] **Step 1: Create the auth-helpers module**

Write to `app/api/v1/auth_helpers.py`:

```python
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
```

- [ ] **Step 2: Verify the module imports cleanly**

Run: `python -c "from app.api.v1.auth_helpers import api_login_required, api_staff_required, api_admin_required; print('OK')"`

Expected output: `OK`

- [ ] **Step 3: Commit**

```
git add app/api/v1/auth_helpers.py
git commit -m "feat(api): add Bearer+session auth decorators for /api/v1/*"
```

---

## Task 6: Auth endpoints — login / logout

**Files:**
- Create: `app/api/v1/auth.py`
- Modify: `app/api/v1/__init__.py` (uncomment / add the auth import)

- [ ] **Step 1: Create `app/api/v1/auth.py`**

Write to `app/api/v1/auth.py`:

```python
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
```

- [ ] **Step 2: Wire `auth.py` into the blueprint init**

Edit `app/api/v1/__init__.py`. Find the comment that says:
```python
# Resource module imports go here once the modules exist (Tasks 7-13).
# auth_helpers is imported by individual resource modules, not registered here.
```

Replace it with:
```python
# Resource module imports — each module attaches its routes to api_v1_bp on import.
# auth_helpers is NOT imported here; it is imported by the individual resource modules.
from . import auth  # noqa: E402,F401
```

- [ ] **Step 3: Verify routes are registered**

Run: `python -c "from app import create_app; app = create_app(); [print(str(r), '->', list(r.methods - {'HEAD', 'OPTIONS'})) for r in sorted(app.url_map.iter_rules(), key=lambda r: r.rule) if str(r).startswith('/api/v1')]"`

Expected output (two routes — order may vary):
```
/api/v1/auth/login -> ['POST']
/api/v1/auth/logout -> ['POST']
```

- [ ] **Step 4: Commit**

```
git add app/api/v1/auth.py app/api/v1/__init__.py
git commit -m "feat(api): add POST /api/v1/auth/login and POST /api/v1/auth/logout"
```

---

## Task 7: Users + /me endpoints

**Files:**
- Create: `app/api/v1/users.py`
- Modify: `app/api/v1/__init__.py` (add `users` import)

- [ ] **Step 1: Create `app/api/v1/users.py`**

Write to `app/api/v1/users.py`:

```python
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
```

- [ ] **Step 2: Wire `users.py` into the blueprint init**

Edit `app/api/v1/__init__.py`. Append `, users` to the import line so it reads:

```python
from . import auth, users  # noqa: E402,F401
```

- [ ] **Step 3: Verify routes**

Run the same `url_map` listing command as Task 6 Step 3.

Expected routes for `/api/v1/*`:
```
/api/v1/auth/login -> ['POST']
/api/v1/auth/logout -> ['POST']
/api/v1/me -> ['GET']
/api/v1/users -> ['GET']
/api/v1/users/<int:user_id> -> ['DELETE', 'GET', 'PUT']
```

- [ ] **Step 4: Commit**

```
git add app/api/v1/users.py app/api/v1/__init__.py
git commit -m "feat(api): add user CRUD + /me endpoints"
```

---

## Task 8: Lost-reports endpoints (with privacy filter)

**Files:**
- Create: `app/api/v1/lost_reports.py`
- Modify: `app/api/v1/__init__.py` (add `lost_reports` import)

- [ ] **Step 1: Create `app/api/v1/lost_reports.py`**

Write to `app/api/v1/lost_reports.py`:

```python
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
```

- [ ] **Step 2: Wire into blueprint init**

Edit `app/api/v1/__init__.py`. Update the import line to:

```python
from . import auth, users, lost_reports  # noqa: E402,F401
```

- [ ] **Step 3: Verify routes**

Run the `url_map` listing command. Expected `/api/v1/*` routes now include:
```
/api/v1/lost-reports -> ['GET', 'POST']
/api/v1/lost-reports/<int:report_id> -> ['DELETE', 'GET', 'PUT']
```

(Plus the previously added auth + users routes.)

- [ ] **Step 4: Commit**

```
git add app/api/v1/lost_reports.py app/api/v1/__init__.py
git commit -m "feat(api): add lost-reports CRUD with privacy filter"
```

---

## Task 9: Found-items endpoints

**Files:**
- Create: `app/api/v1/found_items.py`
- Modify: `app/api/v1/__init__.py` (add `found_items` import)

- [ ] **Step 1: Create `app/api/v1/found_items.py`**

Write to `app/api/v1/found_items.py`:

```python
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
```

- [ ] **Step 2: Wire into blueprint init**

Edit `app/api/v1/__init__.py`. Update the import line to:

```python
from . import auth, users, lost_reports, found_items  # noqa: E402,F401
```

- [ ] **Step 3: Verify routes**

Run the `url_map` listing command. New `/api/v1/*` routes include:
```
/api/v1/found-items -> ['GET', 'POST']
/api/v1/found-items/<int:item_id> -> ['DELETE', 'GET', 'PUT']
```

- [ ] **Step 4: Commit**

```
git add app/api/v1/found_items.py app/api/v1/__init__.py
git commit -m "feat(api): add found-items CRUD (POST any user; PUT/DELETE staff-only)"
```

---

## Task 10: Matches endpoints

**Files:**
- Create: `app/api/v1/matches.py`
- Modify: `app/api/v1/__init__.py` (add `matches` import)

- [ ] **Step 1: Create `app/api/v1/matches.py`**

Write to `app/api/v1/matches.py`:

```python
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
```

- [ ] **Step 2: Wire into blueprint init**

Edit `app/api/v1/__init__.py`. Update the import line to:

```python
from . import auth, users, lost_reports, found_items, matches  # noqa: E402,F401
```

- [ ] **Step 3: Verify routes**

Run the `url_map` listing command. New routes:
```
/api/v1/matches -> ['GET', 'POST']
/api/v1/matches/<int:match_id> -> ['DELETE', 'GET']
```

- [ ] **Step 4: Commit**

```
git add app/api/v1/matches.py app/api/v1/__init__.py
git commit -m "feat(api): add matches endpoints (POST/DELETE staff-only; GET any user)"
```

---

## Task 11: Claims endpoints (with status transitions)

**Files:**
- Create: `app/api/v1/claims.py`
- Modify: `app/api/v1/__init__.py` (add `claims` import)

- [ ] **Step 1: Create `app/api/v1/claims.py`**

Write to `app/api/v1/claims.py`:

```python
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
```

- [ ] **Step 2: Wire into blueprint init**

Edit `app/api/v1/__init__.py`. Update the import line to:

```python
from . import auth, users, lost_reports, found_items, matches, claims  # noqa: E402,F401
```

- [ ] **Step 3: Verify routes**

Run the `url_map` listing command. New routes:
```
/api/v1/claims -> ['GET', 'POST']
/api/v1/claims/<int:claim_id> -> ['DELETE', 'GET', 'PUT']
```

- [ ] **Step 4: Commit**

```
git add app/api/v1/claims.py app/api/v1/__init__.py
git commit -m "feat(api): add claims CRUD with status-transition rules"
```

---

## Task 12: Notifications endpoints

**Files:**
- Create: `app/api/v1/notifications.py`
- Modify: `app/api/v1/__init__.py` (add `notifications` import)

- [ ] **Step 1: Create `app/api/v1/notifications.py`**

Write to `app/api/v1/notifications.py`:

```python
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
```

- [ ] **Step 2: Wire into blueprint init**

Edit `app/api/v1/__init__.py`. Update the import line to:

```python
from . import auth, users, lost_reports, found_items, matches, claims, notifications  # noqa: E402,F401
```

- [ ] **Step 3: Verify all routes**

Run: `python -c "from app import create_app; app = create_app(); [print(str(r), '->', sorted(r.methods - {'HEAD', 'OPTIONS'})) for r in sorted(app.url_map.iter_rules(), key=lambda r: r.rule) if str(r).startswith('/api/v1')]"`

Expected full route list (order matches alphabetical-by-rule):
```
/api/v1/auth/login -> ['POST']
/api/v1/auth/logout -> ['POST']
/api/v1/claims -> ['GET', 'POST']
/api/v1/claims/<int:claim_id> -> ['DELETE', 'GET', 'PUT']
/api/v1/found-items -> ['GET', 'POST']
/api/v1/found-items/<int:item_id> -> ['DELETE', 'GET', 'PUT']
/api/v1/lost-reports -> ['GET', 'POST']
/api/v1/lost-reports/<int:report_id> -> ['DELETE', 'GET', 'PUT']
/api/v1/matches -> ['GET', 'POST']
/api/v1/matches/<int:match_id> -> ['DELETE', 'GET']
/api/v1/me -> ['GET']
/api/v1/notifications -> ['GET']
/api/v1/notifications/<int:notification_id> -> ['DELETE', 'GET', 'PUT']
/api/v1/users -> ['GET']
/api/v1/users/<int:user_id> -> ['DELETE', 'GET', 'PUT']
```

(15 unique rule paths, ~28 method/route pairs.)

- [ ] **Step 4: Commit**

```
git add app/api/v1/notifications.py app/api/v1/__init__.py
git commit -m "feat(api): add notifications endpoints (owner-only, mark-read via PUT)"
```

---

## Task 13: Smoke-test cheatsheet for the user

**Files:**
- Create: `docs/api-smoke-test.md`

- [ ] **Step 1: Create `docs/api-smoke-test.md` — a curl-driven walkthrough**

Write to `docs/api-smoke-test.md`:

````markdown
# /api/v1 smoke test cheatsheet

Use these `curl` commands to confirm the API is wired up correctly after running
the one-time `ALTER TABLE` migration from Task 1:

```sql
ALTER TABLE users ADD COLUMN api_token_hash VARCHAR(255) NULL;
```

> Make sure `python run.py` is running in another terminal so the API is reachable at
> `http://127.0.0.1:8000`. Substitute a real admin email/password from your local DB
> for `admin@example.com` / `Pa55word!` below.

## 1. Log in and capture the Bearer token

```powershell
$resp = Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/auth/login `
  -Method POST -ContentType "application/json" `
  -Body '{"email": "admin@example.com", "password": "Pa55word!"}'
$token = $resp.token
$token
```

Expected: a 64-character hex string is printed.

## 2. Confirm /me returns the logged-in admin

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/me `
  -Headers @{ Authorization = "Bearer $token" }
```

Expected: `data` field contains `name`, `email`, `role: admin`, etc. No `password_hash` or `api_token_hash` keys.

## 3. List users (admin only)

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/users `
  -Headers @{ Authorization = "Bearer $token" }
```

Expected: a `{data, page, per_page, total}` shape; `data` is a list of user dicts (no password/token hashes).

## 4. Create a lost report

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/lost-reports `
  -Method POST -ContentType "application/json" `
  -Headers @{ Authorization = "Bearer $token" } `
  -Body '{"item_name": "Black Backpack", "category": "bag", "location": "Library 2F", "date_lost": "2026-05-18"}'
```

Expected: HTTP 201, `data` payload includes a `report_id` and `status: "reported"`.

## 5. Read it back

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/lost-reports `
  -Headers @{ Authorization = "Bearer $token" }
```

Expected: the report created in step 4 appears in the `data` array.

## 6. Hit an unknown route — verify JSON 404

```powershell
try {
  Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/no-such-thing `
    -Headers @{ Authorization = "Bearer $token" }
} catch {
  $_.Exception.Response.GetResponseStream() | %{ (New-Object IO.StreamReader $_).ReadToEnd() }
}
```

Expected: the response body is `{"error": "not_found"}` (JSON, not the HTML 404 page).

## 7. Log out

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/auth/logout `
  -Method POST -Headers @{ Authorization = "Bearer $token" }
```

Expected: HTTP 204, empty body. Subsequent requests with the same `$token` now return `401 {"error": "authentication_required"}`.

---

These seven steps cover the auth lifecycle, a happy-path resource create+read, error JSON, and token revocation. They are the basis for the Milestone M3 Postman/Thunder Client collection.
````

- [ ] **Step 2: Confirm the file rendered correctly**

Run: `grep -nE "^## " "docs/api-smoke-test.md"`

Expected: seven headings, one per smoke-test step.

- [ ] **Step 3: Commit**

```
git add docs/api-smoke-test.md
git commit -m "docs(api): add smoke-test cheatsheet for the new /api/v1 endpoints"
```

---

## Task 14: Final verification + URL-map snapshot

**Files:**
- Inspect-only

- [ ] **Step 1: Confirm the full URL map**

Run the same `url_map` listing command from Task 12 Step 3. Confirm 15 rule paths, all `/api/v1/*`, in the order shown there. No extra routes, no missing routes.

- [ ] **Step 2: Confirm all the expected files exist**

Run: `ls "app/api/v1/"`

Expected output (one per line, in any order):
```
__init__.py
auth.py
auth_helpers.py
claims.py
found_items.py
lost_reports.py
matches.py
notifications.py
users.py
```

Run: `ls "app/api/"`

Expected:
```
__init__.py
v1
```

- [ ] **Step 3: Confirm git log shows the expected commits**

Run: `git log --oneline -15`

Expected: 13 new commits on top of whatever existed before this plan (one per Task 1–13). The subject lines should follow the `feat(api):`, `feat(db):`, `feat(models):`, and `docs(api):` pattern.

- [ ] **Step 4: Confirm no untracked Python files were forgotten**

Run: `git status`

Expected: no `app/api/*.py` paths appear under "Untracked files" — every new file from the plan should now be tracked. The pre-existing untracked files (e.g., `requirements.txt`, the PDF) are not part of this plan and can remain untracked.

- [ ] **Step 5: No additional commit — Task 14 is verification only**

If all four checks above pass, M2 is structurally complete. The user can now run the `ALTER TABLE users ADD COLUMN api_token_hash VARCHAR(255) NULL;` migration and then walk through `docs/api-smoke-test.md` to verify the endpoints end-to-end against their local MySQL.

---

## Acceptance criteria recap (from spec §11)

After this plan executes, the following must all be true:

1. ✅ `app/api/v1/` exists and contains the eight files listed in spec §4. — *Tasks 3, 5, 6, 7, 8, 9, 10, 11, 12.*
2. ✅ `users.api_token_hash` column exists (in `database/schema.sql`). User runs the `ALTER TABLE` once against their live DB. — *Task 1.*
3. ✅ Every endpoint in spec §6 is registered with Flask and returns the spec'd shape. — *Tasks 6–12; verified via url_map.*
4. ✅ `POST /api/v1/auth/login` issues a token; Bearer auth succeeds afterwards. — *Tasks 5, 6, 13.*
5. ✅ Invalid login returns `401 {"error": "invalid_credentials"}`. — *Task 6.*
6. ✅ Session cookie fallback works (test by hitting `/api/v1/me` from a browser logged into the HTML app). — *Task 5; verified via §13 smoke test.*
7. ✅ JSON envelopes match spec §8. — *Every resource task.*
8. ✅ `to_dict()` never leaks `password_hash` or `api_token_hash`. — *Task 2 (User.to_dict deliberately omits both).*
9. ✅ Unknown `/api/v1/*` routes return JSON 404. — *Task 3 (error handlers).*
10. ✅ Existing HTML routes still work (the new blueprint adds; it doesn't modify others). — *Verified by Task 14 Step 1's url_map showing all pre-existing routes still registered.*
