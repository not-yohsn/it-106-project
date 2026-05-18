# Lost and Found Management System
**IT106 — Integrative Programming and Technologies · Final Course Project**

A web-based system for reporting lost items, logging found items, automatically matching them, and notifying owners. Maps to **Suggested Project Title #11** in the [IT106 Final Term Project Specifications](IT106%20Final%20Term%20Project%20Specifications.pdf).

---

## 1. Background

Caraga State University currently handles lost and found items through a fragmented, ad-hoc workflow: students post sightings on Facebook groups, finders walk items over to the Student Local Government (SLG) Office, and the office keeps logs on paper or in private spreadsheets. The result is predictable — items go unreturned because their owners never see the post, records get lost when phones change hands, and the same description gets re-reported across three channels with no single source of truth.

The **Lost and Found Management System** replaces that workflow with a single web-based platform. Students file a lost report once; staff log found items once; the system automatically suggests matches based on category, keywords, and location overlap; and the original reporter is notified the moment a match appears. The result is a centralized, searchable record of every lost and found item on campus, plus a workflow that takes a recovered item from *Reported* → *Matched* → *Claimed* → *Released* without anyone retyping data.

---

## 2. Objectives

### General Objective

To design and develop an integrated web-based application that demonstrates CRUD operations, database connectivity, API integration, and application of programming concepts.

### Specific Objectives

The system aims to:

1. Develop a functional web-based application for reporting lost items and logging found items on campus.
2. Implement complete CRUD operations for lost reports, found items, claims, and user accounts.
3. Integrate a MySQL database with seven related tables, primary/foreign keys, and proper constraints for record management.
4. Create REST API endpoints (`/api/v1/*`) exposing every core resource as JSON for `GET`, `POST`, `PUT`, and `DELETE`.
5. Apply object-oriented programming concepts — class definitions, model inheritance (`UserMixin` + `db.Model`), and service-style modules for matching and notification logic.
6. Apply the **MVC** design pattern (models / templates / route blueprints) and the **Application Factory** pattern (`create_app`).
7. Test the system through functional test cases and document the results in the IT106 testing-results table.

---

## 3. Scope and Limitations

### In Scope

- Registration and authentication for **student**, **staff**, and **admin** roles
- Filing lost reports with photo, category, location, and date
- Logging found items by staff or finders, with auto-resized photo upload
- Automatic match scoring based on category, shared keywords, and location overlap
- Claim workflow (`pending → approved → released`) with item-status transitions
- In-app notifications (with optional email via Flask-Mail)
- Per-role dashboards with KPI cards and personal stats
- CSV exports of lost reports, found items, and claims (staff only)
- Admin-side user management (promote/demote without touching SQL)
- REST API for every core resource (Milestone M2)

### Out of Scope (v1)

- Native mobile apps (the web UI is responsive)
- Payment, rewards, or any monetary transaction
- AI / image-based matching — text and category matching only
- Off-campus or public-facing deployment beyond the demo
- Integration with external university systems (student records, ID system)

---

## 4. System Architecture

```
 ┌────────────┐    HTTP/HTTPS    ┌──────────────────────────────┐    SQL    ┌────────────┐
 │  Browser   │ ───────────────▶ │  Flask 3 (Gunicorn on Render)│ ────────▶ │  MySQL 8   │
 │ (Bootstrap │                  │                              │           │  (TiDB     │
 │  5 + JS)   │ ◀─────────────── │  • Blueprints (MVC routes)   │ ◀──────── │   Cloud)   │
 └────────────┘  HTML / JSON     │  • SQLAlchemy ORM            │           └────────────┘
                                 │  • Flask-Login + WTForms     │
                                 │  • /api/v1/*  (M2 — JSON)    │
                                 │  • Jinja2 templates          │
                                 └──────────────────────────────┘
```

**Request flow:**

