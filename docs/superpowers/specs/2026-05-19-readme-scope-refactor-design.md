# README Scope Refactor — Design Spec

**Date:** 2026-05-19
**Milestone:** M1 (gap analysis + scope alignment with PDF §VI)
**Approach:** A — Insert-and-keep. Add four new PDF §VI-aligned sections at the top of README.md *before* the existing "IT106 Course Mapping" table. ScopeProject.md gets demoted to a build-history / risk-register supplement that links back to README as the source of truth.

---

## 1. Why this refactor

The README already maps IT106 concepts to the codebase and tracks the M1–M8 submission roadmap. But the PDF §VI documentation format (the 12-section deliverable that M5 will eventually produce) expects four scope-level sections that the README does not currently contain:

| PDF §VI section          | Current README state                                      |
| ------------------------ | --------------------------------------------------------- |
| §VI.2 Introduction       | Only a one-line tagline                                   |
| §VI.3 Objectives         | Implicit in the course-mapping table; no formal list      |
| §VI.4 Scope & Limitations| Exists in ScopeProject.md §3, not surfaced in README      |
| §VI.6 System Architecture| Tech-stack table only; no UI→Backend→DB diagram           |

Adding these four sections turns the README into a single scope-of-record that graders can read top-to-bottom and check off against PDF §VI. When Milestone M5 produces `docs/final-documentation.md`, the content can be lifted from README verbatim instead of being re-drafted.

## 2. Scope of this refactor

**In scope:**
- Insert four new sections at the top of README.md, between the project tagline and the existing "IT106 Course Mapping" table.
- Renumber the existing top-level sections (`## 1. IT106 Course Mapping`, `## 2. Minimum Feature Compliance`, …) so numbering remains sequential after the inserts.
- Add a short header note to ScopeProject.md pointing to README as the source of truth.

**Out of scope:**
- No changes to existing README sections beyond renumbering (Course Mapping, Feature Compliance, Tech Stack, Roadmap, Quick Start, Deploy, User Roles, Project Structure, Data Model, Documentation all stay verbatim).
- No new content in ScopeProject.md beyond the header redirect; the rest of ScopeProject.md (milestones 1–8, risk register, setup guide) stays as build history.
- No code changes. No new files outside README.md, ScopeProject.md, and this spec.

## 3. Final section ordering of README.md

```
Title + tagline
1. Background                       ← NEW (PDF §VI.2)
2. Objectives                       ← NEW (PDF §VI.3)
3. Scope and Limitations            ← NEW (PDF §VI.4)
4. System Architecture              ← NEW (PDF §VI.6)
5. IT106 Course Mapping             ← was 1
6. Minimum Feature Compliance       ← was 2
7. Features (current)               ← was 3
8. Tech Stack                       ← was 4
9. Submission Roadmap to May 25     ← was 5
10. Quick Start (local)             ← was 6
11. Deploy to Render + TiDB Cloud   ← was 7
12. User Roles                      ← was 8
13. Project Structure               ← was 9
14. Data Model                      ← was 10
15. Documentation                   ← was 11
```

## 4. Content for each new section

### 4.1 Section 1 — Background (PDF §VI.2)

```markdown
## 1. Background

Caraga State University currently handles lost and found items through a fragmented, ad-hoc workflow: students post sightings on Facebook groups, finders walk items over to the Student Local Government (SLG) Office, and the office keeps logs on paper or in private spreadsheets. The result is predictable — items go unreturned because their owners never see the post, records get lost when phones change hands, and the same description gets re-reported across three channels with no single source of truth.

The **Lost and Found Management System** replaces that workflow with a single web-based platform. Students file a lost report once; staff log found items once; the system automatically suggests matches based on category, keywords, and location overlap; and the original reporter is notified the moment a match appears. The result is a centralized, searchable record of every lost and found item on campus, plus a workflow that takes a recovered item from *Reported* → *Matched* → *Claimed* → *Released* without anyone retyping data.
```

### 4.2 Section 2 — Objectives (PDF §VI.3)

```markdown
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
```

### 4.3 Section 3 — Scope and Limitations (PDF §VI.4)

```markdown
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
```

### 4.4 Section 4 — System Architecture (PDF §VI.6)

````markdown
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
````

## 5. ScopeProject.md adjustment

Add a header note at the very top of ScopeProject.md (above the existing "ScopeProject — Lost and Found Tracking System" H1):

```markdown
> **Note:** The single source of truth for project scope, objectives, and architecture is now [README.md](README.md). This document is preserved as a build-history log and risk register for the original Milestones 1–8 that delivered the application itself.
```

No other changes to ScopeProject.md.

## 6. Acceptance criteria

The refactor is complete when:

1. README.md opens with the four new sections (Background → Objectives → Scope and Limitations → System Architecture) in that order, before the IT106 Course Mapping table.
2. All previously existing sections still render with sequential numbering (1–15 total) and unchanged content (modulo the renumber).
3. Internal Markdown links inside the README (e.g., `[ScopeProject.md §6](ScopeProject.md)`) still resolve. No anchor links break.
4. ScopeProject.md has the header redirect note pointing to README; everything else in ScopeProject.md is unchanged.
5. `git diff` shows changes only in README.md and ScopeProject.md (plus this new spec file in `docs/superpowers/specs/`).

## 7. What this unblocks

- **M5 (final-documentation.md):** Background, Objectives, Scope/Limitations, and Architecture lift directly from README into the 12-section IT106 documentation.
- **M2 (REST API):** The README's Objective #4 and the Architecture diagram both already name `/api/v1/*` as the planned API surface — the implementation plan can refer back to them.
- **Defense / presentation (M7):** Slides for "Problem", "Objectives", "Scope", and "System Architecture" map 1:1 to README §§1–4.
