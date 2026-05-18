# M3 — API Testing Artifacts (Thunder Client) — Design Spec

**Date:** 2026-05-19
**Milestone:** M3 — API testing artifacts (PDF §VIII.8: "Screenshots of API testing using Postman, Thunder Client, or browser"; ~5 rubric points for Testing & Debugging; evidence row for the M5 testing-results table).
**Goal:** Produce a Thunder Client collection of ~25 representative requests against `/api/v1/*`, an idempotent seed script to populate the DB with realistic demo data, an IT106-format testing-results table, and a README walkthrough — so the user can import → click through → screenshot the evidence required for the IT106 submission.

---

## 1. Why this milestone

The PDF requires testing screenshots (§VIII.8) and a testing-results table (§VI.10). The system currently has no formal test artifacts — only the informal `docs/api-smoke-test.md` cheatsheet from M2.

M3 produces:
- A reproducible test collection any grader can import
- A seed script so the responses are meaningful (not all empty arrays)
- A formatted testing-results table that drops straight into M5
- Screenshots that go straight into M6's `docs/screenshots/` folder

## 2. Scope

**In scope:**
- One idempotent seed script: `scripts/seed_demo_data.py`
- Thunder Client collection: `docs/api-tests/thunder-collection_LostFound.json`
- Thunder Client environment: `docs/api-tests/thunder-environment_LostFound.json`
- IT106-format testing-results table: `docs/api-tests/results-table.md`
- User-facing README walkthrough: `docs/api-tests/README.md`
- Empty `docs/api-tests/screenshots/` folder (populated by the user manually after import)

**Out of scope:**
- Postman alternative format (user picked Thunder Client only)
- pytest / automated unit tests (deferred; M3 is explicitly about manual API testing for the rubric)
- Continuous testing / CI integration
- Load testing, performance testing
- Tests for the HTML routes (the API is the audited surface; the HTML routes have manual UI verification via M6 screenshots)

## 3. Tech and dependencies

- **No new Python packages.** The seed script uses Flask's existing app context + SQLAlchemy.
- **Thunder Client** = a VS Code extension. User installs it separately (one click in the Extensions panel). The collection file is plain JSON.

## 4. File layout

```
scripts/
└── seed_demo_data.py                       # Idempotent seed; run with `python scripts/seed_demo_data.py`

docs/api-tests/
├── README.md                                # User walkthrough — import, run, screenshot
├── thunder-collection_LostFound.json        # 25 requests in 7 folders
├── thunder-environment_LostFound.json       # base_url + token vars
├── results-table.md                         # IT106 §VI.10 testing-results table (15 rows)
└── screenshots/                             # User drops screenshots here (.gitkeep to track)
    └── .gitkeep
```

## 5. Seed script (`scripts/seed_demo_data.py`)

### 5.1 What it creates

| Resource | Count | Notes |
|----------|------:|-------|
| users    | 3 | `admin@lostfound.local` / `Admin123!` (role=admin); `student@lostfound.local` / `Student123!` (role=student); `student2@lostfound.local` / `Student123!` (role=student, used to demonstrate the lost-report privacy filter from a non-owner perspective) |
| finders  | 0 | None — found items are logged by the admin user |
| lost_reports | 3 | All owned by the student user. Item names: "Black Backpack", "Silver Pen", "Blue Student ID Card". Categories: bag, electronics/pen, id. |
| found_items | 3 | All logged by admin. Names: "Black Backpack (Library 2F)", "Silver Pen (Cafeteria)", "Black Jacket (Gym)". |
| matches | 1 | "Black Backpack" lost ↔ "Black Backpack (Library 2F)" found. Confidence 0.85. Side effect: both items flip to status=`matched`. |
| claims | 1 | Student claims the matched item. Status=`pending`. |
| notifications | 1 | To the student: title="Possible match for your lost item", body="A found item matches your 'Black Backpack' report." |

### 5.2 Idempotency

Every insert checks `Model.query.filter_by(<unique-key>).first()` first:
- Users by email
- Lost reports / found items by `(user_id, item_name)` / `(logged_by, item_name)` composite
- Match by `(lost_report_id, found_item_id)`
- Claim by `(match_id, claimant_id)`
- Notification by `(user_id, title)`

If everything already exists, the script prints `Already seeded — nothing to do.` and exits 0.

### 5.3 Output

```
Seeded:
  - users:         3 (2 created, 1 already existed)
  - lost_reports:  3 (created)
  - found_items:   3 (created)
  - matches:       1 (created)
  - claims:        1 (created)
  - notifications: 1 (created)
Done.
```

The script uses `print()` (not logging) so the user sees output directly when running interactively. Exit code 0 on success, non-zero on error.

## 6. Thunder Client collection (`thunder-collection_LostFound.json`)

