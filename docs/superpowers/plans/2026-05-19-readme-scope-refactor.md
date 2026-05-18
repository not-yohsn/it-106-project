# README Scope Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Insert four new PDF §VI-aligned sections (Background, Objectives, Scope and Limitations, System Architecture) at the top of `README.md`, renumber the existing 11 sections, fix one stale internal reference, and add a redirect note to `ScopeProject.md` — so the README becomes the single PDF §VI-aligned scope-of-record.

**Architecture:** Documentation-only refactor — no code changes. All edits are confined to two files (`README.md`, `ScopeProject.md`). Verification is by re-reading the rendered file content and grepping for stale references. Each task ends with a verification step and a focused commit.

**Tech Stack:** Markdown (GitHub-flavored), git. No tests to run, no build to break.

**Spec:** [docs/superpowers/specs/2026-05-19-readme-scope-refactor-design.md](../specs/2026-05-19-readme-scope-refactor-design.md)

---

## Task 1: Audit and baseline

**Files:**
- Read: `README.md`
- Read: `ScopeProject.md`

- [ ] **Step 1: Confirm the baseline structure of README.md**

Run: `grep -nE "^## " "README.md"`

Expected output (exactly 11 top-level sections, currently numbered 1–11):
```
10:## 1. IT106 Course Mapping
29:## 2. Minimum Feature Compliance (PDF §V)
44:## 3. Features (current)
58:## 4. Tech Stack (matches PDF §IV — Option C: Hybrid)
77:## 5. Submission Roadmap to May 25, 2026
108:## 6. Quick Start (local)
141:## 7. Deploy to Render + TiDB Cloud
163:## 8. User Roles
180:## 9. Project Structure
226:## 10. Data Model
236:## 11. Documentation
```

(Line numbers may drift slightly — what matters is that there are exactly 11 sections numbered 1 through 11 in this exact order.)

- [ ] **Step 2: Confirm the only stale internal reference is on line 40**

Run: `grep -nE "§[0-9]+" "README.md"`

Expected output:
```
40:| At least one design pattern                                    | ✅ done        | MVC + Application Factory (see §1 above)                |
232:See [ScopeProject.md §6](ScopeProject.md) for the full relationship breakdown.
```

Line 40 references README's own §1 (currently "IT106 Course Mapping") — this **will need to change to §5** after renumber. Line 232 references ScopeProject.md §6 (an external file) — unaffected.

- [ ] **Step 3: Confirm there are no anchor links targeting README's numbered sections**

Run: `grep -nE "\]\(#[0-9]" "README.md"`

