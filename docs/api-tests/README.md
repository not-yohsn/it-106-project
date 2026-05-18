# M3 — API Testing Walkthrough

This folder is the IT106 evidence for **PDF §VIII.8** (Screenshots of API testing using Postman, Thunder Client, or browser) and feeds **PDF §VI.10** (Testing Results table).

## What's here

- [`postman-collection_LostFound.json`](postman-collection_LostFound.json) — 25 requests in 7 folders (Postman v2.1.0 schema)
- [`postman-environment_LostFound.json`](postman-environment_LostFound.json) — env variables (`base_url`, three token vars, `new_report_id`)
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

## Step 2 — Install the Postman extension

In VS Code: Extensions panel → search **"Postman"** (by Postman Inc.) → Install. Sign in with a free Postman account when prompted (the extension requires it to sync workspaces).

## Step 3 — Import the collection and environment

1. Open the Postman sidebar (the orange Postman icon in the VS Code activity bar).
2. **Collections** tab → **Import** button → pick `docs/api-tests/postman-collection_LostFound.json`.
3. **Environments** tab → **Import** → pick `docs/api-tests/postman-environment_LostFound.json`.
4. In the top-right environment dropdown of any request tab, select **"Lost & Found (local)"** so the `{{base_url}}` and token variables resolve.

## Step 4 — Run the requests in order

Click each request top-to-bottom within each folder. **Folder 0 — Auth must run first** because requests 01, 02, and 02b populate `{{token_admin}}`, `{{token_student}}`, and `{{token_student2}}` automatically via their **Tests** scripts (`pm.environment.set(...)`).

After running each request, the **Test Results** tab (next to "Body" / "Headers" in the response panel) shows green checks ✅ or red Xs ❌ for each assertion.

**Order:**
1. Folder 0 — Auth (01, 02, 02b, 03, 04)
2. Folder 1 — Users (05, 06, 07, 08)
3. Folder 2 — Lost reports (09, 10, 11, 12, 13, 14) — request 12 populates `{{new_report_id}}` for 13 & 14
4. Folder 3 — Found items (15, 16, 17, 18)
5. Folder 4 — Matches (19, 20)
6. Folder 5 — Claims (21, 22, 23) — 22 must run before 23 for the invalid-transition test to make sense
7. Folder 6 — Notifications + 404 (24, 25)

## Step 5 — Screenshot each request

For each request, after running it:
1. Make sure both the **Request** panel (URL, headers, body) and the **Response** panel (status, body, Test Results) are visible.
2. Take a screenshot of the entire Postman window.
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

- **All requests returning 401:** Folder 0 wasn't run first. Run requests 01, 02, and 02b to populate the token env vars. Open the **Environment quick-look** (eye icon next to the env dropdown) to confirm the tokens are filled in.
- **Tokens still empty after running login requests:** Open the **Test Results** tab on the login response and check that the `pm.environment.set(...)` assertion ran without error. If the env dropdown wasn't set to "Lost & Found (local)", the value silently went to globals instead — fix the env selector and re-run.
- **Request 11 still returns the full payload (description visible):** the privacy filter is in `app/api/v1/lost_reports.py:_serialize_lost_report_for`. Confirm `{{token_student2}}` is populated (rerun request 02b) and that the seed actually created `student2@lostfound.local`.
- **Request 13/14 fail with "not_found":** `{{new_report_id}}` wasn't captured. Re-run request 12; the Test Results tab should show `report_id captured` as green.
- **Variables not substituting (`{{...}}` shows up literally in the request):** the environment isn't active. Use the top-right environment dropdown on any request tab to pick "Lost & Found (local)".
