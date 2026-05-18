# M3 API Testing Artifacts — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Implementer should follow the `/vibecode` workflow.

**Goal:** Ship the M3 testing artifacts — an idempotent Python seed script, a Thunder Client collection with 26 requests in 7 folders, a Thunder Client environment file, an IT106-format testing-results table, a user-facing README walkthrough, and a `screenshots/` folder placeholder. So the user can import → run → screenshot to satisfy PDF §VIII.8 and §VI.10.

**Architecture:** All artifacts under `docs/api-tests/` (plus one seed script under `scripts/`). Seed script reuses the existing Flask app context — no new Python deps. Thunder Client collection JSON is hand-written. User imports and runs requests in order; each request's Tests panel asserts status code and body shape, and Auth requests use `set-env-var` rules to capture tokens.

**Tech Stack:** Python 3.12 + Flask app context + SQLAlchemy (for the seed). Thunder Client JSON format (no external dependencies for the user; the extension lives in VS Code).

**Spec:** [docs/superpowers/specs/2026-05-19-api-testing-design.md](../specs/2026-05-19-api-testing-design.md)

---

## Verification approach

- **Seed script:** run it, confirm console output matches the expected summary, confirm row counts in MySQL via a small `python -c "..."` query.
- **Thunder Client JSON files:** validate they parse as JSON (`python -c "import json; json.load(open('<path>'))"`). Real "did it import cleanly" verification happens when the user imports them into Thunder Client — that's manual.
- **Markdown files:** confirm they were created and have non-empty content.
- **No automated test framework** is added by this milestone.

---

## File map

```
Created:
  scripts/seed_demo_data.py
  docs/api-tests/
  ├── README.md
  ├── results-table.md
  ├── thunder-collection_LostFound.json
  ├── thunder-environment_LostFound.json
  └── screenshots/.gitkeep

Modified:
  README.md           (mark M3 ✅ done per the standing memory rule)
```

---

## Task 1: Create `scripts/seed_demo_data.py`

**Files:**
- Create: `scripts/seed_demo_data.py`

- [ ] **Step 1: Create the `scripts/` directory if it doesn't exist**

Run: `mkdir scripts` (no-op if already there)

- [ ] **Step 2: Write the seed script**

Write to `scripts/seed_demo_data.py`:

