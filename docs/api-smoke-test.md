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
