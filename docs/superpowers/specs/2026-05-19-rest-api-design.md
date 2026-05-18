# REST API Layer (M2) — Design Spec

**Date:** 2026-05-19
**Milestone:** M2 — REST API layer (PDF §V.3 hard requirement; 15 rubric points for "Backend & API Integration")
**Goal:** Add `/api/v1/*` JSON endpoints to the Lost and Found Management System so the project satisfies the PDF requirements for REST API endpoints, JSON data exchange, and clean Postman/Thunder Client demos.

---

## 1. Why this milestone

The PDF §V.3 mandates GET/POST/PUT/DELETE endpoints returning JSON. The existing system is server-rendered HTML only — no JSON surface exists. M2 closes this gap with a single new blueprint mounted at `/api/v1`, exposing every core domain resource (users, lost reports, found items, matches, claims, notifications) over JSON.

The PDF §VIII.8 also requires Postman/Thunder Client screenshots in the submission, which means the auth flow must be demoable in those tools — hence **Bearer-token auth** with a **session-cookie fallback** for the browser-side `fetch()` calls.

## 2. Scope

**In scope (v1):**
- New blueprint `app/api/v1/` mounted at `/api/v1`
- Bearer-token auth (`POST /api/v1/auth/login` → token; `POST /api/v1/auth/logout` → revoke), with a session-cookie fallback that reuses Flask-Login
- One new DB column: `users.api_token_hash VARCHAR(255) NULL`
- ~24 JSON endpoints across 6 resources (users, lost-reports, found-items, matches, claims, notifications) with pagination on list endpoints
- `to_dict()` methods added to each of the 7 SQLAlchemy models
- Standard JSON response/error envelope (`{"data": ...}`, `{"error": "...", "fields": {...}}`)
- Blueprint-scoped JSON error handlers (404/405/500 inside `/api/v1/*` return JSON, not HTML)

**Out of scope (v1):**
- Photo upload via API (uploads continue through the existing HTML forms; the API exposes `photo_path` as a read-only string)
- Token expiry, refresh tokens, OAuth, multiple-tokens-per-user (single token column suffices)
- Public/unauthenticated browsing endpoints (every endpoint requires auth)
- API rate limiting
- API versioning beyond `v1` (the `v1` prefix is intentionally future-proof; no `v2` planned)
- OpenAPI/Swagger auto-generation (manual docs sufficient for M3)
- Database migrations framework (Alembic) — schema change applied via a one-line `ALTER TABLE`

## 3. Tech and dependencies

**No new Python packages.** Everything is built on Flask 3, Flask-Login, SQLAlchemy, and Werkzeug — all already in `requirements.txt`.

**One schema change** (applied to both `database/schema.sql` and existing DBs via a one-line `ALTER TABLE`):

```sql
ALTER TABLE users ADD COLUMN api_token_hash VARCHAR(255) NULL;
```

## 4. File organization

```
app/api/
├── __init__.py          # (empty marker)
└── v1/
    ├── __init__.py      # Blueprint definition + JSON 404/405/500 error handlers + module imports
    ├── auth.py          # POST /auth/login, POST /auth/logout
    ├── auth_helpers.py  # @api_login_required, @api_staff_required, @api_admin_required
    ├── users.py         # GET /users, GET /users/:id, GET /me, PUT /users/:id, DELETE /users/:id
    ├── lost_reports.py  # full CRUD on /lost-reports
    ├── found_items.py   # full CRUD on /found-items
    ├── matches.py       # GET list/detail, POST, DELETE on /matches
    ├── claims.py        # full CRUD on /claims
    └── notifications.py # GET list/detail, PUT mark-read, DELETE on /notifications
```

Each resource file owns its endpoints (`~80–150 lines`). All routes are decorated with `@api_login_required` (plus stacked role decorators where needed). `auth_helpers.py` is the single place that knows how to identify the current API caller.

**Models stay in `app/models.py`** — each of the 7 model classes gains a `to_dict()` method (and `User` additionally gains `set_api_token()`, `clear_api_token()`, and `check_api_token(raw_token)` methods). No new file for serializers.

## 5. Auth flow