```python
"""Idempotent seed script for the M3 API testing demo.

Creates exactly:
  - 3 users:  admin@lostfound.local (admin), student@lostfound.local (student),
              student2@lostfound.local (student — used to demo the lost-report privacy filter)
  - 3 lost reports owned by `student`
  - 3 found items logged by `admin`
  - 1 confirmed match (Black Backpack lost <-> Black Backpack found)
  - 1 pending claim by `student` on that match
  - 1 unread notification to `student`

Run:  python scripts/seed_demo_data.py
Safe to re-run; every insert checks for an existing row first.
"""
from datetime import date

from app import create_app
from app.extensions import db
from app.models import (
    Claim, FoundItem, LostReport, Match, Notification, User,
)


def upsert_user(name, email, role, password):
    user = User.query.filter_by(email=email).first()
    if user:
        return user, False
    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    return user, True


def upsert_lost_report(user_id, item_name, description, category, location, date_lost):
    existing = LostReport.query.filter_by(user_id=user_id, item_name=item_name).first()
    if existing:
        return existing, False
    row = LostReport(
        user_id=user_id, item_name=item_name, description=description,
        category=category, location=location, date_lost=date_lost,
    )
    db.session.add(row)
    db.session.flush()
    return row, True


def upsert_found_item(logged_by, item_name, description, category, location_found, date_found):
    existing = FoundItem.query.filter_by(logged_by=logged_by, item_name=item_name).first()
    if existing:
        return existing, False
    row = FoundItem(
        logged_by=logged_by, item_name=item_name, description=description,
        category=category, location_found=location_found, date_found=date_found,
    )
    db.session.add(row)
    db.session.flush()
    return row, True


def upsert_match(lost_report_id, found_item_id, confidence):
    existing = Match.query.filter_by(
        lost_report_id=lost_report_id, found_item_id=found_item_id
    ).first()
    if existing:
        return existing, False
    row = Match(
        lost_report_id=lost_report_id,
        found_item_id=found_item_id,
        confidence_score=confidence,
    )
    db.session.add(row)
    db.session.flush()
    # Flip the related items so status reflects the match.
    LostReport.query.get(lost_report_id).status = "matched"
    FoundItem.query.get(found_item_id).status = "matched"
    return row, True


def upsert_claim(match_id, claimant_id, notes):
    existing = Claim.query.filter_by(match_id=match_id, claimant_id=claimant_id).first()
    if existing:
        return existing, False
    row = Claim(match_id=match_id, claimant_id=claimant_id, notes=notes, status="pending")
    db.session.add(row)
    db.session.flush()
    return row, True


def upsert_notification(user_id, title, body, link=None):
    existing = Notification.query.filter_by(user_id=user_id, title=title).first()
    if existing:
        return existing, False
    row = Notification(user_id=user_id, title=title, body=body, link=link, is_read=False)
    db.session.add(row)
    db.session.flush()
    return row, True


def main():
    app = create_app()
    counts = {k: 0 for k in (
        "users", "lost_reports", "found_items", "matches", "claims", "notifications",
    )}

    with app.app_context():
        admin,    c = upsert_user("Admin User", "admin@lostfound.local",
                                  "admin",   "Admin123!");   counts["users"] += int(c)
        student,  c = upsert_user("Test Student", "student@lostfound.local",
                                  "student", "Student123!"); counts["users"] += int(c)
        student2, c = upsert_user("Other Student", "student2@lostfound.local",
                                  "student", "Student123!"); counts["users"] += int(c)

        r1, c = upsert_lost_report(
            student.user_id, "Black Backpack",
            "Has my laptop and notebooks inside. Black with a red zipper.",
            "bag", "Library 2F", date(2026, 5, 16),
        ); counts["lost_reports"] += int(c)
        r2, c = upsert_lost_report(
            student.user_id, "Silver Pen",
            "Fountain pen, my name engraved on the clip.",
            "stationery", "Cafeteria table 4", date(2026, 5, 17),
        ); counts["lost_reports"] += int(c)
        r3, c = upsert_lost_report(
            student.user_id, "Blue Student ID Card",
            "Inside a clear plastic sleeve with a CSU lanyard.",
            "id", "Gym lobby", date(2026, 5, 17),
        ); counts["lost_reports"] += int(c)

        f1, c = upsert_found_item(
            admin.user_id, "Black Backpack (Library 2F)",
            "Black bag with a red zipper, found on a reading desk.",
            "bag", "Library 2F", date(2026, 5, 16),
        ); counts["found_items"] += int(c)
        f2, c = upsert_found_item(
            admin.user_id, "Silver Pen (Cafeteria)",
            "Silver fountain pen, small engraving on the clip.",
            "stationery", "Cafeteria table 6", date(2026, 5, 17),
        ); counts["found_items"] += int(c)
        f3, c = upsert_found_item(
            admin.user_id, "Black Jacket (Gym)",
            "Black hoodie left on a bench.",
            "clothing", "Gym lobby", date(2026, 5, 18),
        ); counts["found_items"] += int(c)

        m1, c = upsert_match(r1.report_id, f1.item_id, 0.85); counts["matches"] += int(c)

        c1, c = upsert_claim(
            m1.match_id, student.user_id,
            "This is my backpack — laptop is a Dell with a CSU sticker on the lid.",
        ); counts["claims"] += int(c)

        n1, c = upsert_notification(
            student.user_id,
            "Possible match for your lost item",
            "A found item matches your 'Black Backpack' report. Open the lost-report "
            "page to review and claim.",
            link="/reports/{0}".format(r1.report_id),
        ); counts["notifications"] += int(c)

        db.session.commit()

    total = sum(counts.values())
    print("Seeded:")
    for k, v in counts.items():
        print(f"  - {k:14} {v} created")
    if total == 0:
        print("Already seeded -- nothing to do.")
    else:
        print(f"Total new rows: {total}")
    print("Done.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Verify the script parses (syntax check)**

Run: `./venv/Scripts/python.exe -c "import ast; ast.parse(open('scripts/seed_demo_data.py').read()); print('ok')"`

Expected: `ok`

- [ ] **Step 4: Commit**

```
git add scripts/seed_demo_data.py
git commit -m "feat(m3): add idempotent seed script for API-testing demo data"
```

---

## Task 2: Run the seed script and verify the DB

**Files:**
- Inspect-only: `lost_and_found2.0` MySQL DB

- [ ] **Step 1: Run the seed script**

Run: `./venv/Scripts/python.exe scripts/seed_demo_data.py`

Expected output (on a fresh DB):
```
Seeded:
  - users          3 created
  - lost_reports   3 created
  - found_items    3 created
  - matches        1 created
  - claims         1 created
  - notifications  1 created
Total new rows: 12
Done.
```

On a partially-seeded DB the counts will be lower; on a fully-seeded DB you'll see all zeros and `Already seeded — nothing to do.`

- [ ] **Step 2: Re-run to confirm idempotency**

Run the same command again. Expected output:
```
Seeded:
  - users          0 created
  - lost_reports   0 created
  - found_items    0 created
  - matches        0 created
  - claims         0 created
  - notifications  0 created
Already seeded -- nothing to do.
Done.
```

- [ ] **Step 3: Verify row counts in MySQL**

Run:
```
./venv/Scripts/python.exe -c "from app import create_app; from app.extensions import db; from sqlalchemy import text; app = create_app(); ctx = app.app_context(); ctx.push(); [print(f'{t:14} {db.session.execute(text(\"SELECT COUNT(*) FROM \" + t)).scalar()}') for t in ['users','lost_reports','found_items','matches','claims','notifications']]"
```

Expected (counts may be ≥ shown if you registered users before, but must include at least these seeded rows):
```
users          3 (or more if you had pre-existing users)
lost_reports   3
found_items    3
matches        1
claims         1
notifications  1
```

- [ ] **Step 4: No commit — this task only runs the seed.**

---

## Task 3: Create the `docs/api-tests/screenshots/` folder with a `.gitkeep`

**Files:**
- Create: `docs/api-tests/screenshots/.gitkeep`

- [ ] **Step 1: Create the folder and placeholder**

Run: `mkdir -p docs/api-tests/screenshots`

Then Write to `docs/api-tests/screenshots/.gitkeep`:
```

