# Lost and Found Management System — Final Project Documentation

> Formatted per IT 106 Final Term Project Specifications §VI. Each numbered section corresponds 1-to-1 with the rubric.

---

## 1. Title Page

| Field             | Value                                                              |
|-------------------|--------------------------------------------------------------------|
| **Project title** | Lost and Found Management System                                   |
| **Course title**  | IT 106 – Integrative Programming and Technologies                  |
| **Section**       | _[TBD — fill in your section]_                                     |
| **Group number**  | _[TBD — fill in your group number]_                                |
| **Members**       | _[TBD — fill in all member names, one per line]_                   |
| **Instructor**    | _[TBD — fill in your instructor's name]_                           |
| **Date submitted**| May 25, 2026                                                       |

---

## 2. Introduction

University campuses lose track of dozens of items every week — student IDs left in classrooms, backpacks forgotten in the library, jackets abandoned at the gym. Today this is handled informally: a student who finds something brings it to the security office, the owner files a Facebook post or pins a note on a bulletin board, and the two parties hope to meet in the middle. Information is fragmented across channels, items sit in lost-and-found bins for weeks, and there is no audit trail when an item finally changes hands.

The **Lost and Found Management System** is a centralized web application that closes that gap. Students report lost items in a structured form. Staff log found items with photos and location metadata. The system suggests possible matches between the two and lets staff confirm them. The original owner files a claim, staff verifies their proof, and the item is released — every transition recorded with a timestamp and the user who performed it.

The system matters because it eliminates the manual, paper-based, and Facebook-based workflows that universities still rely on. It gives the security office a single source of truth, it gives students a way to track their reports without walking across campus, and it gives administration the audit log required for property-handover policies. It is also the chosen vehicle for demonstrating the integration of frontend, backend, database, REST API, OOP, and design-pattern concepts required by IT 106.

---

## 3. Objectives of the Project

### General Objective

To design and develop an integrated web-based application that demonstrates CRUD operations, database connectivity, REST API integration, and the application of object-oriented programming and design-pattern concepts taught in IT 106.

### Specific Objectives

The system aims to:

1. **Develop a functional web-based application** — built on Flask 3 + Jinja2 + Bootstrap 5, served at `http://127.0.0.1:8000` ([run.py](../run.py), [app/__init__.py](../app/__init__.py)).
2. **Implement CRUD operations** on all seven domain entities (`users`, `finders`, `lost_reports`, `found_items`, `matches`, `claims`, `notifications`) — every entity supports Create, Read, Update, and Delete via both the browser UI and the REST API.
3. **Integrate a database for record management** — MariaDB 10.4.32 (MySQL protocol) running under XAMPP, accessed via SQLAlchemy ORM with seven related tables, primary keys, foreign keys, and ENUM-typed status fields. Schema in [database/schema.sql](../database/schema.sql).
4. **Create REST API endpoints for data exchange** — 30+ method/route pairs across six resources at `/api/v1/*`, all responding with JSON envelopes (`{"data": ...}` / `{"error": ...}`). Endpoints documented in section 8 of this document and at [docs/api-smoke-test.md](api-smoke-test.md).
5. **Apply object-oriented programming concepts** — five distinct concepts (class definition, multiple inheritance, encapsulation, polymorphism, abstraction) each mapped to a specific file and line. Full write-up in [docs/oop-and-patterns.md](oop-and-patterns.md).
6. **Use at least one software design pattern** — five patterns applied (Application Factory, Blueprint, Decorator, State, ORM/Active-Record-style). Same write-up.
7. **Test the system based on functional requirements** — 15 documented test cases covering authentication, authorization, CRUD, validation, status transitions, and error envelopes — see [docs/api-tests/results-table.md](api-tests/results-table.md). All 25 representative requests captured as Postman screenshots in [docs/api-tests/screenshots/](api-tests/screenshots/).

---

## 4. Scope and Limitations

### Scope — what the system does

- **User accounts** with three roles: `student`, `staff`, `admin`. Self-registration for students; staff/admin promotion via the admin panel.
- **Authentication** via two complementary schemes: Flask-Login browser sessions for the website, and Bearer-token authentication for the REST API (raw token issued at `/api/v1/auth/login`, hashed at rest in `users.api_token_hash`).
- **Lost-item reporting** — student fills a structured form (item name, description, category, location, date lost, optional photo). Stored in `lost_reports`.
- **Found-item logging** — staff/admin logs a found item, optionally linked to a `Finder` record (the person who turned the item in if they are not a system user).
- **Matching workflow** — staff can manually link a `lost_report` to a `found_item` to create a `match`; a confidence score and timestamp are recorded.
- **Claim workflow** — the original owner submits a claim; staff approves, rejects, or releases. Status transitions are enforced (`pending → approved → released`, `pending → rejected`; terminal states block reversal).
- **Notifications** — in-app notification feed (per-user unread counter injected into every template) plus email on key events (Flask-Mail).
- **CSV exports** of lost reports, found items, and claims for staff record-keeping.
- **Privacy filter** — non-owner students viewing another student's lost report see only public fields (item name, category, photo, date posted). The full description, exact location, and contact details are hidden.
- **Role-based access control** — applied at both the view layer (`@staff_required`, `@admin_required`) and the API layer (`@api_login_required`, `@api_staff_required`, `@api_admin_required`).
- **Pagination** — all list endpoints return a `{data, page, per_page, total}` envelope.
- **Search and filter** — by category, location, status, and date range on lost-report and found-item lists.
- **Responsive UI** built on Bootstrap 5 with a custom design system (Inter font, indigo accent, soft status tints).

### Limitations — what the system does not do

- **Web only** — no native mobile app. The site is responsive and works in mobile browsers, but there is no iOS/Android shell.
- **No SMS** — notifications are in-app and email only. There is no Twilio/SMS integration.
- **Local file storage** — uploaded photos are stored on the application server's disk under `app/static/uploads/`. There is no S3/CDN integration.
- **No real-time push** — the unread-notification badge is computed per-request via a Flask context processor; the user sees new notifications when they navigate, not via websockets.
- **No payment processing** — out of scope for a lost-and-found system.
- **No university SSO** — accounts are local to this app; there is no SAML, OAuth, or LDAP bridge to the university's directory.
- **One photo per item** — JPEG/PNG only, no multi-image gallery.
- **English-only UI** — no localization.

---

## 5. System Features

| Feature                       | Description                                                                                                                            |
|-------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| User registration & login     | Self-registration for students; bcrypt-style scrypt password hashing via Werkzeug. Browser session + API token both supported.        |
| Role-based dashboard          | Students see their own reports and notifications; staff/admin see system-wide KPI cards (open reports, pending claims, recent matches). |
| Lost report management        | Students create, view, edit, and delete their own lost reports. Staff/admin can view all and update status.                            |
| Found item management         | Staff/admin logs found items with finder details and photo. Students can also create found-item entries.                               |
| Match management              | Staff manually links a lost report to a found item, recording a confidence score. Both records flip to `matched` status automatically.  |
| Claim workflow                | Owner submits a claim; staff approves, rejects, or releases. Status transitions enforced by a state machine.                            |
| Notifications                 | In-app notification feed with unread badge in the navbar. Email on match-confirmed and claim-approved events.                          |
| Admin user management         | Admin can promote students to staff, demote staff to students, and reset passwords. No SQL needed.                                     |
| CSV export                    | Staff can export lost reports, found items, and claims to CSV for offline record-keeping.                                              |
| Privacy filter                | Non-owner students viewing another's lost report see only item name, category, photo, and date posted — not description or location.   |
| REST API                      | 30+ JSON endpoints at `/api/v1/*`, paginated lists, structured error envelopes, Bearer-token auth.                                     |
| Search, filter, pagination    | Filter by category/location/status/date on list pages; paginated with `page` and `per_page` query parameters.                          |
| Responsive Bootstrap 5 UI     | Custom design system (Inter font, indigo accent, soft status tints, status timelines, auth-shell layout).                              |

---

## 6. System Architecture

### Layered diagram

```
┌────────────────────────────────────────────────────────────────────┐
│  Presentation                                                       │
│  ─ Jinja2 templates (app/templates/)                                │
│  ─ Bootstrap 5 + custom CSS (app/static/css/style.css)              │
│  ─ Light JS (browser fetch() for some interactions)                 │
└────────────────────────────────────────────────────────────────────┘
                            │   HTTP / JSON
                            ▼
┌────────────────────────────────────────────────────────────────────┐
│  Application                                                        │
│  ─ Flask 3 app factory (app/__init__.py:create_app)                 │
│  ─ 9 blueprints, one per resource area:                             │
│    auth · main · reports · found · matches · claims                 │
│    notifications · admin · api_v1                                   │
│  ─ Decorators: @api_login_required, @staff_required, etc.           │
│  ─ Auth resolver: bearer-token first, then session fallback         │
└────────────────────────────────────────────────────────────────────┘
                            │   SQLAlchemy ORM
                            ▼
┌────────────────────────────────────────────────────────────────────┐
│  Data Access                                                        │
│  ─ SQLAlchemy 2.x models (app/models.py)                            │
│  ─ Connection pool, identity-map, lazy relationship loading         │
│  ─ to_dict() serializers on every model                             │
└────────────────────────────────────────────────────────────────────┘
                            │   PyMySQL driver
                            ▼
┌────────────────────────────────────────────────────────────────────┐
│  Persistence                                                        │
│  ─ MariaDB 10.4.32 (MySQL protocol) under XAMPP                     │
│  ─ Database: lost_and_found2.0                                      │
│  ─ 7 related tables, PKs, FKs, ENUM status fields                   │
└────────────────────────────────────────────────────────────────────┘
```

### Request lifecycle (e.g. `POST /api/v1/lost-reports`)

1. **Browser / Postman** sends an HTTP request with `Authorization: Bearer <token>` and a JSON body.
2. **Flask app factory** (`create_app`) routes the request to the `api_v1_bp` blueprint mounted at `/api/v1`.
3. **Decorator chain** — `@api_v1_bp.route("/lost-reports", methods=["POST"])` matches, then `@api_login_required` resolves the user from the bearer token via `_resolve_current_api_user` ([app/api/v1/auth_helpers.py:17](../app/api/v1/auth_helpers.py#L17)). On failure, returns `401 {"error": "authentication_required"}`.
4. **View function** validates payload, constructs a `LostReport` model instance, calls `db.session.add(report); db.session.commit()`.
5. **SQLAlchemy** translates the model write into an `INSERT` statement, sends it to MariaDB via PyMySQL.
6. **Response serializer** calls `report.to_dict()` and returns `201 {"data": {...}}`.

The entire flow is deterministic and testable — the Postman collection at [docs/api-tests/postman-collection_LostFound.json](api-tests/postman-collection_LostFound.json) exercises this exact path.

---

## 7. Database Design

The database is named **`lost_and_found2.0`** and contains seven tables. The schema is committed at [database/schema.sql](../database/schema.sql) and seeded via the idempotent script at [scripts/seed_demo_data.py](../scripts/seed_demo_data.py).

### Entity-Relationship overview

```
users (1)──────┐
               │
               ├──< (M) lost_reports ────(1:1)──┐
               │                                ├──< (M) claims
               ├──< (M) found_items ────(1:1)───┘
               │                                ▲
               ├──< (M) notifications           │
               │                                │
finders (1)────┴──< (M) found_items             │
                                                │
                                       matches  ┘
```

### Table-by-table

#### `users`
The principal actor table. Stores accounts, role, and credentials (both interactive password and API token, each hashed with Werkzeug scrypt).

| Field            | Type                                           | Description                                                        |
|------------------|------------------------------------------------|--------------------------------------------------------------------|
| `user_id`        | INT, PK, AUTO_INCREMENT                        | Primary key.                                                       |
| `name`           | VARCHAR(120), NOT NULL                         | Full name.                                                         |
| `email`          | VARCHAR(120), UNIQUE, NOT NULL, INDEX          | Login identifier.                                                  |
| `phone`          | VARCHAR(20)                                    | Optional contact.                                                  |
| `role`           | ENUM('student','staff','admin'), NOT NULL      | Authorization level. Default `student`.                            |
| `password_hash`  | VARCHAR(255), NOT NULL                         | Werkzeug-scrypt hash of the user password.                         |
| `api_token_hash` | VARCHAR(255), NULL                             | Werkzeug-scrypt hash of the current API token. NULL after logout.  |
| `created_at`     | DATETIME, default `CURRENT_TIMESTAMP`          | Account creation timestamp.                                        |

Sample rows from the seed script: `admin@lostfound.local / Admin123!` (admin), `student@lostfound.local / Student123!` (student), `student2@lostfound.local / Student123!` (student — used to demonstrate the privacy filter).

#### `finders`
A person who turned in an item but does not have a system account. Optional FK from `found_items`.

| Field        | Type                                  | Description                            |
|--------------|---------------------------------------|----------------------------------------|
| `finder_id`  | INT, PK, AUTO_INCREMENT               | Primary key.                           |
| `name`       | VARCHAR(120), NOT NULL                | Finder's name.                         |
| `email`      | VARCHAR(120)                          | Contact email.                         |
| `phone`      | VARCHAR(20)                           | Contact phone.                         |
| `created_at` | DATETIME                              | Record creation timestamp.             |

#### `lost_reports`
A student-submitted record of a lost item.

| Field          | Type                                                                  | Description                                                  |
|----------------|-----------------------------------------------------------------------|--------------------------------------------------------------|
| `report_id`    | INT, PK, AUTO_INCREMENT                                               | Primary key.                                                 |
| `user_id`      | INT, FK → `users.user_id`, NOT NULL                                   | The student who reported the item.                           |
| `item_name`    | VARCHAR(120), NOT NULL                                                | Short title (e.g. "Black Backpack").                         |
| `description`  | TEXT                                                                  | Detailed description (hidden from non-owner students).       |
| `category`     | VARCHAR(60)                                                           | Tag for filtering (e.g. `bag`, `stationery`, `id`).          |
| `location`     | VARCHAR(120)                                                          | Where the item was last seen.                                |
| `date_lost`    | DATE                                                                  | Approximate date the item went missing.                      |
| `photo_path`   | VARCHAR(255)                                                          | Optional uploaded image path.                                |
| `status`       | ENUM('reported','matched','claimed','closed')                         | Workflow state. Default `reported`.                          |
| `created_at`   | DATETIME                                                              | Record creation timestamp.                                   |

#### `found_items`
A staff- or student-logged record of a found item.

| Field            | Type                                                                  | Description                                                  |
|------------------|-----------------------------------------------------------------------|--------------------------------------------------------------|
| `item_id`        | INT, PK, AUTO_INCREMENT                                               | Primary key.                                                 |
| `finder_id`      | INT, FK → `finders.finder_id`, NULL                                   | Optional non-user finder.                                    |
| `logged_by`      | INT, FK → `users.user_id`, NULL                                       | The system user who logged the entry.                        |
| `item_name`      | VARCHAR(120), NOT NULL                                                | Short title.                                                 |
| `description`    | TEXT                                                                  | Detailed description.                                        |
| `category`       | VARCHAR(60)                                                           | Tag for filtering.                                           |
| `location_found` | VARCHAR(120)                                                          | Where the item was discovered.                               |
| `date_found`     | DATE                                                                  | Approximate find date.                                       |
| `photo_path`     | VARCHAR(255)                                                          | Optional image path.                                         |
| `status`         | ENUM('logged','matched','released')                                   | Workflow state. Default `logged`.                            |
| `created_at`     | DATETIME                                                              | Record creation timestamp.                                   |

#### `matches`
A confirmed pairing between one lost report and one found item. 1:1 on both sides.

| Field              | Type                                                          | Description                                  |
|--------------------|---------------------------------------------------------------|----------------------------------------------|
| `match_id`         | INT, PK, AUTO_INCREMENT                                       | Primary key.                                 |
| `lost_report_id`   | INT, FK → `lost_reports.report_id`, UNIQUE, NOT NULL          | The lost side.                               |
| `found_item_id`    | INT, FK → `found_items.item_id`, UNIQUE, NOT NULL             | The found side.                              |
| `matched_at`       | DATETIME                                                      | When the match was confirmed.                |
| `confidence_score` | FLOAT                                                         | 0.0–1.0 confidence assigned by the matcher.  |

#### `claims`
The owner's formal request to retrieve a matched item.

| Field          | Type                                                              | Description                                                          |
|----------------|-------------------------------------------------------------------|----------------------------------------------------------------------|
| `claim_id`     | INT, PK, AUTO_INCREMENT                                           | Primary key.                                                         |
| `match_id`     | INT, FK → `matches.match_id`, NOT NULL                            | The match being claimed.                                             |
| `claimant_id`  | INT, FK → `users.user_id`, NOT NULL                               | The user filing the claim (usually the original report owner).       |
| `verified_by`  | INT, FK → `users.user_id`, NULL                                   | Staff/admin who approved or released. NULL until acted on.           |
| `status`       | ENUM('pending','approved','rejected','released')                  | State-machine status. Default `pending`.                             |
| `notes`        | TEXT                                                              | Free-form notes (proof description, staff remarks).                  |
| `submitted_at` | DATETIME                                                          | When the claim was filed.                                            |
| `resolved_at`  | DATETIME, NULL                                                    | Populated when status becomes `approved`, `rejected`, or `released`. |

#### `notifications`
In-app notification feed; one row = one badge in the user's navbar.

| Field             | Type                                  | Description                                              |
|-------------------|---------------------------------------|----------------------------------------------------------|
| `notification_id` | INT, PK, AUTO_INCREMENT               | Primary key.                                             |
| `user_id`         | INT, FK → `users.user_id`, NOT NULL, INDEX | Recipient.                                          |
| `title`           | VARCHAR(160), NOT NULL                | Bold line in the notification card.                      |
| `body`            | TEXT                                  | Detail.                                                  |
| `link`            | VARCHAR(255)                          | Where clicking the notification takes the user.          |
| `is_read`         | BOOLEAN, INDEX, default `FALSE`       | Whether the user has acknowledged it.                    |
| `created_at`      | DATETIME                              | Timestamp.                                               |

### Sample data

Running `python scripts/seed_demo_data.py` on a fresh database creates:
- 3 users (admin, student, student2)
- 3 lost reports owned by `student`
- 3 found items logged by `admin`
- 1 confirmed `match` linking Black Backpack (lost) ↔ Black Backpack (found)
- 1 pending `claim` filed by `student`
- 1 unread `notification` to `student` about the possible match

These rows back the M3 testing artifacts.

---

## 8. API Documentation

All endpoints are mounted under `/api/v1` and return JSON. Authentication is by Bearer token (`Authorization: Bearer <hex64>`) issued at login, with browser-session cookies accepted as a fallback for in-browser fetch calls. Errors use the envelope `{"error": "<code>"}` or `{"error": "validation_failed", "fields": {...}}`. List endpoints return `{"data": [...], "page": N, "per_page": N, "total": N}`.

### Authentication

| Method | Endpoint               | Auth          | Purpose                                                       |
|--------|------------------------|---------------|---------------------------------------------------------------|
| POST   | `/api/v1/auth/login`   | none          | Validate credentials, issue a new Bearer token (replaces old) |
| POST   | `/api/v1/auth/logout`  | login required| Invalidate the caller's Bearer token (`api_token_hash = NULL`)|

### Users

| Method | Endpoint                  | Auth   | Purpose                                                    |
|--------|---------------------------|--------|------------------------------------------------------------|
| GET    | `/api/v1/users`           | login  | Paginated list of users.                                   |
| GET    | `/api/v1/me`              | login  | Current authenticated user.                                |
| GET    | `/api/v1/users/<id>`      | login  | Get one user.                                              |
| POST   | `/api/v1/users`           | admin  | Create a new user.                                         |
| PUT    | `/api/v1/users/<id>`      | admin  | Update name, email, role, phone, or reset password.        |
| DELETE | `/api/v1/users/<id>`      | admin  | Hard-delete a user.                                        |

### Lost reports

| Method | Endpoint                          | Auth   | Purpose                                                          |
|--------|-----------------------------------|--------|------------------------------------------------------------------|
| GET    | `/api/v1/lost-reports`            | login  | Paginated list. Privacy filter applied for non-owner students.   |
| GET    | `/api/v1/lost-reports/<id>`       | login  | Single report. Privacy filter applied if caller is not the owner.|
| POST   | `/api/v1/lost-reports`            | login  | Create. Owner is set from `g.current_api_user`.                  |
| PUT    | `/api/v1/lost-reports/<id>`       | login  | Update. Owner-or-staff only.                                     |
| DELETE | `/api/v1/lost-reports/<id>`       | login  | Delete. Owner-or-staff only.                                     |

### Found items

| Method | Endpoint                       | Auth   | Purpose                                              |
|--------|--------------------------------|--------|------------------------------------------------------|
| GET    | `/api/v1/found-items`          | login  | Paginated list.                                      |
| GET    | `/api/v1/found-items/<id>`     | login  | Single found item.                                   |
| POST   | `/api/v1/found-items`          | login  | Create.                                              |
| PUT    | `/api/v1/found-items/<id>`     | staff  | Update fields, including status transitions.         |
| DELETE | `/api/v1/found-items/<id>`     | staff  | Delete.                                              |

### Matches

| Method | Endpoint                  | Auth   | Purpose                                                              |
|--------|---------------------------|--------|----------------------------------------------------------------------|
| GET    | `/api/v1/matches`         | login  | Paginated list of matches the caller can see.                        |
| GET    | `/api/v1/matches/<id>`    | login  | Single match.                                                        |
| POST   | `/api/v1/matches`         | staff  | Confirm a match between a lost report and a found item.              |
| DELETE | `/api/v1/matches/<id>`    | staff  | Remove a match (e.g. wrong link). Restores both sides to prior state.|

### Claims

| Method | Endpoint                | Auth   | Purpose                                                                                  |
|--------|-------------------------|--------|------------------------------------------------------------------------------------------|
| GET    | `/api/v1/claims`        | login  | Paginated list. Students see only their own claims; staff see all.                       |
| GET    | `/api/v1/claims/<id>`   | login  | Single claim. Owner-or-staff only.                                                       |
| POST   | `/api/v1/claims`        | login  | File a new claim against a match.                                                        |
| PUT    | `/api/v1/claims/<id>`   | staff  | Update status (with state-machine guard) and/or notes. Sets `verified_by`, `resolved_at`.|
| DELETE | `/api/v1/claims/<id>`   | staff  | Delete a claim.                                                                          |

### Notifications

| Method | Endpoint                          | Auth   | Purpose                                                       |
|--------|-----------------------------------|--------|---------------------------------------------------------------|
| GET    | `/api/v1/notifications`           | login  | Caller's own notifications, paginated.                        |
| PUT    | `/api/v1/notifications/<id>`      | login  | Mark a notification read/unread (caller must own it).         |
| DELETE | `/api/v1/notifications/<id>`      | login  | Delete a notification (caller must own it).                   |

### Error handlers (blueprint-scoped)

| Trigger                        | Response                                                                          |
|--------------------------------|-----------------------------------------------------------------------------------|
| Unmatched route under `/api/v1`| `404 {"error": "not_found"}`                                                      |
| Method not allowed on a route  | `405 {"error": "method_not_allowed"}`                                             |
| Uncaught server-side exception | `500 {"error": "internal_server_error"}`                                          |

These handlers only fire for `/api/v1/*` paths; HTML routes still return the normal Flask error pages. Implementation at [app/api/v1/__init__.py:6-24](../app/api/v1/__init__.py#L6-L24).

### Full request/response examples

For complete request/response samples (headers, body, JSON shape), see the Postman collection at [docs/api-tests/postman-collection_LostFound.json](api-tests/postman-collection_LostFound.json) — 25 working requests with assertions.

---

## 9. Screenshots of the System

### Required screenshot index (per §VI.9)

| Screen                                | Location                                                                              |
|---------------------------------------|---------------------------------------------------------------------------------------|
| Login page                            | `docs/screenshots/01-login.png`                                                       |
| Dashboard                             | `docs/screenshots/02-dashboard.png`                                                   |
| Add form (lost report)                | `docs/screenshots/03-add-lost-report.png`                                             |
| Data table (lost reports list)        | `docs/screenshots/04-lost-reports-table.png`                                          |
| Edit form                             | `docs/screenshots/05-edit-lost-report.png`                                            |
| Delete confirmation                   | `docs/screenshots/06-delete-confirm.png`                                              |
| Search / filter result                | `docs/screenshots/07-search-filter.png`                                               |
| API test (Postman)                    | [docs/api-tests/screenshots/](api-tests/screenshots/) (26 PNGs, one per request)      |

> **Note:** UI screenshots (rows 1–7 above) are the deliverable of milestone M6 and will land in `docs/screenshots/` ahead of submission. The API-test screenshots (row 8) are already captured under [docs/api-tests/screenshots/](api-tests/screenshots/) — all 26 PNGs are committed and visible on GitHub.

---

## 10. Testing Results

A short summary table per §VI.10 — the full 15-case results table lives at [docs/api-tests/results-table.md](api-tests/results-table.md).

| Test Case                                                       | Expected Output                                | Actual Output                                                                         | Status     |
|-----------------------------------------------------------------|------------------------------------------------|---------------------------------------------------------------------------------------|------------|
| Add new lost report                                             | `201 Created` + payload with new `report_id`   | `201` + auto-incremented ID returned                                                  | ✅ Passed  |
| Edit (update) an existing lost report                           | `200 OK` + updated payload                     | `200` + new `description` value persisted                                             | ✅ Passed  |
| Delete a lost report                                            | `204 No Content`                               | `204` empty body                                                                      | ✅ Passed  |
| Search / filter lost reports by category                        | List filtered to matching rows only            | Filter applied; matching rows returned                                                | ✅ Passed  |
| Login with valid admin credentials                              | `200 OK` + 64-char hex token + user payload    | `200` + token issued; populated `token_admin` in Postman env                          | ✅ Passed  |
| Login with wrong password                                       | `401 invalid_credentials`                      | `401 {"error":"invalid_credentials"}`                                                 | ✅ Passed  |
| Access protected endpoint without `Authorization` header        | `401 authentication_required`                  | `401 {"error":"authentication_required"}`                                             | ✅ Passed  |
| Non-owner student GETs another's lost report (privacy filter)   | `200 OK` with public fields only               | `200` — `description`, `location`, `date_lost`, `user_id` absent for non-owner caller | ✅ Passed  |
| Student attempts `DELETE /found-items/:id` (staff-only)         | `403 forbidden`                                | `403 {"error":"forbidden"}`                                                           | ✅ Passed  |
| Invalid claim status transition (approved → pending)            | `400 invalid_transition`                       | `400 {"error":"invalid_transition", "fields":{"status":"..."}}`                       | ✅ Passed  |
| Hit unknown `/api/v1/no-such-route`                             | `404 not_found` JSON (not HTML 404 page)       | `404 {"error":"not_found"}`                                                           | ✅ Passed  |
| Mark notification as read                                       | `200 OK` + `is_read: true`                     | `200` + `is_read` flipped to `true`                                                   | ✅ Passed  |
| List users — pagination envelope present                        | `200 OK` with `data`, `page`, `per_page`, `total` | `200` envelope shape verified                                                       | ✅ Passed  |
| Staff confirms a match                                          | `201 Created`; both items flip to `matched`    | `201` + both flipped (verified via subsequent GET)                                    | ✅ Passed  |
| Approve a pending claim                                         | `200 OK` + `verified_by` set + `resolved_at`   | `200` + both audit fields populated                                                   | ✅ Passed  |

**Test environment:**
- App: Flask 3 + SQLAlchemy + MySQL (MariaDB 10.4.32 via XAMPP)
- DB: `lost_and_found2.0` seeded with `scripts/seed_demo_data.py` (12 rows total)
- Test tool: Postman (VS Code extension), collection [postman-collection_LostFound.json](api-tests/postman-collection_LostFound.json)
- Date executed: 2026-05-19

---

## 11. Conclusion

The Lost and Found Management System is a fully working web application that meets every minimum requirement on the IT 106 specification: it has a frontend interface, server-side logic, an integrated MySQL database, REST API endpoints, two complementary authentication schemes, JSON data exchange, and complete project documentation.

The system demonstrates all the integrative-programming concepts the course set out to teach. Object-oriented design is end-to-end: every database table is a class, every row is an object, and every model implements a uniform `to_dict()` interface so the routing layer can serialize polymorphically. Five design patterns are applied with intent — Application Factory builds the app on demand, Blueprint splits concerns into nine modular folders, Decorator centralizes authorization across 30+ endpoints, State enforces the claim lifecycle, and the SQLAlchemy ORM eliminates handwritten SQL while still letting raw queries through when needed. Each pattern is documented with file:line citations in [docs/oop-and-patterns.md](oop-and-patterns.md).

Beyond the rubric, the project earns a few additional points worth highlighting in the demo: the privacy filter for non-owner students, the dual auth scheme (bearer token plus session cookie) with a single resolver, the JSON-or-HTML error response pattern routed by URL prefix, and the idempotent seed script that lets the grader recreate the demo dataset with one command.

Across the build, the team practiced full-stack engineering, schema design, REST API discipline, test scripting in Postman, and documentation rigor. Those skills generalize directly to industry web development.

---

## 12. References

### Frameworks and libraries

- **Flask** — Pallets Projects. <https://flask.palletsprojects.com/>
- **SQLAlchemy** — SQLAlchemy team. <https://docs.sqlalchemy.org/>
- **Flask-SQLAlchemy** — Pallets-Eco. <https://flask-sqlalchemy.palletsprojects.com/>
- **Flask-Login** — Maxime Cote. <https://flask-login.readthedocs.io/>
- **Flask-WTF** — Pallets-Eco. <https://flask-wtf.readthedocs.io/>
- **Flask-Mail** — Mariano Anaya. <https://flask-mail.readthedocs.io/>
- **Werkzeug** — Pallets Projects (password and token hashing via `generate_password_hash` and `check_password_hash`). <https://werkzeug.palletsprojects.com/>
- **PyMySQL** — PyMySQL contributors. <https://github.com/PyMySQL/PyMySQL>
- **Bootstrap 5** — Twitter / Bootstrap team. <https://getbootstrap.com/>
- **Inter font** — Rasmus Andersson. <https://rsms.me/inter/>

### Tools

- **MariaDB 10.4.32** under XAMPP — <https://mariadb.org/> and <https://www.apachefriends.org/>
- **Postman (VS Code extension)** — collection format v2.1.0. <https://learning.postman.com/>
- **Python `secrets.token_hex(32)`** for raw API token generation — <https://docs.python.org/3/library/secrets.html>
- **`functools.wraps`** for preserving decorated-function metadata — <https://docs.python.org/3/library/functools.html#functools.wraps>

### Course materials

- IT 106 — Integrative Programming and Technologies, Caraga State University, College of Computing and Information Sciences. Final Term Project Specifications by John Michael F. Cutamora.

### Internal cross-references

- [README.md](../README.md) — project overview and milestone status
- [docs/oop-and-patterns.md](oop-and-patterns.md) — OOP and design-pattern write-up
- [docs/api-tests/](api-tests/) — Postman collection, environment, walkthrough, results table, 26 screenshots
- [docs/api-smoke-test.md](api-smoke-test.md) — quick REST API walkthrough
- [database/schema.sql](../database/schema.sql) — committed schema
- [scripts/seed_demo_data.py](../scripts/seed_demo_data.py) — idempotent demo seeder
