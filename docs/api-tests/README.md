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