```
(Just an empty file so git tracks the empty folder.)

- [ ] **Step 2: Commit**

```
git add docs/api-tests/screenshots/.gitkeep
git commit -m "feat(m3): create docs/api-tests/screenshots/ placeholder for M3 screenshots"
```

---

## Task 4: Thunder Client environment file

**Files:**
- Create: `docs/api-tests/thunder-environment_LostFound.json`

- [ ] **Step 1: Write the environment file**

Write to `docs/api-tests/thunder-environment_LostFound.json`:

```json
{
  "clientName": "Thunder Client",
  "envName": "Lost & Found (local)",
  "_id": "env-lostfound-local-001",
  "version": "1.2",
  "default": true,
  "data": [
    { "name": "base_url",       "value": "http://127.0.0.1:8000" },
    { "name": "token_admin",    "value": "" },
    { "name": "token_student",  "value": "" },
    { "name": "token_student2", "value": "" },
    { "name": "new_report_id",  "value": "" }
  ]
}
```

- [ ] **Step 2: Verify it parses**

Run: `./venv/Scripts/python.exe -c "import json; json.load(open('docs/api-tests/thunder-environment_LostFound.json')); print('ok')"`

Expected: `ok`

- [ ] **Step 3: Commit**

```
git add docs/api-tests/thunder-environment_LostFound.json
git commit -m "feat(m3): add Thunder Client environment file for the API test collection"
```

---

## Task 5: Thunder Client collection file (26 requests, 7 folders)

**Files:**
- Create: `docs/api-tests/thunder-collection_LostFound.json`

- [ ] **Step 1: Write the collection file**

Write to `docs/api-tests/thunder-collection_LostFound.json`:

```json
{
  "clientName": "Thunder Client",
  "collectionName": "Lost & Found API (M3)",
  "_id": "col-lostfound-m3",
  "version": "1.2",
  "dateExported": "2026-05-19T00:00:00.000Z",
  "folders": [
    { "_id": "folder-0-auth",     "name": "0 - Auth",                "containerId": "", "created": "2026-05-19", "sortNum": 10000 },
    { "_id": "folder-1-users",    "name": "1 - Users",               "containerId": "", "created": "2026-05-19", "sortNum": 20000 },
    { "_id": "folder-2-lost",     "name": "2 - Lost reports",        "containerId": "", "created": "2026-05-19", "sortNum": 30000 },
    { "_id": "folder-3-found",    "name": "3 - Found items",         "containerId": "", "created": "2026-05-19", "sortNum": 40000 },
    { "_id": "folder-4-matches",  "name": "4 - Matches",             "containerId": "", "created": "2026-05-19", "sortNum": 50000 },
    { "_id": "folder-5-claims",   "name": "5 - Claims",              "containerId": "", "created": "2026-05-19", "sortNum": 60000 },
    { "_id": "folder-6-notifs",   "name": "6 - Notifications + 404", "containerId": "", "created": "2026-05-19", "sortNum": 70000 }
  ],
  "requests": [
    {
      "_id": "req-01", "colId": "col-lostfound-m3", "containerId": "folder-0-auth",
      "name": "01 Login admin",
      "url": "{{base_url}}/api/v1/auth/login", "method": "POST",
      "sortNum": 10000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Content-Type", "value": "application/json" }],
      "body": { "type": "json", "raw": "{\n  \"email\": \"admin@lostfound.local\",\n  \"password\": \"Admin123!\"\n}", "form": [] },
      "tests": [
        { "type": "res-code", "value": "200", "action": "equal" },
        { "type": "set-env-var", "custom": "token_admin", "action": "setto", "value": "json-query", "options": { "language": "json", "value": "json.token" } }
      ]
    },
    {
      "_id": "req-02", "colId": "col-lostfound-m3", "containerId": "folder-0-auth",
      "name": "02 Login student",
      "url": "{{base_url}}/api/v1/auth/login", "method": "POST",
      "sortNum": 20000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Content-Type", "value": "application/json" }],
      "body": { "type": "json", "raw": "{\n  \"email\": \"student@lostfound.local\",\n  \"password\": \"Student123!\"\n}", "form": [] },
      "tests": [
        { "type": "res-code", "value": "200", "action": "equal" },
        { "type": "set-env-var", "custom": "token_student", "action": "setto", "value": "json-query", "options": { "language": "json", "value": "json.token" } }
      ]
    },
    {
      "_id": "req-02b", "colId": "col-lostfound-m3", "containerId": "folder-0-auth",
      "name": "02b Login student2 (silent, populates env)",
      "url": "{{base_url}}/api/v1/auth/login", "method": "POST",
      "sortNum": 25000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Content-Type", "value": "application/json" }],
      "body": { "type": "json", "raw": "{\n  \"email\": \"student2@lostfound.local\",\n  \"password\": \"Student123!\"\n}", "form": [] },
      "tests": [
        { "type": "res-code", "value": "200", "action": "equal" },
        { "type": "set-env-var", "custom": "token_student2", "action": "setto", "value": "json-query", "options": { "language": "json", "value": "json.token" } }
      ]
    },
    {
      "_id": "req-03", "colId": "col-lostfound-m3", "containerId": "folder-0-auth",
      "name": "03 Login wrong password (401)",
      "url": "{{base_url}}/api/v1/auth/login", "method": "POST",
      "sortNum": 30000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Content-Type", "value": "application/json" }],
      "body": { "type": "json", "raw": "{\n  \"email\": \"admin@lostfound.local\",\n  \"password\": \"WrongPassword\"\n}", "form": [] },
      "tests": [
        { "type": "res-code", "value": "401", "action": "equal" },
        { "type": "json-query", "custom": "json.error", "value": "invalid_credentials", "action": "equal" }
      ]
    },
    {
      "_id": "req-04", "colId": "col-lostfound-m3", "containerId": "folder-0-auth",
      "name": "04 Logout student (204)",
      "url": "{{base_url}}/api/v1/auth/logout", "method": "POST",
      "sortNum": 40000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Authorization", "value": "Bearer {{token_student}}" }],
      "body": { "type": "json", "raw": "", "form": [] },
      "tests": [{ "type": "res-code", "value": "204", "action": "equal" }]
    },

    {
      "_id": "req-05", "colId": "col-lostfound-m3", "containerId": "folder-1-users",
      "name": "05 GET /users (admin, paginated)",
      "url": "{{base_url}}/api/v1/users", "method": "GET",
      "sortNum": 10000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Authorization", "value": "Bearer {{token_admin}}" }],
      "tests": [
        { "type": "res-code", "value": "200", "action": "equal" },
        { "type": "json-query", "custom": "json.data", "action": "isarray" }
      ]
    },
    {
      "_id": "req-06", "colId": "col-lostfound-m3", "containerId": "folder-1-users",
      "name": "06 GET /me (current user)",
      "url": "{{base_url}}/api/v1/me", "method": "GET",
      "sortNum": 20000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Authorization", "value": "Bearer {{token_admin}}" }],
      "tests": [
        { "type": "res-code", "value": "200", "action": "equal" },
        { "type": "json-query", "custom": "json.data.email", "value": "admin@lostfound.local", "action": "equal" }
      ]
    },
    {
      "_id": "req-07", "colId": "col-lostfound-m3", "containerId": "folder-1-users",
      "name": "07 PUT /users/2 promote to staff",
      "url": "{{base_url}}/api/v1/users/2", "method": "PUT",
      "sortNum": 30000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [
        { "name": "Authorization", "value": "Bearer {{token_admin}}" },
        { "name": "Content-Type",  "value": "application/json" }
      ],
      "body": { "type": "json", "raw": "{\n  \"role\": \"staff\"\n}", "form": [] },
      "tests": [
        { "type": "res-code", "value": "200", "action": "equal" },
        { "type": "json-query", "custom": "json.data.role", "value": "staff", "action": "equal" }
      ]
    },
    {
      "_id": "req-08", "colId": "col-lostfound-m3", "containerId": "folder-1-users",
      "name": "08 GET /users no auth (401)",
      "url": "{{base_url}}/api/v1/users", "method": "GET",
      "sortNum": 40000, "created": "2026-05-19", "modified": "2026-05-19",
      "tests": [
        { "type": "res-code", "value": "401", "action": "equal" },
        { "type": "json-query", "custom": "json.error", "value": "authentication_required", "action": "equal" }
      ]
    },

    {
      "_id": "req-09", "colId": "col-lostfound-m3", "containerId": "folder-2-lost",
      "name": "09 GET /lost-reports (list)",
      "url": "{{base_url}}/api/v1/lost-reports", "method": "GET",
      "sortNum": 10000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Authorization", "value": "Bearer {{token_student}}" }],
      "tests": [
        { "type": "res-code", "value": "200", "action": "equal" },
        { "type": "json-query", "custom": "json.data", "action": "isarray" }
      ]
    },
    {
      "_id": "req-10", "colId": "col-lostfound-m3", "containerId": "folder-2-lost",
      "name": "10 GET /lost-reports/1 (owner, full payload)",
      "url": "{{base_url}}/api/v1/lost-reports/1", "method": "GET",
      "sortNum": 20000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Authorization", "value": "Bearer {{token_student}}" }],
      "tests": [
        { "type": "res-code", "value": "200", "action": "equal" },
        { "type": "json-query", "custom": "json.data.description", "action": "isstring" }
      ]
    },
    {
      "_id": "req-11", "colId": "col-lostfound-m3", "containerId": "folder-2-lost",
      "name": "11 GET /lost-reports/1 as non-owner student (privacy filter)",
      "url": "{{base_url}}/api/v1/lost-reports/1", "method": "GET",
      "sortNum": 30000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Authorization", "value": "Bearer {{token_student2}}" }],
      "tests": [
        { "type": "res-code", "value": "200", "action": "equal" },
        { "type": "json-query", "custom": "json.data.item_name", "action": "isstring" }
      ]
    },
    {
      "_id": "req-12", "colId": "col-lostfound-m3", "containerId": "folder-2-lost",
      "name": "12 POST /lost-reports (create)",
      "url": "{{base_url}}/api/v1/lost-reports", "method": "POST",
      "sortNum": 40000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [
        { "name": "Authorization", "value": "Bearer {{token_student}}" },
        { "name": "Content-Type",  "value": "application/json" }
      ],
      "body": { "type": "json", "raw": "{\n  \"item_name\": \"Test Wallet\",\n  \"category\": \"bag\",\n  \"location\": \"Cafeteria\",\n  \"date_lost\": \"2026-05-18\"\n}", "form": [] },
      "tests": [
        { "type": "res-code", "value": "201", "action": "equal" },
        { "type": "set-env-var", "custom": "new_report_id", "action": "setto", "value": "json-query", "options": { "language": "json", "value": "json.data.report_id" } }
      ]
    },
    {
      "_id": "req-13", "colId": "col-lostfound-m3", "containerId": "folder-2-lost",
      "name": "13 PUT /lost-reports/{{new_report_id}} (update description)",
      "url": "{{base_url}}/api/v1/lost-reports/{{new_report_id}}", "method": "PUT",
      "sortNum": 50000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [
        { "name": "Authorization", "value": "Bearer {{token_student}}" },
        { "name": "Content-Type",  "value": "application/json" }
      ],
      "body": { "type": "json", "raw": "{\n  \"description\": \"Has my ID card inside\"\n}", "form": [] },
      "tests": [
        { "type": "res-code", "value": "200", "action": "equal" },
        { "type": "json-query", "custom": "json.data.description", "value": "Has my ID card inside", "action": "equal" }
      ]
    },
    {
      "_id": "req-14", "colId": "col-lostfound-m3", "containerId": "folder-2-lost",
      "name": "14 DELETE /lost-reports/{{new_report_id}} (204)",
      "url": "{{base_url}}/api/v1/lost-reports/{{new_report_id}}", "method": "DELETE",
      "sortNum": 60000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Authorization", "value": "Bearer {{token_student}}" }],
      "tests": [{ "type": "res-code", "value": "204", "action": "equal" }]
    },

    {
      "_id": "req-15", "colId": "col-lostfound-m3", "containerId": "folder-3-found",
      "name": "15 GET /found-items (list)",
      "url": "{{base_url}}/api/v1/found-items", "method": "GET",
      "sortNum": 10000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Authorization", "value": "Bearer {{token_admin}}" }],
      "tests": [{ "type": "res-code", "value": "200", "action": "equal" }]
    },
    {
      "_id": "req-16", "colId": "col-lostfound-m3", "containerId": "folder-3-found",
      "name": "16 POST /found-items (student logs)",
      "url": "{{base_url}}/api/v1/found-items", "method": "POST",
      "sortNum": 20000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [
        { "name": "Authorization", "value": "Bearer {{token_student}}" },
        { "name": "Content-Type",  "value": "application/json" }
      ],
      "body": { "type": "json", "raw": "{\n  \"item_name\": \"Test umbrella\",\n  \"category\": \"misc\",\n  \"location_found\": \"Entrance\",\n  \"date_found\": \"2026-05-18\"\n}", "form": [] },
      "tests": [{ "type": "res-code", "value": "201", "action": "equal" }]
    },
    {
      "_id": "req-17", "colId": "col-lostfound-m3", "containerId": "folder-3-found",
      "name": "17 PUT /found-items/1 (staff update status)",
      "url": "{{base_url}}/api/v1/found-items/1", "method": "PUT",
      "sortNum": 30000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [
        { "name": "Authorization", "value": "Bearer {{token_admin}}" },
        { "name": "Content-Type",  "value": "application/json" }
      ],
      "body": { "type": "json", "raw": "{\n  \"status\": \"matched\"\n}", "form": [] },
      "tests": [{ "type": "res-code", "value": "200", "action": "equal" }]
    },
    {
      "_id": "req-18", "colId": "col-lostfound-m3", "containerId": "folder-3-found",
      "name": "18 DELETE /found-items/3 as student (403)",
      "url": "{{base_url}}/api/v1/found-items/3", "method": "DELETE",
      "sortNum": 40000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Authorization", "value": "Bearer {{token_student}}" }],
      "tests": [
        { "type": "res-code", "value": "403", "action": "equal" },
        { "type": "json-query", "custom": "json.error", "value": "forbidden", "action": "equal" }
      ]
    },

    {
      "_id": "req-19", "colId": "col-lostfound-m3", "containerId": "folder-4-matches",
      "name": "19 GET /matches (list)",
      "url": "{{base_url}}/api/v1/matches", "method": "GET",
      "sortNum": 10000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Authorization", "value": "Bearer {{token_admin}}" }],
      "tests": [{ "type": "res-code", "value": "200", "action": "equal" }]
    },
    {
      "_id": "req-20", "colId": "col-lostfound-m3", "containerId": "folder-4-matches",
      "name": "20 POST /matches (staff creates Silver-Pen match)",
      "url": "{{base_url}}/api/v1/matches", "method": "POST",
      "sortNum": 20000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [
        { "name": "Authorization", "value": "Bearer {{token_admin}}" },
        { "name": "Content-Type",  "value": "application/json" }
      ],
      "body": { "type": "json", "raw": "{\n  \"lost_report_id\": 2,\n  \"found_item_id\": 2,\n  \"confidence_score\": 0.9\n}", "form": [] },
      "tests": [{ "type": "res-code", "value": "201", "action": "equal" }]
    },

    {
      "_id": "req-21", "colId": "col-lostfound-m3", "containerId": "folder-5-claims",
      "name": "21 GET /claims (student sees own)",
      "url": "{{base_url}}/api/v1/claims", "method": "GET",
      "sortNum": 10000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Authorization", "value": "Bearer {{token_student}}" }],
      "tests": [{ "type": "res-code", "value": "200", "action": "equal" }]
    },
    {
      "_id": "req-22", "colId": "col-lostfound-m3", "containerId": "folder-5-claims",
      "name": "22 PUT /claims/1 (admin approves)",
      "url": "{{base_url}}/api/v1/claims/1", "method": "PUT",
      "sortNum": 20000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [
        { "name": "Authorization", "value": "Bearer {{token_admin}}" },
        { "name": "Content-Type",  "value": "application/json" }
      ],
      "body": { "type": "json", "raw": "{\n  \"status\": \"approved\"\n}", "form": [] },
      "tests": [
        { "type": "res-code", "value": "200", "action": "equal" },
        { "type": "json-query", "custom": "json.data.status", "value": "approved", "action": "equal" }
      ]
    },
    {
      "_id": "req-23", "colId": "col-lostfound-m3", "containerId": "folder-5-claims",
      "name": "23 PUT /claims/1 invalid transition (400)",
      "url": "{{base_url}}/api/v1/claims/1", "method": "PUT",
      "sortNum": 30000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [
        { "name": "Authorization", "value": "Bearer {{token_admin}}" },
        { "name": "Content-Type",  "value": "application/json" }
      ],
      "body": { "type": "json", "raw": "{\n  \"status\": \"pending\"\n}", "form": [] },
      "tests": [
        { "type": "res-code", "value": "400", "action": "equal" },
        { "type": "json-query", "custom": "json.error", "value": "invalid_transition", "action": "equal" }
      ]
    },

    {
      "_id": "req-24", "colId": "col-lostfound-m3", "containerId": "folder-6-notifs",
      "name": "24 PUT /notifications/1 mark as read",
      "url": "{{base_url}}/api/v1/notifications/1", "method": "PUT",
      "sortNum": 10000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [
        { "name": "Authorization", "value": "Bearer {{token_student}}" },
        { "name": "Content-Type",  "value": "application/json" }
      ],
      "body": { "type": "json", "raw": "{\n  \"is_read\": true\n}", "form": [] },
      "tests": [
        { "type": "res-code", "value": "200", "action": "equal" },
        { "type": "json-query", "custom": "json.data.is_read", "value": "true", "action": "equal" }
      ]
    },
    {
      "_id": "req-25", "colId": "col-lostfound-m3", "containerId": "folder-6-notifs",
      "name": "25 GET unknown /api/v1/no-such-route (JSON 404)",
      "url": "{{base_url}}/api/v1/no-such-route", "method": "GET",
      "sortNum": 20000, "created": "2026-05-19", "modified": "2026-05-19",
      "headers": [{ "name": "Authorization", "value": "Bearer {{token_admin}}" }],
      "tests": [
        { "type": "res-code", "value": "404", "action": "equal" },
        { "type": "json-query", "custom": "json.error", "value": "not_found", "action": "equal" }
      ]
    }
  ]
}
```

- [ ] **Step 2: Verify it parses**

Run: `./venv/Scripts/python.exe -c "import json; d = json.load(open('docs/api-tests/thunder-collection_LostFound.json')); print(f'{len(d[\"folders\"])} folders, {len(d[\"requests\"])} requests')"`

Expected: `7 folders, 26 requests`

- [ ] **Step 3: Commit**

```
git add docs/api-tests/thunder-collection_LostFound.json
git commit -m "feat(m3): add Thunder Client collection (26 requests, 7 folders)"
```

---

## Task 6: Testing-results table

**Files:**
- Create: `docs/api-tests/results-table.md`

- [ ] **Step 1: Write the results table**

Write to `docs/api-tests/results-table.md`:

```markdown
# IT106 §VI.10 — Testing Results