1. The browser sends a request — either an HTML form post (server-rendered pages) or a `fetch()` call to `/api/v1/*` (JSON API, M2).
2. Flask's app factory (`create_app`) routes the request to the matching blueprint controller (`auth`, `reports`, `found`, `matches`, `claims`, `notifications`, `admin`, `api`).
3. The controller validates input through WTForms or JSON schema, calls the SQLAlchemy model layer, and runs supporting services (`matching.py`, `notify.py`, `utils.py`).
4. The response is either a Jinja-rendered HTML page or a JSON payload.

---

## 5. IT106 Course Mapping

Each concept the PDF requires (§I) and where this project applies it:

| IT106 Required Concept           | Where it lives in this codebase                                        |
| -------------------------------- | ---------------------------------------------------------------------- |
| Web application development      | Flask 3 + Jinja2 + Bootstrap 5 — [app/__init__.py](app/__init__.py)    |
| RESTful API integration          | `/api/v1/*` JSON endpoints — **planned, see Milestone M2 below**       |
| Database connectivity            | SQLAlchemy + PyMySQL → MySQL 8 — [app/config.py](app/config.py)        |
| Data mapping / JSON exchange     | API serializers (M2) + CSV exports (`*/routes.py:export_csv`)          |
| Middleware / backend services    | Flask blueprints — [app/__init__.py](app/__init__.py#L20-L35)          |
| Frontend ↔ backend integration   | Jinja templates + browser `fetch()` against `/api/v1/*` (M2)           |
| OOP — class / inheritance        | `class User(UserMixin, db.Model)` in [app/models.py](app/models.py)    |
| Design pattern                   | **MVC** (models/views/routes split via blueprints) + **Application Factory** (`create_app`) + **Repository-like access** via SQLAlchemy queries |
| Basic security & validation      | Werkzeug password hashing, Flask-Login sessions, Flask-WTF CSRF + validators, `@staff_required` / `@admin_required` — [app/decorators.py](app/decorators.py) |
| Testing & documentation          | Test-case table + screenshots in `docs/` — **planned, see M3/M5/M6**   |

---

## 6. Minimum Feature Compliance

| PDF Requirement                                                | Status         | Location                                                |
| -------------------------------------------------------------- | -------------- | ------------------------------------------------------- |
| User Interface (homepage, nav, forms, tables, search, buttons) | ✅ done        | [app/templates/](app/templates/)                        |
| CRUD operations                                                | ✅ done        | [app/reports/](app/reports/), [app/found/](app/found/), [app/claims/](app/claims/) |
| REST API endpoints (`GET/POST/PUT/DELETE` returning JSON)      | ✅ done        | [app/api/v1/](app/api/v1/) (~24 endpoints across 6 resources)         |
| Database — 3+ related tables w/ PK & FK                        | ✅ done (7 tables) | [database/schema.sql](database/schema.sql)          |
| Authentication / user validation                               | ✅ done        | [app/auth/](app/auth/), Flask-WTF validators, Bearer token in [app/api/v1/auth.py](app/api/v1/auth.py)     |
| Data exchange via JSON                                         | ✅ done        | `/api/v1/*` responses + structured envelopes per [docs/superpowers/specs/2026-05-19-rest-api-design.md](docs/superpowers/specs/2026-05-19-rest-api-design.md) §8  |
| OOP (class, inheritance, etc.)                                 | ✅ done        | [app/models.py](app/models.py)                          |
| At least one design pattern                                    | ✅ done        | MVC + Application Factory (see §5 above)                |

---

## 7. Features (current)

- **Lost reports** with photo, category, location, and date
- **Found items** logged by staff or finders, with photo upload (auto-resized via Pillow)
- **Match engine** — scores candidate pairs by category, shared keywords, and location overlap; shows a *"why this matched"* breakdown
- **Claim workflow** — `pending → approved → released`, with item-status transitions
- **In-app notifications** with unread badge in the navbar (optional email via Flask-Mail)
- **Per-role dashboard** — KPI cards for staff/admin, personal stats for students
- **CSV exports** for lost reports, found items, and claims (staff only)
- **Admin user management** — promote / demote without touching SQL
- **Privacy** — only the reporter and staff see full details on a lost report; other students see item name, photo, category, post date

---

## 8. Tech Stack

| Layer        | Choice                                            |
| ------------ | ------------------------------------------------- |
| Backend      | Python 3.12 + **Flask 3** (approved hybrid backend) |
| ORM          | SQLAlchemy via Flask-SQLAlchemy                   |
| Auth         | Flask-Login + Werkzeug password hashing           |
| Forms / CSRF | Flask-WTF + WTForms                               |
| Database     | MySQL 8 (XAMPP locally, TiDB Cloud in production) |
| Frontend     | Jinja2 + Bootstrap 5                              |
| API Format   | JSON                                              |
| Image upload | Pillow                                            |
| Email        | Flask-Mail (optional)                             |
| Production   | Gunicorn on Render                                |

---

## 9. Submission Roadmap to May 25, 2026

| #  | Milestone                       | Deliverable                                                                 | Status |
| -- | ------------------------------- | --------------------------------------------------------------------------- | ------ |
| M1 | Gap analysis + scope alignment  | This README + course-mapping tables                                         | ✅ done |
| M2 | **REST API layer (JSON)**       | `app/api/v1/` blueprint exposing `GET/POST/PUT/DELETE` for users, lost reports, found items, matches, claims, notifications | ⏭ next |
| M3 | API testing artifacts           | Postman / Thunder Client collection + screenshots in `docs/api-tests/`      | ⬜ todo |
| M4 | OOP + design-pattern write-up   | `docs/oop-and-patterns.md` pointing to exact files/lines for each concept   | ⬜ todo |
| M5 | IT106 final documentation       | `docs/final-documentation.md` covering all 12 sections in PDF §VI           | ⬜ todo |
| M6 | System screenshots              | `docs/screenshots/` — login, dashboard, add form, data table, edit, delete, search, API tests | ⬜ todo |
| M7 | Presentation deck (10–15 min)   | `docs/presentation.pptx` (or PDF) — 11 required sections in PDF §VII        | ⬜ todo |
| M8 | User manual + submission ZIP    | `docs/user-manual.pdf`, SQL dump, individual-contribution form, GitHub link, `IT106_FinalProject_<Group>_LostAndFound.zip` per PDF §VIII | ⬜ todo |

### How rubric points map to milestones

| Rubric Criterion                          | Points | Covered by                          |
| ----------------------------------------- | -----: | ----------------------------------- |
| System Functionality                      |     25 | Already built · M6 screenshots prove it |
| Backend & API Integration                 |     15 | **M2** (currently 0 — biggest gap)  |
| Database Design & Integration             |     15 | Already built · M5 documents it     |
| Frontend Design & Usability               |     10 | ✅ Custom "Quiet Polish" design system shipped on top of Bootstrap; M6 screenshots prove it |
| OOP & Design Patterns                     |     10 | Already built · **M4** documents it |
| Validation & Basic Security               |     10 | Already built · M5 documents it     |
| Testing & Debugging                       |      5 | ✅ M3 shipped — Thunder Client collection + testing-results table; M5 references it |
| Documentation                             |      5 | **M5**                              |
| Presentation & Demonstration              |      5 | **M7**                              |

---

## 10. Quick Start (local)

### Prerequisites
- Python 3.11+
- XAMPP (for MySQL + phpMyAdmin)
- Git

### Setup
```powershell
git clone https://github.com/<your-user>/lost-and-found.git
cd lost-and-found

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

Copy-Item .env.example .env
```

### Database
1. Start MySQL via the XAMPP Control Panel
2. Open http://localhost/phpmyadmin → SQL tab
3. Paste and run [database/schema.sql](database/schema.sql)

### Run
```powershell
python run.py
```

App at **http://127.0.0.1:8000**.

---

## 11. Deploy to Render + TiDB Cloud

1. **TiDB Cloud Serverless** — create a free cluster, run the table-creation statements (without `CREATE DATABASE`/`USE`) in the `test` database
2. **GitHub** — push this repo (GitHub Desktop or `git push`)
3. **Render** — *New + → Web Service* from the repo:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn run:app`
4. **Environment variables** on Render:

   | Key | Value |
   | --- | ----- |
   | `DB_HOST` | TiDB host (ends in `.tidbcloud.com`) |
   | `DB_PORT` | `4000` |
   | `DB_USER` | TiDB user |
   | `DB_PASSWORD` | TiDB password |
   | `DB_NAME` | `test` |
   | `DB_SSL` | `1` |
   | `SECRET_KEY` | output of `python -c "import secrets; print(secrets.token_hex(32))"` |

> **Note:** Render's free tier has an ephemeral filesystem — uploaded photos persist within a deployment but reset on each redeploy. For permanent photos, swap [app/utils.py](app/utils.py)`:save_uploaded_image` to use Cloudinary / S3.

---

## 12. User Roles

| Role        | Capabilities                                                                       |
| ----------- | ---------------------------------------------------------------------------------- |
| **Student** | File lost reports, log found items, browse, claim matched items                    |
| **Staff**   | All student capabilities + log office-turned-in items, confirm matches, verify claims, release items |
| **Admin**   | All staff capabilities + manage user roles via `/admin/users`                      |

New accounts always start as **student**. Promote via the admin UI, or directly:

```sql
UPDATE users SET role = 'admin' WHERE email = 'someone@example.com';
```

---

## 13. Project Structure

```
.
├── app/
│   ├── __init__.py          # Flask app factory + blueprint registration  ← Application Factory pattern
│   ├── config.py            # reads .env, handles DB_SSL for cloud MySQL
│   ├── extensions.py        # db, login_manager, mail singletons          ← Singleton pattern
│   ├── models.py            # 7 SQLAlchemy entities                       ← Model layer (MVC)
│   ├── matching.py          # match scoring (category + keywords + location)
│   ├── notify.py            # in-app + optional email helpers             ← Observer-like notifier
│   ├── stats.py             # dashboard KPIs
│   ├── decorators.py        # @staff_required / @admin_required
│   ├── utils.py             # image upload + resize
│   ├── auth/                # register / login / logout                   ← Controller layer (MVC)
│   ├── reports/             # lost reports + CSV export
│   ├── found/               # found items + CSV export
│   ├── matches/             # confirm / dissolve
│   ├── claims/              # claim lifecycle + CSV export
│   ├── notifications/       # inbox + mark-read
│   ├── admin/               # user management
│   ├── main/                # landing page + dashboard
│   ├── api/                 # M2: /api/v1/* JSON endpoints
│   ├── templates/           # Jinja2 (Bootstrap 5)                        ← View layer (MVC)
│   └── static/              # CSS + uploaded photos
├── database/
│   └── schema.sql           # MySQL schema for the 7 tables
├── docs/                    # M3–M8: IT106 submission artifacts
│   ├── api-tests/           # Postman/Thunder Client screenshots (M3)
│   ├── screenshots/         # system screenshots (M6)
│   ├── oop-and-patterns.md  # OOP + design pattern write-up (M4)
│   ├── final-documentation.md  # IT106 §VI format (M5)
│   ├── user-manual.pdf      # short user manual (M8)
│   └── presentation.pptx    # final defense deck (M7)
├── others/                  # original brief + ERD prototype
├── ScopeProject.md          # full project scope, milestones, risk register
├── IT106 Final Term Project Specifications.pdf
├── requirements.txt
├── runtime.txt              # Python version pin for Render
├── Procfile                 # Render start command
├── .env.example             # environment template
└── run.py                   # entrypoint
```

---

## 14. Data Model

Seven tables (PDF §V.4 requires only 3+), derived from the ERD in [others/prototype.html](others/prototype.html):

`users` · `finders` · `lost_reports` · `found_items` · `matches` · `claims` · `notifications`

See [ScopeProject.md §6](ScopeProject.md) for the full relationship breakdown.