### 6.1 Folder structure (7 folders, 25 requests)

| Folder | Requests | Cumulative |
|--------|---------:|-----------:|
| 0 — Auth | 4 | 4 |
| 1 — Users | 4 | 8 |
| 2 — Lost reports | 6 | 14 |
| 3 — Found items | 4 | 18 |
| 4 — Matches | 2 | 20 |
| 5 — Claims | 3 | 23 |
| 6 — Notifications + 404 | 2 | 25 |

### 6.2 Full request list

**📁 0 — Auth**
1. `POST {{base_url}}/api/v1/auth/login` — admin (body: `{"email":"admin@lostfound.local","password":"Admin123!"}`) → expects 200; test script writes `response.token` to `{{token_admin}}`.
2. `POST .../auth/login` — student → expects 200; writes `{{token_student}}`.
2b. `POST .../auth/login` — student2 (body: `{"email":"student2@lostfound.local","password":"Student123!"}`) → expects 200; writes `{{token_student2}}`. *(Login is silently captured; not numbered separately because the testing-results table treats requests 1 and 2 as representative of "log in with valid credentials".)*
3. `POST .../auth/login` — wrong password (`Admin123WRONG`) → expects 401 + `{"error":"invalid_credentials"}`.
4. `POST .../auth/logout` (Bearer `{{token_student}}`) → expects 204.

**📁 1 — Users (admin scope)**
5. `GET .../users` (Bearer `{{token_admin}}`) → expects 200 + paginated envelope.
6. `GET .../me` (Bearer `{{token_admin}}`) → expects 200 + admin user payload.
7. `PUT .../users/2` (Bearer `{{token_admin}}`, body: `{"role":"staff"}`) → expects 200 + updated role.
8. `GET .../users` (no Authorization header) → expects 401 + `{"error":"authentication_required"}`.

**📁 2 — Lost reports**
9. `GET .../lost-reports` (Bearer `{{token_student}}`) → expects 200 + list, all 3 seeded reports visible.
10. `GET .../lost-reports/1` (Bearer `{{token_student}}`) → expects 200 + full payload (student is owner of report 1).
11. `GET .../lost-reports/1` (Bearer `{{token_student2}}`) → expects 200 + **privacy-filtered** payload: only `report_id`, `item_name`, `category`, `photo_path`, `created_at`, `status` (no `description`, `location`, `date_lost`, `user_id`). Demonstrates the §6.1 privacy rule from the M2 spec — student2 is not the owner of report 1 and not staff.
12. `POST .../lost-reports` (Bearer `{{token_student}}`, body: `{"item_name":"Test Wallet","category":"bag","location":"Cafeteria","date_lost":"2026-05-18"}`) → expects 201 + new report. Test script writes `response.data.report_id` to `{{new_report_id}}`.
13. `PUT .../lost-reports/{{new_report_id}}` (Bearer `{{token_student}}`, body: `{"description":"Has my ID card inside"}`) → expects 200 + description updated.
14. `DELETE .../lost-reports/{{new_report_id}}` (Bearer `{{token_student}}`) → expects 204.

**📁 3 — Found items**
15. `GET .../found-items` (Bearer `{{token_admin}}`) → expects 200 + 3 seeded found items.
16. `POST .../found-items` (Bearer `{{token_student}}`, body: `{"item_name":"Test umbrella","category":"misc","location_found":"Entrance","date_found":"2026-05-18"}`) → expects 201.
17. `PUT .../found-items/1` (Bearer `{{token_admin}}`, body: `{"status":"matched"}`) → expects 200 (idempotent since seed already set status to matched, but the endpoint accepts the same value).
18. `DELETE .../found-items/3` (Bearer `{{token_student}}`) → expects 403 + `{"error":"forbidden"}` (students cannot DELETE found items).

**📁 4 — Matches**
19. `GET .../matches` (Bearer `{{token_admin}}`) → expects 200 + the 1 seeded match.
20. `POST .../matches` (Bearer `{{token_admin}}`, body: `{"lost_report_id":2,"found_item_id":2,"confidence_score":0.9}`) → expects 201 + new match created for Silver Pen.

**📁 5 — Claims**
21. `GET .../claims` (Bearer `{{token_student}}`) → expects 200 + only the student's own claim (seeded claim_id=1).
22. `PUT .../claims/1` (Bearer `{{token_admin}}`, body: `{"status":"approved"}`) → expects 200 + status=approved, `verified_by` set to admin user_id, `resolved_at` populated.
23. `PUT .../claims/1` (Bearer `{{token_admin}}`, body: `{"status":"pending"}`) → expects 400 + `{"error":"invalid_transition","fields":{"status":"cannot move from approved to pending"}}`.