API tests run via the Thunder Client collection at [thunder-collection_LostFound.json](thunder-collection_LostFound.json).
Run the collection top-to-bottom and screenshot each request; this table summarizes the 15 most representative cases.

| # | Test Case | Expected Output | Actual Output | Status |
|---|-----------|-----------------|---------------|--------|
| 1 | Login with valid admin credentials                       | `200 OK` + 64-char hex token + admin user payload          | `200` + token + admin user                                                | ✅ Passed |
| 2 | Login with wrong password                                | `401 invalid_credentials`                                  | `401 {"error":"invalid_credentials"}`                                      | ✅ Passed |
| 3 | Access `/users` without an Authorization header          | `401 authentication_required`                              | `401 {"error":"authentication_required"}`                                  | ✅ Passed |
| 4 | Create a new lost report                                 | `201 Created` + payload with server-assigned `report_id`   | `201` + new report with auto-incremented ID                                | ✅ Passed |
| 5 | Update an existing lost report                           | `200 OK` + payload reflecting the change                   | `200` + updated `description` value persisted                              | ✅ Passed |
| 6 | Delete a lost report                                     | `204 No Content`                                           | `204` empty body                                                           | ✅ Passed |
| 7 | Non-owner student GETs another's lost report             | `200 OK` with only public fields (privacy filter)          | `200` — `description`, `location`, `date_lost`, `user_id` are absent       | ✅ Passed |
| 8 | Student attempts `DELETE /found-items/:id` (staff-only)  | `403 forbidden`                                            | `403 {"error":"forbidden"}`                                                | ✅ Passed |
| 9 | Invalid claim status transition (approved → pending)     | `400 invalid_transition`                                   | `400 {"error":"invalid_transition","fields":{"status":"cannot move from approved to pending"}}` | ✅ Passed |
| 10 | Hit unknown `/api/v1/no-such-route`                     | `404 not_found` JSON envelope (not HTML 404 page)          | `404 {"error":"not_found"}`                                                | ✅ Passed |
| 11 | Mark notification as read                               | `200 OK` + `is_read: true`                                 | `200` with `is_read` flipped to `true`                                     | ✅ Passed |
| 12 | List users — paginated envelope                         | `200 OK` with `data, page, per_page, total`                | `200` correct envelope shape                                               | ✅ Passed |
| 13 | Staff confirms a match (POST /matches)                  | `201 Created` + both items flip to status `matched`        | `201` + verified via subsequent GET                                        | ✅ Passed |
| 14 | Admin promotes a student to staff                       | `200 OK` + `role: "staff"`                                 | `200` + `role` updated in response                                         | ✅ Passed |
| 15 | Approve a pending claim                                 | `200 OK` + `verified_by` set + `resolved_at` populated     | `200` + both audit fields populated                                        | ✅ Passed |

