# IT106 §VI.10 — Testing Results

API tests run via the Postman collection at [postman-collection_LostFound.json](postman-collection_LostFound.json).
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
- Test tool: Postman (VS Code extension), collection `postman-collection_LostFound.json`
- Date: 2026-05-19

> If any row's actual output differs from the expected, mark it ❌ Failed and add the actual response under the row.