### 5.1 The new DB column

```sql
ALTER TABLE users ADD COLUMN api_token_hash VARCHAR(255) NULL;
```

- `NULL` means the user currently has no active API token.
- The column stores a Werkzeug-hashed token (`generate_password_hash`), never the raw token.

### 5.2 `POST /api/v1/auth/login`

**Request:**
```json
{"email": "alice@example.com", "password": "secret"}
```

**Success (200):**
```json
{
  "token": "9f3a2b4c8d7e1f5a9b3c2d4e8f1a5b9c3d7e2f8a4b6c1d5e9f3a7b2c8d4e6f1a",
  "user": {"user_id": 1, "name": "Alice", "email": "alice@example.com", "role": "student"}
}
```

**Process:**
1. Validate email + password against `users` (using existing `check_password`).
2. Generate a 64-character random hex token (`secrets.token_hex(32)`).
3. Store `generate_password_hash(token)` in `users.api_token_hash`. Commit.
4. Return the **raw** token + the user payload.

**Failure:** `401 {"error": "invalid_credentials"}` (no hint about which field was wrong).

### 5.3 `POST /api/v1/auth/logout`

Requires auth (Bearer or session). Sets `users.api_token_hash = NULL` on the caller's row. Returns `204 No Content`.

### 5.4 `@api_login_required` decorator

```python
from functools import wraps
from flask import g, jsonify, request
from flask_login import current_user
from ...models import User

def api_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        # 1. Try Bearer token
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            raw_token = auth[len("Bearer "):].strip()
            users_with_tokens = User.query.filter(User.api_token_hash.isnot(None)).all()
            for u in users_with_tokens:
                if u.check_api_token(raw_token):
                    g.current_api_user = u
                    return view(*args, **kwargs)
        # 2. Try Flask-Login session
        if current_user.is_authenticated:
            g.current_api_user = current_user
            return view(*args, **kwargs)
        # 3. Reject
        return jsonify({"error": "authentication required"}), 401
    return wrapped
```

(The linear scan over users-with-tokens is fine at student-project scale. If needed later, a token-prefix-indexed column can replace the scan.)

### 5.5 `@api_staff_required` and `@api_admin_required`

Stacked on top of `@api_login_required`. Read `g.current_api_user.role`. Return `403 {"error": "forbidden"}` if the role is insufficient.

## 6. Endpoint surface (~24 endpoints)

| # | Method | Path | Auth | Notes |
|---|--------|------|------|-------|
| 1 | POST | `/api/v1/auth/login` | public | returns token + user |
| 2 | POST | `/api/v1/auth/logout` | any user | clears token |
| 3 | GET | `/api/v1/users` | admin | paginated list |
| 4 | GET | `/api/v1/users/:id` | admin OR self | |
| 5 | GET | `/api/v1/me` | any user | shortcut for "current user" |
| 6 | PUT | `/api/v1/users/:id` | admin | edit role/name/email/phone |
| 7 | DELETE | `/api/v1/users/:id` | admin | cannot delete self |
| 8 | GET | `/api/v1/lost-reports` | any user | paginated; `?mine=1` filter |
| 9 | GET | `/api/v1/lost-reports/:id` | any user — see §6.1 privacy rule | |
| 10 | POST | `/api/v1/lost-reports` | any user | creates own report |
| 11 | PUT | `/api/v1/lost-reports/:id` | owner OR staff | |
| 12 | DELETE | `/api/v1/lost-reports/:id` | owner OR staff | |
| 13 | GET | `/api/v1/found-items` | any user | paginated |
| 14 | GET | `/api/v1/found-items/:id` | any user | |
| 15 | POST | `/api/v1/found-items` | any user (student logs own; staff logs anything) | |
| 16 | PUT | `/api/v1/found-items/:id` | staff | |
| 17 | DELETE | `/api/v1/found-items/:id` | staff | |
| 18 | GET | `/api/v1/matches` | any user | paginated |
| 19 | GET | `/api/v1/matches/:id` | any user | |
| 20 | POST | `/api/v1/matches` | staff | body has lost_report_id + found_item_id |
| 21 | DELETE | `/api/v1/matches/:id` | staff | dissolves the match |
| 22 | GET | `/api/v1/claims` | claimant (own only) OR staff (all) | paginated |
| 23 | GET | `/api/v1/claims/:id` | claimant OR staff | |
| 24 | POST | `/api/v1/claims` | any user | body has match_id |
| 25 | PUT | `/api/v1/claims/:id` | staff | change status (approve/reject/release) |
| 26 | DELETE | `/api/v1/claims/:id` | staff | |
| 27 | GET | `/api/v1/notifications` | owner only | own notifications, paginated |
| 28 | GET | `/api/v1/notifications/:id` | owner only | |
| 29 | PUT | `/api/v1/notifications/:id` | owner only | `{"is_read": true}` |
| 30 | DELETE | `/api/v1/notifications/:id` | owner only | |