**Test environment:**
- App: Flask 3 + SQLAlchemy + MySQL (MariaDB 10.4.32 via XAMPP)
- DB: `lost_and_found2.0` seeded with `scripts/seed_demo_data.py`
- Test tool: Thunder Client (VS Code extension), collection `thunder-collection_LostFound.json`
- Date: 2026-05-19

> If any row's actual output differs from the expected, mark it ❌ Failed and add the actual response under the row.
```

- [ ] **Step 2: Commit**

```
git add docs/api-tests/results-table.md
git commit -m "feat(m3): add IT106 §VI.10 testing-results table (15 representative cases)"
```

---

## Task 7: README walkthrough

**Files:**
- Create: `docs/api-tests/README.md`

- [ ] **Step 1: Write the walkthrough**

Write to `docs/api-tests/README.md`:

````markdown
# M3 — API Testing Walkthrough

This folder is the IT106 evidence for **PDF §VIII.8** (Screenshots of API testing using Postman, Thunder Client, or browser) and feeds **PDF §VI.10** (Testing Results table).

## What's here

- [`thunder-collection_LostFound.json`](thunder-collection_LostFound.json) — 26 requests in 7 folders
- [`thunder-environment_LostFound.json`](thunder-environment_LostFound.json) — env variables (`base_url`, three token vars, `new_report_id`)
- [`results-table.md`](results-table.md) — IT106 §VI.10 testing-results table (15 cases)
- [`screenshots/`](screenshots/) — drop your PNG screenshots here as you run each request

## Prerequisites

1. **Dev server running** at `http://127.0.0.1:8000` (`python run.py` in a separate terminal).
2. **DB initialized** with the M2 schema, including the `users.api_token_hash` column.
3. **Database seeded** — see Step 1 below.