**📁 6 — Notifications + 404**
24. `PUT .../notifications/1` (Bearer `{{token_student}}`, body: `{"is_read":true}`) → expects 200 + `is_read: true`.
25. `GET .../no-such-route` (Bearer `{{token_admin}}`) → expects 404 + `{"error":"not_found"}` (verifies JSON 404 handler, not HTML 404 page).

### 6.3 Environment variables (`thunder-environment_LostFound.json`)

| Variable | Default value |
|----------|---------------|
| `base_url` | `http://127.0.0.1:8000` |
| `token_admin` | (empty — populated by request 1's test script) |
| `token_student` | (empty — populated by request 2) |
| `token_student2` | (empty — populated by a new request 2b: `POST /auth/login` for `student2@lostfound.local`) |
| `new_report_id` | (empty — populated by request 12) |

### 6.4 Test scripts (Thunder Client's "Tests" tab)

Thunder Client supports JSON-based response assertions. Each request includes the relevant tests:

- Status code assertion (e.g., `"res-code": 200`)
- JSON body key/value checks (e.g., `"json-query": "$.data.report_id", "exists": true`)
- For login requests: `setEnv` rule writing `response.token` → `{{token_admin}}` or `{{token_student}}`
- For request 12 (POST lost-report): `setEnv` rule writing `response.data.report_id` → `{{new_report_id}}`

These tests display ✅ / ❌ in Thunder Client's response panel — visible in every screenshot.

## 7. Testing-results table (`results-table.md`)

15 rows in the PDF §VI.10 format (Test Case | Expected Output | Actual Output | Status). The 15 rows are a representative subset of the 25 requests — duplicate / similar tests (e.g., login admin vs login student) are consolidated.

Each row reflects what the user will actually see when they run the corresponding request. The file is structured so the user can mark a row as ❌ Failed if their actual output differs.

## 8. README walkthrough (`docs/api-tests/README.md`)

User-facing markdown document covering:

1. **Prerequisites** — Dev server running at `http://127.0.0.1:8000`; the `lost_and_found2.0` database initialized with the schema; the `ALTER TABLE users ADD COLUMN api_token_hash …` migration already applied (per M2 spec).
2. **Step 1: Seed the database** — `python scripts/seed_demo_data.py`. Verify the output matches the expected line counts.
3. **Step 2: Install Thunder Client** — VS Code → Extensions tab → search "Thunder Client" → Install (publisher: Ranga Vadhineni).
4. **Step 3: Import collection + environment** — Thunder Client sidebar → Collections → ⋯ menu → Import. Pick `thunder-collection_LostFound.json`. Repeat for `thunder-environment_LostFound.json`. Set the environment as active.
5. **Step 4: Run requests in order** — Click each folder top-to-bottom. Auth folder MUST go first (it populates the token env vars). Each request shows pass/fail in the test results panel.
6. **Step 5: Screenshot each request** — For each request, take a screenshot showing the request configuration on the left and the response panel on the right with the test-result badges visible. Save as `docs/api-tests/screenshots/<NN>-<short-name>.png`. Suggested naming:
   - `01-auth-login-admin.png`
   - `02-auth-login-student.png`
   - `03-auth-login-wrong-password.png`
   - `04-auth-logout.png`
   - `05-users-list.png` … through `25-not-found.png`.
7. **Step 6: Verify the results table** — Open `docs/api-tests/results-table.md` and confirm every row matches your actual responses. If any row differs, mark it ❌ and we debug.

## 9. Acceptance criteria

M3 is complete when:

1. `scripts/seed_demo_data.py` exists, runs successfully against the live DB, is idempotent, and prints the expected summary.
2. `docs/api-tests/thunder-collection_LostFound.json` exists, imports cleanly into Thunder Client, contains 25 requests in 7 folders matching §6.2.
3. `docs/api-tests/thunder-environment_LostFound.json` exists with the 4 variables in §6.3.
4. `docs/api-tests/results-table.md` exists with the 15 rows in PDF §VI.10 format.
5. `docs/api-tests/README.md` exists with the 6-step walkthrough.
6. `docs/api-tests/screenshots/` folder exists (with a `.gitkeep` so git tracks it) for the user to populate after running the collection.
7. The README mentions M3 as ✅ done in the §9 roadmap (per the standing memory rule).

## 10. What this unblocks

- **M5 (final-documentation.md):** §VI.8 "API Documentation" table lifts directly from this collection; §VI.10 "Testing Results" lifts directly from `results-table.md`.
- **M6 (system screenshots):** The API-test screenshots required by PDF §VI.9 are produced by following this milestone's walkthrough.
- **Rubric "Testing & Debugging" (5 pts):** evidence is on disk.
- **Defense (M7):** clean talking point — "I built a 25-request test collection covering every HTTP verb, every resource, and the auth/permission/validation error envelopes. Here are the test results, all green."