(30 numbered rows because I split out `/me` and listed both auth endpoints individually. ~24 distinct CRUD endpoints if you exclude `/auth/*` and `/me`.)

URL casing: **kebab-case** for multi-word paths (`/lost-reports`, `/found-items`). Single-word resources stay simple (`/users`, `/matches`, `/claims`, `/notifications`).

### 6.1 Lost-report privacy rule

The existing HTML route shows only public fields to non-owners (per README §3 "Privacy"). The API mirrors this behavior:

- **Owner of the report OR staff/admin** → `to_dict()` returns the full payload (every field in §9.2 LostReport).
- **Any other authenticated user** → response includes only `report_id`, `item_name`, `category`, `photo_path`, `created_at`, `status`. Sensitive fields (`description`, `location`, `date_lost`, `user_id`) are omitted from the JSON.

This filter lives inside `lost_reports.py`'s detail and list handlers — not on the model — so the model's `to_dict()` stays a pure full-representation method and the privacy filter is a thin wrapper in the route.

### 6.2 Claim status transitions

`PUT /api/v1/claims/:id` accepts `{"status": "<new>"}` and `{"notes": "..."}`. Status transitions are validated server-side; invalid transitions return `400 {"error": "invalid_transition", "fields": {"status": "cannot move from X to Y"}}`.

Allowed transitions:
- `pending → approved` (staff approves the claim)
- `pending → rejected` (staff rejects the claim)
- `approved → released` (staff marks the item physically released)
- Terminal states: `rejected` and `released` cannot transition further

On transition to `approved` or `released`, the route additionally sets `verified_by = g.current_api_user.user_id` and `resolved_at = now()`. On transition to `rejected`, it sets `resolved_at = now()` but leaves `verified_by` per the same rule.

## 7. Pagination

Every `GET` list endpoint accepts:
- `?page=<int>` (default 1, min 1)
- `?per_page=<int>` (default 20, min 1, max 100)

Invalid values fall back to defaults (no 400). Out-of-range pages return an empty `data` array (not a 404).

**List response shape:**
```json
{
  "data": [{...}, {...}],
  "page": 1,
  "per_page": 20,
  "total": 47
}
```

## 8. JSON response and error envelopes

### 8.1 Successful single-resource read
```json
{"data": {"report_id": 7, "item_name": "Backpack", "category": "bag", "status": "reported", "user": {...}, "created_at": "2026-05-19T10:23:00Z"}}
```

### 8.2 Successful create (`201 Created`)
Same shape as a successful single-resource read. Always returns the newly created resource so the client can read back the server-assigned ID and timestamps.

### 8.3 Successful update
Same shape as a successful single-resource read. Returns the post-update state.

### 8.4 Successful delete or revoke
HTTP `204 No Content`, empty body.

### 8.5 Validation error (`400 Bad Request`)
```json
{"error": "validation_failed", "fields": {"item_name": "is required", "date_lost": "must be YYYY-MM-DD"}}
```

### 8.6 Auth/permission/not-found errors
```json
{"error": "authentication_required"}   // 401
{"error": "invalid_credentials"}        // 401, only on /auth/login
{"error": "forbidden"}                  // 403
{"error": "not_found"}                  // 404
{"error": "method_not_allowed"}         // 405
```