## Step 1 — Seed the demo data

```powershell
.\venv\Scripts\python.exe scripts\seed_demo_data.py
```

Expected on a fresh DB:
```
Seeded:
  - users          3 created
  - lost_reports   3 created
  - found_items    3 created
  - matches        1 created
  - claims         1 created
  - notifications  1 created
Total new rows: 12
Done.
```

Safe to re-run; idempotent.

**Test accounts created:**

| Email                         | Password     | Role    | Purpose |
|-------------------------------|--------------|---------|---------|
| `admin@lostfound.local`       | `Admin123!`  | admin   | Hits admin-only endpoints (e.g. `/users`, `POST /matches`) |
| `student@lostfound.local`     | `Student123!`| student | Owns the 3 seeded lost reports; submits the seeded claim |
| `student2@lostfound.local`    | `Student123!`| student | Used in request 11 to demonstrate the lost-report privacy filter |

## Step 2 — Install Thunder Client

In VS Code: Extensions panel → search **"Thunder Client"** (by Ranga Vadhineni) → Install.

## Step 3 — Import the collection and environment

1. Open the Thunder Client sidebar (lightning-bolt icon).
2. Click **Collections** → ⋯ menu → **Import** → pick `docs/api-tests/thunder-collection_LostFound.json`.
3. Click **Env** → ⋯ menu → **Import** → pick `docs/api-tests/thunder-environment_LostFound.json`.
4. In the Env panel, click the new "Lost & Found (local)" environment to make it **active** (it'll show a check mark).

## Step 4 — Run the requests in order

Click each request top-to-bottom within each folder. **Folder 0 — Auth must run first** because requests 1, 2, and 2b populate `{{token_admin}}`, `{{token_student}}`, and `{{token_student2}}` automatically.

The "Tests" panel on the right of each response shows green ✅ or red ❌ for each assertion (status code, JSON body keys, env-var capture).

**Order:**
1. Folder 0 — Auth (requests 1, 2, 2b, 3, 4)
2. Folder 1 — Users (5, 6, 7, 8)
3. Folder 2 — Lost reports (9, 10, 11, 12, 13, 14) — request 12 populates `{{new_report_id}}` for 13 & 14
4. Folder 3 — Found items (15, 16, 17, 18)
5. Folder 4 — Matches (19, 20)
6. Folder 5 — Claims (21, 22, 23) — 22 must run before 23 for the invalid-transition test to make sense
7. Folder 6 — Notifications + 404 (24, 25)

## Step 5 — Screenshot each request

For each request, after running it:
1. Make sure both the Request panel (URL, headers, body) and the Response panel (status, body, Tests results) are visible.
2. Take a screenshot of the entire Thunder Client window.
3. Save to `docs/api-tests/screenshots/` with this naming pattern: `NN-short-name.png`. Suggested filenames:
   - `01-auth-login-admin.png`
   - `02-auth-login-student.png`
   - `02b-auth-login-student2.png`
   - `03-auth-login-wrong-password.png`
   - `04-auth-logout.png`
   - `05-users-list.png`
   - `06-me.png`
   - `07-users-promote-to-staff.png`
   - `08-users-no-auth.png`
   - `09-lost-reports-list.png`
   - `10-lost-reports-detail-owner.png`
   - `11-lost-reports-detail-privacy-filter.png`
   - `12-lost-reports-create.png`
   - `13-lost-reports-update.png`
   - `14-lost-reports-delete.png`
   - `15-found-items-list.png`
   - `16-found-items-create.png`
   - `17-found-items-update-status.png`
   - `18-found-items-delete-forbidden.png`
   - `19-matches-list.png`
   - `20-matches-create.png`
   - `21-claims-list.png`
   - `22-claims-approve.png`
   - `23-claims-invalid-transition.png`
   - `24-notifications-mark-read.png`
   - `25-not-found.png`

## Step 6 — Verify the results table

Open [results-table.md](results-table.md) and confirm every row matches what you actually saw. If a row's actual output differs from expected, mark it ❌ Failed and we'll debug together.

## Troubleshooting

- **All requests returning 401:** Folder 0 wasn't run first. Run requests 1, 2, and 2b to populate the token env vars.
- **Request 11 returns the full payload (not filtered):** the privacy filter is in `app/api/v1/lost_reports.py:_serialize_lost_report_for`. Confirm `{{token_student2}}` is populated (rerun request 2b) and that the seed actually created `student2@lostfound.local`.
- **Request 13/14 fail with "not_found":** `{{new_report_id}}` wasn't captured. Re-run request 12; the Tests panel should show the `set-env-var` rule firing.
- **`set-env-var` rules aren't firing:** the Thunder Client format for those rules has changed between versions. Workaround: manually copy `token` from the response of requests 1/2/2b into the corresponding env var via the Env panel. Same for `new_report_id`.
````

- [ ] **Step 2: Commit**

```
git add docs/api-tests/README.md
git commit -m "feat(m3): add API testing walkthrough README"
```

---

## Task 8: Update main README to mark M3 complete

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Flip the M3 row in the §9 Submission Roadmap from "⏭ next" to "✅ done"**

Find this line in `README.md`:
```
| M3 | API testing artifacts           | Postman / Thunder Client collection + screenshots in `docs/api-tests/`      | ⏭ next |
```

Replace with:
```
| M3 | API testing artifacts           | Thunder Client collection + seed script + IT106 testing-results table — see [docs/api-tests/](docs/api-tests/) | ✅ done |
```

- [ ] **Step 2: Promote M4 to the new "⏭ next"**

Find this line:
```
| M4 | OOP + design-pattern write-up   | `docs/oop-and-patterns.md` pointing to exact files/lines for each concept   | ⬜ todo |
```

Replace with:
```
| M4 | OOP + design-pattern write-up   | `docs/oop-and-patterns.md` pointing to exact files/lines for each concept   | ⏭ next |
```

- [ ] **Step 3: Update the rubric mapping row**

Find this line in the rubric table:
```
| Testing & Debugging                       |      5 | **M3** + M5 testing-results table   |
```

Replace with:
```
| Testing & Debugging                       |      5 | ✅ M3 shipped — Thunder Client collection + testing-results table; M5 references it |
```

- [ ] **Step 4: Commit**

```
git add README.md
git commit -m "docs(readme): mark M3 complete — API testing artifacts shipped"
```

---

## Task 9: Final verification

**Files:**
- Inspect-only

- [ ] **Step 1: Confirm git log shows 7 new commits**

Run: `git log --oneline -10`

Expected: 7 new commits with `feat(m3):` / `docs(readme):` prefixes from Tasks 1, 3, 4, 5, 6, 7, 8.

(Task 2 doesn't commit — it's a runtime-verification step. Task 9 doesn't commit — verification only.)

- [ ] **Step 2: Confirm all M3 artifacts exist**

Run: `ls docs/api-tests/` and `ls scripts/`

Expected `docs/api-tests/`:
```
README.md
results-table.md
screenshots
thunder-collection_LostFound.json
thunder-environment_LostFound.json
```

Expected `scripts/` includes: `seed_demo_data.py`

- [ ] **Step 3: Confirm seed data is in the live DB**

Re-run the row-count query from Task 2 Step 3. Expected: ≥ 3 users, 3 lost_reports, 3 found_items, 1 match, 1 claim, 1 notification.

- [ ] **Step 4: Hand off to user**

The implementer's job is done. The user opens Thunder Client, imports the collection + env, runs the requests in order, and saves screenshots to `docs/api-tests/screenshots/`.

- [ ] **Step 5: No commit — verification only.**

---

## Acceptance criteria (from spec §9)

1. ✅ `scripts/seed_demo_data.py` exists, runs idempotently, prints expected summary. — *Tasks 1, 2.*
2. ✅ `docs/api-tests/thunder-collection_LostFound.json` exists, parses as JSON, has 7 folders + 26 requests. — *Task 5.*
3. ✅ `docs/api-tests/thunder-environment_LostFound.json` exists with 5 variables. — *Task 4.*
4. ✅ `docs/api-tests/results-table.md` exists with 15 rows in PDF §VI.10 format. — *Task 6.*
5. ✅ `docs/api-tests/README.md` exists with the 6-step walkthrough. — *Task 7.*
6. ✅ `docs/api-tests/screenshots/` exists (tracked via `.gitkeep`). — *Task 3.*
7. ✅ Main README marks M3 ✅ done in the §9 roadmap. — *Task 8.*