Expected output: (empty — no anchor links to numbered sections exist, so renumbering won't break any link)

If any output appears, list them; they will need updating in Task 4 along with the §1 reference.

- [ ] **Step 4: Confirm ScopeProject.md exists and capture its current opening lines**

Run: `head -5 "ScopeProject.md"`

Expected output (the first H1 followed by the source-brief blockquote):
```
# ScopeProject — Lost and Found Tracking System

> Source brief: [LOST-AND-FOUND.pdf](LOST-AND-FOUND.pdf)
> Existing prototypes: [prototype.html](prototype.html) (ERD), [chatbot_prototype.html](chatbot_prototype.html)

```

- [ ] **Step 5: No commit for this task — audit only**

If any expected output above does not match, STOP and report. Otherwise proceed to Task 2.

---

## Task 2: Insert "Background" section into README.md

**Files:**
- Modify: `README.md` (insert new content between the project tagline and the existing `## 1. IT106 Course Mapping` heading)

- [ ] **Step 1: Insert the Background section**

Find this exact passage in `README.md` (lines 8–10 currently):

```
---

## 1. IT106 Course Mapping
```

Replace it with:

```
---

## 1. Background

Caraga State University currently handles lost and found items through a fragmented, ad-hoc workflow: students post sightings on Facebook groups, finders walk items over to the Student Local Government (SLG) Office, and the office keeps logs on paper or in private spreadsheets. The result is predictable — items go unreturned because their owners never see the post, records get lost when phones change hands, and the same description gets re-reported across three channels with no single source of truth.

The **Lost and Found Management System** replaces that workflow with a single web-based platform. Students file a lost report once; staff log found items once; the system automatically suggests matches based on category, keywords, and location overlap; and the original reporter is notified the moment a match appears. The result is a centralized, searchable record of every lost and found item on campus, plus a workflow that takes a recovered item from *Reported* → *Matched* → *Claimed* → *Released* without anyone retyping data.

---

## 1. IT106 Course Mapping
```

(Note: the duplicate `## 1.` heading is intentional and temporary — Task 3 will renumber the second one. This keeps each task atomic and easy to verify.)

- [ ] **Step 2: Verify Background is present**

Run: `grep -n "^## 1\. Background" "README.md"`
Expected: one match.

Run: `grep -c "Caraga State University currently handles" "README.md"`
Expected: `1`

- [ ] **Step 3: Commit**

```
git add README.md
git commit -m "docs(readme): add Background section (PDF §VI.2)"
```

---

## Task 3: Insert "Objectives" section into README.md

**Files:**
- Modify: `README.md` (insert between Background section and the duplicate `## 1. IT106 Course Mapping` heading)

- [ ] **Step 1: Insert the Objectives section**

Find this exact passage in `README.md` (the closing of Background followed by the separator and the duplicate IT106 heading):

```
The **Lost and Found Management System** replaces that workflow with a single web-based platform. Students file a lost report once; staff log found items once; the system automatically suggests matches based on category, keywords, and location overlap; and the original reporter is notified the moment a match appears. The result is a centralized, searchable record of every lost and found item on campus, plus a workflow that takes a recovered item from *Reported* → *Matched* → *Claimed* → *Released* without anyone retyping data.

---

## 1. IT106 Course Mapping
```

Replace it with:

```
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

## 1. IT106 Course Mapping
```

- [ ] **Step 2: Verify Objectives is present**

Run: `grep -n "^## 2\. Objectives" "README.md"`
Expected: one match.

Run: `grep -c "General Objective" "README.md"`
Expected: `1`

Run: `grep -c "Specific Objectives" "README.md"`
Expected: `1`

- [ ] **Step 3: Commit**

```
git add README.md
git commit -m "docs(readme): add Objectives section (PDF §VI.3)"
```

---

## Task 4: Insert "Scope and Limitations" section into README.md

**Files:**
- Modify: `README.md` (insert between Objectives and the duplicate `## 1. IT106 Course Mapping` heading)

- [ ] **Step 1: Insert the Scope and Limitations section**

Find this exact passage in `README.md`:

```
7. Test the system through functional test cases and document the results in the IT106 testing-results table.

---

## 1. IT106 Course Mapping
```

Replace it with:

```
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

## 1. IT106 Course Mapping
```

- [ ] **Step 2: Verify Scope and Limitations is present**

Run: `grep -n "^## 3\. Scope and Limitations" "README.md"`
Expected: one match.

Run: `grep -c "^### In Scope" "README.md"`
Expected: `1`

Run: `grep -c "^### Out of Scope" "README.md"`
Expected: `1`

- [ ] **Step 3: Commit**

```
git add README.md
git commit -m "docs(readme): add Scope and Limitations section (PDF §VI.4)"
```

---

## Task 5: Insert "System Architecture" section into README.md

**Files:**
- Modify: `README.md` (insert between Scope and Limitations and the duplicate `## 1. IT106 Course Mapping` heading)

- [ ] **Step 1: Insert the System Architecture section**

Find this exact passage in `README.md`:

```
- Integration with external university systems (student records, ID system)

---

## 1. IT106 Course Mapping
```

Replace it with:

````
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

## 1. IT106 Course Mapping
````

- [ ] **Step 2: Verify System Architecture is present**

Run: `grep -n "^## 4\. System Architecture" "README.md"`
Expected: one match.

Run: `grep -c "Request flow" "README.md"`
Expected: `1`

- [ ] **Step 3: Commit**

```
git add README.md
git commit -m "docs(readme): add System Architecture section (PDF §VI.6)"
```

---

## Task 6: Renumber the 11 pre-existing sections (1→5, 2→6, …, 11→15)

**Files:**
- Modify: `README.md` (rewrite each of the existing `## N. Title` headings; do the renumber from highest to lowest so an Edit on `## 1. ...` doesn't accidentally match `## 10. ...` or `## 11. ...`)

- [ ] **Step 1: Renumber `## 11. Documentation` → `## 15. Documentation`**

Find: `## 11. Documentation`
Replace with: `## 15. Documentation`

Run after: `grep -nE "^## (11|15)\. Documentation" "README.md"`
Expected: one line matching `## 15. Documentation`, none matching `## 11.`

- [ ] **Step 2: Renumber `## 10. Data Model` → `## 14. Data Model`**

Find: `## 10. Data Model`
Replace with: `## 14. Data Model`

Run after: `grep -nE "^## (10|14)\. Data Model" "README.md"`
Expected: one line matching `## 14. Data Model`, none matching `## 10.`

- [ ] **Step 3: Renumber `## 9. Project Structure` → `## 13. Project Structure`**

Find: `## 9. Project Structure`
Replace with: `## 13. Project Structure`

Run after: `grep -nE "^## (9|13)\. Project Structure" "README.md"`
Expected: one line matching `## 13. Project Structure`, none matching `## 9.`

- [ ] **Step 4: Renumber `## 8. User Roles` → `## 12. User Roles`**

Find: `## 8. User Roles`
Replace with: `## 12. User Roles`

Run after: `grep -nE "^## (8|12)\. User Roles" "README.md"`
Expected: one line matching `## 12. User Roles`, none matching `## 8.`

- [ ] **Step 5: Renumber `## 7. Deploy to Render + TiDB Cloud` → `## 11. Deploy to Render + TiDB Cloud`**

Find: `## 7. Deploy to Render + TiDB Cloud`
Replace with: `## 11. Deploy to Render + TiDB Cloud`

Run after: `grep -nE "^## (7|11)\. Deploy" "README.md"`
Expected: one line matching `## 11. Deploy …`, none matching `## 7.`

- [ ] **Step 6: Renumber `## 6. Quick Start (local)` → `## 10. Quick Start (local)`**

Find: `## 6. Quick Start (local)`
Replace with: `## 10. Quick Start (local)`

Run after: `grep -nE "^## (6|10)\. Quick Start" "README.md"`
Expected: one line matching `## 10. Quick Start (local)`, none matching `## 6.`

- [ ] **Step 7: Renumber `## 5. Submission Roadmap to May 25, 2026` → `## 9. Submission Roadmap to May 25, 2026`**

Find: `## 5. Submission Roadmap to May 25, 2026`
Replace with: `## 9. Submission Roadmap to May 25, 2026`

Run after: `grep -nE "^## (5|9)\. Submission Roadmap" "README.md"`
Expected: one line matching `## 9. Submission Roadmap …`, none matching `## 5.`

- [ ] **Step 8: Renumber `## 4. Tech Stack (matches PDF §IV — Option C: Hybrid)` → `## 8. Tech Stack (matches PDF §IV — Option C: Hybrid)`**

Find: `## 4. Tech Stack (matches PDF §IV — Option C: Hybrid)`
Replace with: `## 8. Tech Stack (matches PDF §IV — Option C: Hybrid)`

Run after: `grep -nE "^## (4|8)\. Tech Stack" "README.md"`
Expected: one line matching `## 8. Tech Stack …`, none matching `## 4.` (Section 4 is now "System Architecture" inserted earlier.)

⚠ If `grep` shows two lines matching `## 4.`, abort and inspect — Section 4 should now be "System Architecture" (from Task 5) and there should be no `## 4. Tech Stack` remaining.

- [ ] **Step 9: Renumber `## 3. Features (current)` → `## 7. Features (current)`**

Find: `## 3. Features (current)`
Replace with: `## 7. Features (current)`

Run after: `grep -nE "^## (3|7)\. Features" "README.md"`
Expected: one line matching `## 7. Features (current)`, none matching `## 3. Features`. (Section 3 is now "Scope and Limitations" from Task 4.)

- [ ] **Step 10: Renumber `## 2. Minimum Feature Compliance (PDF §V)` → `## 6. Minimum Feature Compliance (PDF §V)`**

Find: `## 2. Minimum Feature Compliance (PDF §V)`
Replace with: `## 6. Minimum Feature Compliance (PDF §V)`

Run after: `grep -nE "^## (2|6)\. Minimum Feature Compliance" "README.md"`
Expected: one line matching `## 6. Minimum Feature Compliance …`, none matching `## 2. Minimum Feature Compliance`. (Section 2 is now "Objectives" from Task 3.)

- [ ] **Step 11: Renumber `## 1. IT106 Course Mapping` → `## 5. IT106 Course Mapping`**

Find: `## 1. IT106 Course Mapping`
Replace with: `## 5. IT106 Course Mapping`

Run after: `grep -nE "^## (1|5)\. IT106 Course Mapping" "README.md"`
Expected: one line matching `## 5. IT106 Course Mapping`, none matching `## 1. IT106 Course Mapping`. (Section 1 is now "Background" from Task 2.)

- [ ] **Step 12: Verify the final 15-section sequence**

Run: `grep -nE "^## [0-9]+\. " "README.md"`

Expected (exactly 15 lines, in this order):
```
## 1. Background
## 2. Objectives
## 3. Scope and Limitations
## 4. System Architecture
## 5. IT106 Course Mapping
## 6. Minimum Feature Compliance (PDF §V)
## 7. Features (current)
## 8. Tech Stack (matches PDF §IV — Option C: Hybrid)
## 9. Submission Roadmap to May 25, 2026
## 10. Quick Start (local)
## 11. Deploy to Render + TiDB Cloud
## 12. User Roles
## 13. Project Structure
## 14. Data Model
## 15. Documentation
```

(Line numbers will differ — only the order and titles matter.)

- [ ] **Step 13: Commit**

```
git add README.md
git commit -m "docs(readme): renumber existing sections to 5-15"
```

---

## Task 7: Fix the stale §1 cross-reference

**Files:**
- Modify: `README.md` (the cell at the original line 40, in the Minimum Feature Compliance table)

- [ ] **Step 1: Update the stale reference**

Find this exact substring in `README.md`:

```
MVC + Application Factory (see §1 above)
```

Replace with:

```
MVC + Application Factory (see §5 above)
```

(Reason: it referenced what was §1 "IT106 Course Mapping". That section is now §5 after the renumber in Task 6.)

- [ ] **Step 2: Verify**

Run: `grep -nE "see §[0-9]+ above" "README.md"`
Expected: one match — `(see §5 above)`. No match for `(see §1 above)`.

- [ ] **Step 3: Commit**

```
git add README.md
git commit -m "docs(readme): repoint stale §1 reference to §5 after renumber"
```

---

## Task 8: Add header redirect note to ScopeProject.md

**Files:**
- Modify: `ScopeProject.md` (insert at the very top, above the existing `# ScopeProject — Lost and Found Tracking System` H1)

- [ ] **Step 1: Insert the redirect note**

Find this exact passage at the top of `ScopeProject.md`:

```
# ScopeProject — Lost and Found Tracking System

> Source brief: [LOST-AND-FOUND.pdf](LOST-AND-FOUND.pdf)
> Existing prototypes: [prototype.html](prototype.html) (ERD), [chatbot_prototype.html](chatbot_prototype.html)
```

Replace with:

```
> **Note:** The single source of truth for project scope, objectives, and architecture is now [README.md](README.md). This document is preserved as a build-history log and risk register for the original Milestones 1–8 that delivered the application itself.

---

# ScopeProject — Lost and Found Tracking System

> Source brief: [LOST-AND-FOUND.pdf](LOST-AND-FOUND.pdf)
> Existing prototypes: [prototype.html](prototype.html) (ERD), [chatbot_prototype.html](chatbot_prototype.html)
```

- [ ] **Step 2: Verify**

Run: `head -3 "ScopeProject.md"`

Expected output (first line is the redirect note):
```
> **Note:** The single source of truth for project scope, objectives, and architecture is now [README.md](README.md). This document is preserved as a build-history log and risk register for the original Milestones 1–8 that delivered the application itself.

---
```

- [ ] **Step 3: Commit**

```
git add ScopeProject.md
git commit -m "docs(scope): demote ScopeProject.md to build-history; redirect to README"
```

---

## Task 9: Final verification

**Files:**
- Inspect-only: `README.md`, `ScopeProject.md`

> **Pre-condition note:** This repo had no prior git commits when the plan was written (every file was untracked per `git status`). The seven commits this plan produces (Tasks 2–8) may be the first commits in the repo, or they may sit on top of an initial baseline commit if the user makes one before running the plan. Either way, the seven `docs(...)`-prefixed commits should be visible in `git log` and they should be the only commits that touch `README.md` and `ScopeProject.md`.

- [ ] **Step 1: Confirm the seven plan commits exist**

Run: `git log --oneline | head -10`

Expected: at least seven commits with `docs(readme):` or `docs(scope):` prefixes, in this top-to-bottom order (most recent first):
```
docs(scope): demote ScopeProject.md to build-history; redirect to README
docs(readme): repoint stale §1 reference to §5 after renumber
docs(readme): renumber existing sections to 5-15
docs(readme): add System Architecture section (PDF §VI.6)
docs(readme): add Scope and Limitations section (PDF §VI.4)
docs(readme): add Objectives section (PDF §VI.3)
docs(readme): add Background section (PDF §VI.2)
```

(Earlier commits — e.g. an initial-baseline commit, or the spec/plan docs — may appear below these seven and are fine.)

- [ ] **Step 2: Confirm no code files were touched by the plan's commits**

Run: `git log --name-only --pretty=format:"=== %s" -7`

Expected: every file listed under one of the seven commit summaries is either `README.md` or `ScopeProject.md`. No paths under `app/`, `database/`, `run.py`, `requirements.txt`, `runtime.txt`, etc. should appear.

- [ ] **Step 2: Read the README top-to-bottom for final sanity check**

Run: `head -30 "README.md"`

Expected: project H1 title + `## 1. Background` opening paragraph visible. No leftover `## 1. IT106 Course Mapping`.

Run: `grep -nE "^## [0-9]+\. " "README.md" | head -20`

Expected: the same 15 sequential sections as in Task 6 Step 12.

- [ ] **Step 3: Re-confirm no stale references remain**

Run: `grep -nE "see §[0-9]+ above" "README.md"`
Expected: one match — `(see §5 above)`.

Run: `grep -nE "^## 1\. IT106 Course Mapping" "README.md"`
Expected: empty.

Run: `grep -nE "^## 1\. Background" "README.md"`
Expected: one match.

- [ ] **Step 4: No additional commit — Task 9 is verification only**

If all checks pass, the README scope refactor is complete and acceptance criteria 1–5 from the spec are satisfied.

---

## Acceptance criteria recap (from the spec)

After this plan executes, the following must all be true:

1. ✅ README.md opens with the four new sections (Background → Objectives → Scope and Limitations → System Architecture) before the IT106 Course Mapping table. — *Tasks 2–5.*
2. ✅ All previously existing sections render with sequential numbering 1–15, content unchanged. — *Task 6.*
3. ✅ Internal Markdown links inside the README still resolve (the one `§1` reference is repointed to `§5`). — *Task 7.*
4. ✅ ScopeProject.md has the header redirect note pointing to README; everything else unchanged. — *Task 8.*
5. ✅ `git diff` shows changes only in README.md, ScopeProject.md, and the new spec/plan files under `docs/superpowers/`. — *Task 9.*