### 8.7 Unexpected server error (`500`)
```json
{"error": "internal_server_error"}
```
Underlying exception logged server-side; details NOT exposed to client.

### 8.8 Blueprint-scoped error handlers

Registered on `api_v1_bp` so HTML 404/405/500 pages don't leak into the API:

```python
@api_v1_bp.app_errorhandler(404)
def _404(e):
    if request.path.startswith("/api/v1/"):
        return jsonify({"error": "not_found"}), 404
    return e  # fall through to default HTML handler

@api_v1_bp.app_errorhandler(405)
def _405(e):
    if request.path.startswith("/api/v1/"):
        return jsonify({"error": "method_not_allowed"}), 405
    return e
```

(Using `app_errorhandler` because Flask only fires blueprint-level error handlers for routes already matched to a blueprint; a request to `/api/v1/nonexistent` doesn't match any blueprint route and would otherwise fall through to the global HTML 404 page.)

## 9. `to_dict()` conventions

Each of the 7 models in `app/models.py` gains a `to_dict()` method. Sensitive fields (`password_hash`, `api_token_hash`) are **never** in any output.

### 9.1 User
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

### 9.2 LostReport
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

### 9.3 FoundItem, Match, Claim, Notification, Finder
Same pattern: every column field, ISO-formatted dates and datetimes, no sensitive data, no nested relationships by default. Relationships (e.g. `LostReport.user`) are NOT auto-expanded — if a caller wants the related user they call `/api/v1/users/:id` separately. (Keeps the response shape predictable and prevents accidental N+1 expansion.)

### 9.4 User API-token helpers
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

## 10. Blueprint wiring

In `app/__init__.py:create_app()`, after the existing blueprint registrations:

```python
from .api.v1 import api_v1_bp
app.register_blueprint(api_v1_bp, url_prefix="/api/v1")
```

In `app/api/v1/__init__.py`:

```python
from flask import Blueprint, jsonify, request

api_v1_bp = Blueprint("api_v1", __name__)

# Importing each resource module attaches its routes to api_v1_bp.
# auth_helpers is NOT imported here — it's a helper module imported by the resource modules themselves.
from . import auth, users, lost_reports, found_items, matches, claims, notifications  # noqa: E402,F401

@api_v1_bp.app_errorhandler(404)
def _404(_e):
    if request.path.startswith("/api/v1/"):
        return jsonify({"error": "not_found"}), 404
    return _e

@api_v1_bp.app_errorhandler(405)
def _405(_e):
    if request.path.startswith("/api/v1/"):
        return jsonify({"error": "method_not_allowed"}), 405
    return _e

@api_v1_bp.app_errorhandler(500)
def _500(_e):
    if request.path.startswith("/api/v1/"):
        return jsonify({"error": "internal_server_error"}), 500
    return _e
```

## 11. Acceptance criteria

The milestone is complete when:

1. `app/api/v1/` exists and contains the eight files listed in §4.
2. `users.api_token_hash` column exists in the DB (live + `database/schema.sql`).
3. Every endpoint in §6 is reachable and behaves per its row.
4. `POST /api/v1/auth/login` issues a token; subsequent requests with `Authorization: Bearer <token>` succeed.
5. `POST /api/v1/auth/login` for an unknown email or wrong password returns `401 {"error": "invalid_credentials"}`.
6. Browser session is accepted as a fallback (`/api/v1/me` returns the right user when called with the same browser that's logged in).
7. JSON response/error envelopes match §8 exactly (key names, status codes).
8. `to_dict()` outputs never contain `password_hash` or `api_token_hash`.
9. Hitting `/api/v1/nonexistent-route` returns JSON 404 (not the HTML 404 page).
10. Existing HTML routes continue to work unchanged — the new blueprint adds endpoints, it doesn't modify or remove any.

## 12. What this unblocks

- **M3 (API testing artifacts):** Postman/Thunder Client collection can be built directly against this endpoint surface; screenshots become straightforward.
- **M5 (final documentation):** the §VI.8 "API Documentation" table lifts directly from §6 of this spec.
- **Defense (M7):** the auth flow, error envelope, and permission model are all clearly documented above, giving talking points for the demo.
