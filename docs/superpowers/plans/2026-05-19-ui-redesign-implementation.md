# UI/UX Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The implementer should also follow the `/vibecode` workflow: scan `engineering/` and `engineering-team/` for any frontend / CSS / Bootstrap-override patterns and cite them in the final report.

**Goal:** Replace the vanilla Bootstrap look with a custom "Quiet Polish" modern-minimal design system — one rewritten `style.css` defining tokens + component overrides, an updated `base.html` shell, and refactored markup in every page template to use the new helper classes (`.page-header`, `.segmented-control`, `.empty-state`, `.status-timeline`, `.auth-shell`).

**Architecture:** Keep Bootstrap 5 loaded from CDN. Override its visual primitives in a single ~500-line custom CSS file loaded *after* Bootstrap (source order wins specificity). Add new helper classes for patterns Bootstrap doesn't have. Inline Lucide SVG icons (copy-paste markup, no JS library). Inter font via Google Fonts CDN. Light mode only. No new Python deps, no new JS, no build step.

**Tech Stack:** Bootstrap 5.3 (existing), Jinja2 (existing), custom CSS variables, Inter via Google Fonts CDN, inline Lucide SVGs.

**Spec:** [docs/superpowers/specs/2026-05-19-ui-redesign-design.md](../specs/2026-05-19-ui-redesign-design.md)

---

## Verification approach

Flask is auto-reloading (the dev server has `FLASK_DEBUG=1`). After each file change the server restarts on its own. Per-task verification is two things:

1. **`python -c "from app import create_app; app = create_app(); print('ok')"`** — confirms no Python or Jinja2 import-time errors.
2. **`curl -s -o NUL -w '%{http_code}\n' http://127.0.0.1:8000/<path>`** — confirms the route returns HTTP 200 after the change. (On PowerShell substitute `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/<path> | Select StatusCode`.)

For visual confirmation (does the page *look* right?), the user does the final eyeball-check in Task 9. Per-task we only verify the page renders without breaking.

---

## File map

```
Modified:
  app/static/css/style.css                          (full rewrite, ~500 lines)
  app/templates/base.html                           (full rewrite)
  app/templates/index.html                          (full rewrite)
  app/templates/main/dashboard.html                 (full rewrite)
  app/templates/reports/list.html                   (page-header + segmented + empty-state)
  app/templates/found/list.html                     (page-header + empty-state)
  app/templates/claims/list.html                    (page-header + empty-state)
  app/templates/matches/list.html                   (page-header + empty-state)
  app/templates/notifications/list.html             (page-header + empty-state + soft-tinted rows)
  app/templates/admin/users.html                    (page-header; table style is automatic)
  app/templates/reports/detail.html                 (status timeline + minor restyle)
  app/templates/found/detail.html                   (status timeline + minor restyle)
  app/templates/claims/detail.html                  (status timeline + minor restyle)
  app/templates/matches/detail.html                 (minor restyle, no timeline)
  app/templates/auth/login.html                     (full rewrite — auth-shell)
  app/templates/auth/register.html                  (full rewrite — auth-shell)
  app/templates/reports/new.html                    (wrap in card, small structural tidy)
  app/templates/found/new.html                      (wrap in card, small structural tidy)
  app/templates/claims/new.html                     (already wrapped; minimal change)

Created: (none)
```

---

## Task 1: Rewrite style.css with full design system

**Files:**
- Modify: `app/static/css/style.css` (existing file, 18 lines → ~500 lines)

- [ ] **Step 1: Replace the contents of `app/static/css/style.css` with the full new stylesheet**

Use Write to replace the entire file with:

````css
/* ============================================================
   Lost & Found — Quiet Polish design system
   Spec: docs/superpowers/specs/2026-05-19-ui-redesign-design.md
   Loaded after Bootstrap. Source-order specificity wins.
   ============================================================ */

:root {
  /* Surfaces */
  --color-bg: #fafafa;
  --color-surface: #ffffff;
  --color-surface-subtle: #f4f4f5;
  --color-border: #e4e4e7;
  --color-border-strong: #d4d4d8;

  /* Text */
  --color-text: #18181b;
  --color-text-muted: #71717a;
  --color-text-subtle: #a1a1aa;

  /* Indigo accent */
  --color-primary: #4f46e5;
  --color-primary-hover: #4338ca;
  --color-primary-soft: #eef2ff;
  --color-primary-on: #ffffff;

  /* Status tints (soft) */
  --color-success: #047857;  --color-success-soft: #ecfdf5;
  --color-warning: #b45309;  --color-warning-soft: #fffbeb;
  --color-danger:  #b91c1c;  --color-danger-soft:  #fef2f2;
  --color-info:    #0e7490;  --color-info-soft:    #ecfeff;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;

  /* Radii */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-lg: 0 4px 12px rgba(0,0,0,0.06);

  /* Typography */
  --font-sans: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --text-xs: 12px;
  --text-sm: 13px;
  --text-base: 14px;
  --text-lg: 16px;
  --text-xl: 20px;
  --text-2xl: 24px;
  --text-3xl: 32px;
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
}

/* ============================================================ Base ====== */

html, body {
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  -webkit-font-smoothing: antialiased;
}

h1, h2, h3, h4, h5, h6 { color: var(--color-text); font-weight: 600; letter-spacing: -0.01em; }
a { color: var(--color-primary); text-decoration: none; }
a:hover { color: var(--color-primary-hover); text-decoration: underline; }

hr { border: 0; border-top: 1px solid var(--color-border); margin: var(--space-5) 0; }
.text-muted { color: var(--color-text-muted) !important; }

/* ============================================================ Navbar / Footer ====== */

.site-nav {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: var(--space-3) 0;
  position: sticky;
  top: 0;
  z-index: 1000;
}
.site-nav .navbar-brand {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-primary);
  letter-spacing: -0.01em;
}
.site-nav .navbar-brand:hover { color: var(--color-primary-hover); text-decoration: none; }
.site-nav .nav-link {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
  font-weight: 500;
  padding: var(--space-2) var(--space-3);
  position: relative;
}
.site-nav .nav-link:hover { color: var(--color-text); }
.site-nav .nav-link.active { color: var(--color-primary); }
.site-nav .nav-link.active::after {
  content: "";
  position: absolute;
  left: var(--space-3);
  right: var(--space-3);
  bottom: -10px;
  height: 2px;
  background: var(--color-primary);
  border-radius: 1px;
}
.notif-button { position: relative; }
.notif-dot {
  position: absolute;
  top: 6px; right: 6px;
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--color-primary);
  border: 2px solid var(--color-surface);
}

.site-footer {
  border-top: 1px solid var(--color-border);
  padding: var(--space-5) 0;
  margin-top: var(--space-7);
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  text-align: center;
}

main.container {
  max-width: 1120px;
  padding-top: var(--space-6);
  padding-bottom: var(--space-6);
}

/* ============================================================ Buttons ====== */

.btn {
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 500;
  padding: var(--space-2) var(--space-4);
  height: 36px;
  line-height: 1;
  border: 1px solid transparent;
  transition: background 120ms ease, border-color 120ms ease, color 120ms ease;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}
.btn-sm { height: 28px; padding: var(--space-1) var(--space-3); font-size: var(--text-xs); }
.btn-lg { height: 44px; padding: var(--space-3) var(--space-5); font-size: var(--text-base); }

.btn-primary { background: var(--color-primary); color: var(--color-primary-on); border-color: var(--color-primary); }
.btn-primary:hover, .btn-primary:focus { background: var(--color-primary-hover); border-color: var(--color-primary-hover); color: var(--color-primary-on); }

.btn-outline-primary, .btn-outline-secondary, .btn-outline-light, .btn-outline-warning, .btn-outline-danger {
  background: transparent;
  color: var(--color-text);
  border-color: var(--color-border-strong);
}
.btn-outline-primary:hover, .btn-outline-secondary:hover,
.btn-outline-light:hover, .btn-outline-warning:hover {
  background: var(--color-surface-subtle);
  color: var(--color-text);
  border-color: var(--color-border-strong);
}
.btn-outline-danger { color: var(--color-danger); border-color: var(--color-danger-soft); }
.btn-outline-danger:hover { background: var(--color-danger-soft); color: var(--color-danger); border-color: var(--color-danger-soft); }

.btn-light {
  background: var(--color-surface);
  border-color: var(--color-border-strong);
  color: var(--color-text);
}
.btn-light:hover { background: var(--color-surface-subtle); color: var(--color-text); }

.btn-success { background: var(--color-success); color: white; border-color: var(--color-success); }
.btn-success:hover { background: #036249; color: white; border-color: #036249; }

.btn-ghost {
  background: transparent;
  color: var(--color-text-muted);
  border-color: transparent;
}
.btn-ghost:hover { background: var(--color-surface-subtle); color: var(--color-text); }

/* ============================================================ Cards ====== */

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
.card-body { padding: var(--space-4); }
.card-header {
  background: var(--color-surface-subtle);
  border-bottom: 1px solid var(--color-border);
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}
.card-header.bg-warning-subtle { background: var(--color-warning-soft); color: var(--color-warning); }
.card-header.bg-success-subtle { background: var(--color-success-soft); color: var(--color-success); }
.card-title { font-size: var(--text-lg); font-weight: 600; margin-bottom: var(--space-1); color: var(--color-text); }
.card-text { font-size: var(--text-sm); color: var(--color-text-muted); }

.card-body h6 {
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: var(--space-1);
}
.card-body h2 {
  font-size: var(--text-3xl);
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1;
  color: var(--color-text);
}

/* Stat-card left accent (replaces Bootstrap's full-color borders) */
.card.border-warning {
  border-color: var(--color-border);
  border-left: 3px solid var(--color-warning);
}
.card.border-success {
  border-color: var(--color-border);
  border-left: 3px solid var(--color-success);
}
.card.border-info {
  border-color: var(--color-border);
  border-left: 3px solid var(--color-info);
}
.card.border-warning .card-body,
.card.border-success .card-body,
.card.border-info    .card-body { padding-left: calc(var(--space-4) - 3px); }

/* No-photo placeholder used on item-card photo slots */
.card-photo-empty {
  height: 200px;
  background: var(--color-surface-subtle);
  color: var(--color-text-subtle);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Item-card hover lift (only place we use it) */
.item-card { transition: box-shadow 120ms ease; }
.item-card:hover { box-shadow: var(--shadow-md); }

/* ============================================================ Forms ====== */

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: var(--space-1);
}

.form-control, .form-select {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-base);
  color: var(--color-text);
  width: 100%;
  line-height: var(--leading-normal);
  transition: border-color 120ms ease, box-shadow 120ms ease;
}
.form-control:focus, .form-select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-soft);
  outline: none;
}
.form-control::placeholder { color: var(--color-text-subtle); }
.form-text { font-size: var(--text-xs); color: var(--color-text-muted); margin-top: var(--space-1); }
.form-text.text-danger { color: var(--color-danger) !important; }
.form-control.is-invalid { border-color: var(--color-danger); }
.form-select-sm { height: 28px; padding: var(--space-1) var(--space-3); font-size: var(--text-xs); }

/* ============================================================ Tables ====== */

.table {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border-collapse: separate;
  border-spacing: 0;
  margin-bottom: 0;
}
.table thead th {
  background: var(--color-surface-subtle);
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: var(--space-3) var(--space-4);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}
.table tbody td {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border);
  vertical-align: middle;
}
.table tbody tr:last-child td { border-bottom: 0; }
.table tbody tr:hover td { background: var(--color-surface-subtle); }
.table-hover tbody tr:hover td { background: var(--color-surface-subtle); }
.table-responsive { border-radius: var(--radius-lg); }

/* ============================================================ Badges ====== */

.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-radius: 9999px;
  line-height: 1;
  border: 0;
}
.badge.bg-warning,   .badge-soft-warning   { background: var(--color-warning-soft) !important; color: var(--color-warning) !important; }
.badge.bg-info,      .badge-soft-info      { background: var(--color-info-soft)    !important; color: var(--color-info)    !important; }
.badge.bg-primary,   .badge-soft-primary   { background: var(--color-primary-soft) !important; color: var(--color-primary) !important; }
.badge.bg-success,   .badge-soft-success   { background: var(--color-success-soft) !important; color: var(--color-success) !important; }
.badge.bg-danger,    .badge-soft-danger    { background: var(--color-danger-soft)  !important; color: var(--color-danger)  !important; }
.badge.bg-secondary, .badge-soft-secondary { background: var(--color-surface-subtle) !important; color: var(--color-text-muted) !important; }
.badge.bg-light                            { background: var(--color-surface-subtle) !important; color: var(--color-text-muted) !important; }

/* ============================================================ Alerts ====== */

.alert {
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  border: 1px solid;
}
.alert-success { background: var(--color-success-soft); color: var(--color-success); border-color: var(--color-success-soft); }
.alert-warning { background: var(--color-warning-soft); color: var(--color-warning); border-color: var(--color-warning-soft); }
.alert-danger, .alert-error { background: var(--color-danger-soft); color: var(--color-danger); border-color: var(--color-danger-soft); }
.alert-info { background: var(--color-info-soft); color: var(--color-info); border-color: var(--color-info-soft); }
.alert-light { background: var(--color-surface); color: var(--color-text-muted); border-color: var(--color-border); }

/* ============================================================ Pagination ====== */

.pagination {
  display: flex;
  justify-content: center;
  gap: var(--space-3);
  padding: 0;
  margin-top: var(--space-5);
  list-style: none;
}
.page-item .page-link {
  background: transparent;
  border: 0;
  color: var(--color-text-muted);
  font-size: var(--text-sm);
  font-weight: 500;
  padding: var(--space-1) var(--space-2);
  border-radius: 0;
}
.page-item.active .page-link {
  color: var(--color-primary);
  border-bottom: 2px solid var(--color-primary);
  background: transparent;
}
.page-item:not(.active) .page-link:hover {
  color: var(--color-text);
  background: transparent;
  text-decoration: none;
}
.page-item.disabled .page-link { color: var(--color-text-subtle); }

/* ============================================================ List groups (notifications) ====== */

.list-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.list-group-item {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  color: var(--color-text);
  font-size: var(--text-sm);
  text-decoration: none;
}
.list-group-item:hover { background: var(--color-surface-subtle); text-decoration: none; color: var(--color-text); }
.list-group-item-light, .list-group-item-action { background: var(--color-surface); }
.list-group-item.list-group-item-light { background: var(--color-primary-soft); border-color: var(--color-primary-soft); }

/* ============================================================ Icons (Lucide) ====== */

.icon { width: 16px; height: 16px; stroke-width: 2; vertical-align: -2px; }
.icon-lg { width: 24px; height: 24px; }
.icon-xl { width: 48px; height: 48px; }

/* ============================================================ Hero (landing) ====== */

.hero {
  text-align: center;
  padding: var(--space-7) 0 var(--space-6);
}
.hero-title {
  font-size: var(--text-3xl);
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: var(--space-3);
  color: var(--color-text);
}
.hero-subtitle {
  font-size: var(--text-lg);
  color: var(--color-text-muted);
  max-width: 640px;
  margin: 0 auto var(--space-5);
}
.hero-cta {
  display: flex;
  gap: var(--space-3);
  justify-content: center;
  flex-wrap: wrap;
}

/* ============================================================ Dashboard ====== */

.dashboard-greeting {
  margin-bottom: var(--space-6);
}
.dashboard-greeting h1 {
  font-size: var(--text-2xl);
  font-weight: 600;
  margin-bottom: var(--space-2);
  letter-spacing: -0.01em;
}

/* ============================================================ Page header (list pages) ====== */

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-bottom: var(--space-5);
}
.page-title {
  font-size: var(--text-2xl);
  font-weight: 600;
  letter-spacing: -0.01em;
  margin: 0;
}

.segmented-control {
  display: inline-flex;
  background: var(--color-surface-subtle);
  border-radius: var(--radius-md);
  padding: 2px;
  margin-top: var(--space-2);
}
.segmented-control a {
  font-size: var(--text-xs);
  font-weight: 500;
  padding: var(--space-1) var(--space-3);
  color: var(--color-text-muted);
  border-radius: var(--radius-sm);
  text-decoration: none;
}
.segmented-control a:hover { color: var(--color-text); text-decoration: none; }
.segmented-control a.active {
  background: var(--color-surface);
  color: var(--color-text);
  box-shadow: var(--shadow-sm);
}

/* ============================================================ Empty state ====== */

.empty-state {
  text-align: center;
  padding: var(--space-7) var(--space-4);
}
.empty-icon {
  width: 48px;
  height: 48px;
  color: var(--color-text-subtle);
  margin-bottom: var(--space-4);
}
.empty-title {
  font-size: var(--text-xl);
  font-weight: 600;
  margin-bottom: var(--space-2);
}
.empty-text {
  color: var(--color-text-muted);
  margin: 0 auto var(--space-5);
  max-width: 360px;
}

/* ============================================================ Status timeline ====== */

.status-timeline {
  display: flex;
  list-style: none;
  padding: 0;
  margin: var(--space-4) 0 var(--space-5);
  gap: var(--space-2);
}
.status-step {
  position: relative;
  flex: 1;
  padding-top: var(--space-4);
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text-subtle);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  text-align: left;
}
.status-step::before {
  content: "";
  position: absolute;
  top: 0; left: 0;
  width: 12px; height: 12px;
  border-radius: 50%;
  background: var(--color-border);
  border: 2px solid var(--color-surface);
  box-shadow: 0 0 0 2px var(--color-border);
}
.status-step::after {
  content: "";
  position: absolute;
  top: 5px;
  left: 14px;
  right: 0;
  height: 2px;
  background: var(--color-border);
}
.status-step:last-child::after { display: none; }
.status-step--done { color: var(--color-success); }
.status-step--done::before, .status-step--done::after {
  background: var(--color-success);
  box-shadow: 0 0 0 2px var(--color-success);
}
.status-step--active { color: var(--color-primary); }
.status-step--active::before {
  background: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary);
}
.status-step--danger { color: var(--color-danger); }
.status-step--danger::before, .status-step--danger::after {
  background: var(--color-danger);
  box-shadow: 0 0 0 2px var(--color-danger);
}

/* ============================================================ Auth shell ====== */

.auth-shell {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 200px);
  padding: var(--space-5) var(--space-4);
}
.auth-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: var(--space-6);
  width: 100%;
  max-width: 400px;
}
.auth-title {
  font-size: var(--text-xl);
  font-weight: 600;
  margin-bottom: var(--space-5);
  letter-spacing: -0.01em;
}
.auth-footer {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin: var(--space-5) 0 0;
  text-align: center;
}
.auth-footer a { color: var(--color-primary); font-weight: 500; }

/* ============================================================ Misc utility tweaks ====== */

.img-fluid.rounded { border-radius: var(--radius-lg) !important; }
.bg-light.rounded { background: var(--color-surface-subtle) !important; color: var(--color-text-subtle); }

dl.row dt {
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
dl.row dd { font-size: var(--text-sm); color: var(--color-text); }
````

- [ ] **Step 2: Confirm Flask still boots and CSS loads**

Run: `python -c "from app import create_app; app = create_app(); print('ok')"`

Expected: `ok`

Then: `curl -s -o NUL -w "%{http_code}\n" http://127.0.0.1:8000/static/css/style.css`

Expected: `200`

- [ ] **Step 3: Commit**

```
git add app/static/css/style.css
git commit -m "feat(ui): replace style.css with Quiet Polish design system (tokens + components)"
```

---

## Task 2: Rewrite base.html (Inter, light navbar, footer)

**Files:**
- Modify: `app/templates/base.html` (full rewrite)

- [ ] **Step 1: Replace the entire contents of `app/templates/base.html`**

Use Write to replace the file with:

````html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{% block title %}Lost &amp; Found{% endblock %}</title>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

  <link rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
  <nav class="navbar navbar-expand-lg site-nav">
    <div class="container">
      <a class="navbar-brand" href="{{ url_for('main.index') }}">Lost &amp; Found</a>

      {% if current_user.is_authenticated %}
        {% set is_staff = current_user.role in ("staff", "admin") %}
        {% set is_admin = current_user.role == "admin" %}
        <ul class="navbar-nav me-auto ms-3 flex-row gap-2">
          <li class="nav-item"><a class="nav-link" href="{{ url_for('reports.index') }}">Lost</a></li>
          <li class="nav-item"><a class="nav-link" href="{{ url_for('found.index') }}">Found</a></li>
          <li class="nav-item">
            <a class="nav-link" href="{{ url_for('claims.index') }}">
              {% if is_staff %}Claims{% else %}My claims{% endif %}
            </a>
          </li>
          {% if is_staff %}
            <li class="nav-item"><a class="nav-link" href="{{ url_for('matches.index') }}">Matches</a></li>
          {% endif %}
          {% if is_admin %}
            <li class="nav-item"><a class="nav-link" href="{{ url_for('admin.users') }}">Users</a></li>
          {% endif %}
        </ul>
      {% endif %}

      <div class="ms-auto d-flex gap-2 align-items-center">
        {% if current_user.is_authenticated %}
          <a class="btn btn-ghost btn-sm notif-button"
             href="{{ url_for('notifications.index') }}" title="Notifications">
            <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
              <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
            </svg>
            <span class="d-none d-md-inline">Notifications</span>
            {% if unread_notifications and unread_notifications > 0 %}
              <span class="notif-dot"></span>
            {% endif %}
          </a>
          <a class="btn btn-ghost btn-sm" href="{{ url_for('main.dashboard') }}">Dashboard</a>
          <a class="btn btn-outline-secondary btn-sm" href="{{ url_for('auth.logout') }}">Log out</a>
        {% else %}
          <a class="btn btn-ghost btn-sm" href="{{ url_for('auth.login') }}">Log in</a>
          <a class="btn btn-primary btn-sm" href="{{ url_for('auth.register') }}">Register</a>
        {% endif %}
      </div>
    </div>
  </nav>

  <main class="container">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for category, message in messages %}
        <div class="alert alert-{{ category }}">{{ message }}</div>
      {% endfor %}
    {% endwith %}
    {% block content %}{% endblock %}
  </main>

  <footer class="site-footer">
    <div class="container">
      Lost &amp; Found Management System &middot; IT106 &mdash; Caraga State University
    </div>
  </footer>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
````

- [ ] **Step 2: Verify**

Run: `python -c "from app import create_app; app = create_app(); print('ok')"`
Expected: `ok`

Run: `curl -s -o NUL -w "%{http_code}\n" http://127.0.0.1:8000/`
Expected: `200`

- [ ] **Step 3: Commit**

```
git add app/templates/base.html
git commit -m "feat(ui): light navbar + Inter font + IT106 footer in base.html"
```

---

## Task 3: Rewrite index.html (hero + feature cards)

**Files:**
- Modify: `app/templates/index.html` (full rewrite)

- [ ] **Step 1: Replace the contents of `app/templates/index.html`**

Use Write to replace with:

````html
{% extends "base.html" %}
{% block content %}
<section class="hero">
  <h1 class="hero-title">Lost &amp; Found Tracking</h1>
  <p class="hero-subtitle">
    Report lost items, log found ones, and reunite them &mdash; all in one place.
  </p>
  <div class="hero-cta">
    {% if not current_user.is_authenticated %}
      <a class="btn btn-primary btn-lg" href="{{ url_for('auth.register') }}">Get started</a>
      <a class="btn btn-outline-secondary btn-lg" href="{{ url_for('auth.login') }}">Log in</a>
    {% else %}
      <a class="btn btn-primary btn-lg" href="{{ url_for('main.dashboard') }}">Go to dashboard</a>
    {% endif %}
  </div>
</section>

<div class="row g-4 mt-2">
  <div class="col-md-4">
    <div class="card h-100"><div class="card-body">
      <svg class="icon-lg mb-3" style="color: var(--color-primary);" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
      </svg>
      <h5 class="card-title">Report a lost item</h5>
      <p class="card-text">
        File a report with photo, location, and date. We&apos;ll alert you when there&apos;s a match.
      </p>
    </div></div>
  </div>
  <div class="col-md-4">
    <div class="card h-100"><div class="card-body">
      <svg class="icon-lg mb-3" style="color: var(--color-primary);" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M16.5 9.4 7.55 4.24"/>
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
        <path d="m3.3 7 8.7 5 8.7-5"/>
        <path d="M12 22V12"/>
      </svg>
      <h5 class="card-title">Log a found item</h5>
      <p class="card-text">
        Staff and finders log items turned in to the office for everyone to search.
      </p>
    </div></div>
  </div>
  <div class="col-md-4">
    <div class="card h-100"><div class="card-body">
      <svg class="icon-lg mb-3" style="color: var(--color-primary);" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>
      </svg>
      <h5 class="card-title">Track status</h5>
      <p class="card-text">
        Real-time status: Reported &rarr; Matched &rarr; Claimed &rarr; Closed.
      </p>
    </div></div>
  </div>
</div>
{% endblock %}
````

- [ ] **Step 2: Verify**

Run: `curl -s -o NUL -w "%{http_code}\n" http://127.0.0.1:8000/`
Expected: `200`

- [ ] **Step 3: Commit**

```
git add app/templates/index.html
git commit -m "feat(ui): redesign landing page hero + feature cards with inline Lucide icons"
```

---

## Task 4: Rewrite dashboard.html

**Files:**
- Modify: `app/templates/main/dashboard.html` (full rewrite)

- [ ] **Step 1: Replace the contents of `app/templates/main/dashboard.html`**

Use Write to replace with:

````html
{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block content %}
{% set is_staff = user.role in ("staff", "admin") %}

<div class="dashboard-greeting">
  <h1>Hi, {{ user.name }}</h1>
  <span class="badge badge-soft-primary">{{ user.role|capitalize }}</span>
</div>

{% if is_staff %}
{# ----- Staff / Admin KPIs ----- #}
<div class="row g-3 mb-4">
  <div class="col-md-6 col-lg-3">
    <div class="card h-100 {% if stats.claims_pending > 0 %}border-warning{% endif %}">
      <div class="card-body">
        <h6>Pending claims</h6>
        <h2 class="mb-1">{{ stats.claims_pending }}</h2>
        <a href="{{ url_for('claims.index') }}" class="small">Review &rarr;</a>
      </div>
    </div>
  </div>
  <div class="col-md-6 col-lg-3">
    <div class="card h-100">
      <div class="card-body">
        <h6>Active lost reports</h6>
        <h2 class="mb-1">{{ stats.lost_active }}</h2>
        <span class="text-muted small">{{ stats.lost_total }} total</span>
      </div>
    </div>
  </div>
  <div class="col-md-6 col-lg-3">
    <div class="card h-100">
      <div class="card-body">
        <h6>Items in custody</h6>
        <h2 class="mb-1">{{ stats.found_logged + stats.found_matched }}</h2>
        <span class="text-muted small">{{ stats.found_released }} released</span>
      </div>
    </div>
  </div>
  <div class="col-md-6 col-lg-3">
    <div class="card h-100">
      <div class="card-body">
        <h6>Match rate</h6>
        <h2 class="mb-1">{{ stats.match_rate }}%</h2>
        <span class="text-muted small">{{ stats.matches_total }} confirmed matches</span>
      </div>
    </div>
  </div>
</div>

<h5 class="mb-3 mt-5">Quick actions</h5>
<div class="row g-3">
  <div class="col-md-6 col-lg-4">
    <div class="card h-100"><div class="card-body">
      <h6 class="card-title">Confirm matches</h6>
      <p class="card-text">Review system suggestions and link lost reports to found items.</p>
      <a class="btn btn-primary btn-sm" href="{{ url_for('matches.index') }}">Open</a>
    </div></div>
  </div>
  <div class="col-md-6 col-lg-4">
    <div class="card h-100"><div class="card-body">
      <h6 class="card-title">Review claims</h6>
      <p class="card-text">Approve, reject, or release matched items to their owners.</p>
      <a class="btn btn-primary btn-sm" href="{{ url_for('claims.index') }}">Open</a>
    </div></div>
  </div>
  <div class="col-md-6 col-lg-4">
    <div class="card h-100"><div class="card-body">
      <h6 class="card-title">Log a found item</h6>
      <p class="card-text">Record an item turned in at the office.</p>
      <a class="btn btn-primary btn-sm" href="{{ url_for('found.new') }}">Log</a>
    </div></div>
  </div>
  <div class="col-md-6 col-lg-4">
    <div class="card h-100"><div class="card-body">
      <h6 class="card-title">All lost reports</h6>
      <p class="card-text">Browse everything filed by students.</p>
      <a class="btn btn-outline-primary btn-sm" href="{{ url_for('reports.index') }}">View</a>
    </div></div>
  </div>
  <div class="col-md-6 col-lg-4">
    <div class="card h-100"><div class="card-body">
      <h6 class="card-title">All found items</h6>
      <p class="card-text">Inventory of items currently held or released.</p>
      <a class="btn btn-outline-primary btn-sm" href="{{ url_for('found.index') }}">View</a>
    </div></div>
  </div>
  {% if user.role == "admin" %}
  <div class="col-md-6 col-lg-4">
    <div class="card h-100 border-warning"><div class="card-body">
      <h6 class="card-title">Manage users</h6>
      <p class="card-text">Promote or demote students, staff, and admins.</p>
      <a class="btn btn-outline-primary btn-sm" href="{{ url_for('admin.users') }}">Open</a>
    </div></div>
  </div>
  {% endif %}
</div>

<h5 class="mt-5 mb-3">Exports</h5>
<div class="d-flex gap-2 flex-wrap">
  <a class="btn btn-outline-secondary btn-sm" href="{{ url_for('reports.export_csv') }}">Lost reports (CSV)</a>
  <a class="btn btn-outline-secondary btn-sm" href="{{ url_for('found.export_csv') }}">Found items (CSV)</a>
  <a class="btn btn-outline-secondary btn-sm" href="{{ url_for('claims.export_csv') }}">Claims (CSV)</a>
</div>

{% else %}
{# ----- Student dashboard ----- #}
<div class="row g-3 mb-4">
  <div class="col-md-6 col-lg-3">
    <div class="card h-100">
      <div class="card-body">
        <h6>Active lost reports</h6>
        <h2 class="mb-1">{{ my.my_lost_active }}</h2>
        <span class="text-muted small">{{ my.my_lost }} filed total</span>
      </div>
    </div>
  </div>
  <div class="col-md-6 col-lg-3">
    <div class="card h-100 {% if my.my_lost_matched > 0 %}border-info{% endif %}">
      <div class="card-body">
        <h6>Matched (claimable)</h6>
        <h2 class="mb-1">{{ my.my_lost_matched }}</h2>
        {% if my.my_lost_matched > 0 %}
          <a href="{{ url_for('reports.index', mine=1) }}" class="small">Open my reports &rarr;</a>
        {% else %}
          <span class="text-muted small">no matches yet</span>
        {% endif %}
      </div>
    </div>
  </div>
  <div class="col-md-6 col-lg-3">
    <div class="card h-100">
      <div class="card-body">
        <h6>Pending claims</h6>
        <h2 class="mb-1">{{ my.my_claims_pending }}</h2>
        <span class="text-muted small">awaiting staff review</span>
      </div>
    </div>
  </div>
  <div class="col-md-6 col-lg-3">
    <div class="card h-100 {% if my.my_claims_released > 0 %}border-success{% endif %}">
      <div class="card-body">
        <h6>Recovered</h6>
        <h2 class="mb-1">{{ my.my_claims_released }}</h2>
        <span class="text-muted small">items returned to you</span>
      </div>
    </div>
  </div>
</div>

<h5 class="mb-3 mt-5">Quick actions</h5>
<div class="row g-3">
  <div class="col-md-6 col-lg-4">
    <div class="card h-100"><div class="card-body">
      <h5 class="card-title">Report a lost item</h5>
      <p class="card-text">Lost something? File a report and we&apos;ll alert you when it&apos;s matched.</p>
      <a class="btn btn-primary btn-sm" href="{{ url_for('reports.new') }}">Report</a>
    </div></div>
  </div>
  <div class="col-md-6 col-lg-4">
    <div class="card h-100"><div class="card-body">
      <h5 class="card-title">Log a found item</h5>
      <p class="card-text">Found something? Log it so the owner can find their way to it.</p>
      <a class="btn btn-primary btn-sm" href="{{ url_for('found.new') }}">Log</a>
    </div></div>
  </div>
  <div class="col-md-6 col-lg-4">
    <div class="card h-100"><div class="card-body">
      <h5 class="card-title">My reports</h5>
      <p class="card-text">Track the status of items you&apos;ve reported.</p>
      <a class="btn btn-outline-primary btn-sm" href="{{ url_for('reports.index', mine=1) }}">View mine</a>
    </div></div>
  </div>
  <div class="col-md-6 col-lg-4">
    <div class="card h-100"><div class="card-body">
      <h5 class="card-title">Browse found items</h5>
      <p class="card-text">Search through items others have turned in.</p>
      <a class="btn btn-outline-primary btn-sm" href="{{ url_for('found.index') }}">Browse</a>
    </div></div>
  </div>
  <div class="col-md-6 col-lg-4">
    <div class="card h-100"><div class="card-body">
      <h5 class="card-title">My claims</h5>
      <p class="card-text">See pending and resolved recovery requests.</p>
      <a class="btn btn-outline-primary btn-sm" href="{{ url_for('claims.index') }}">View</a>
    </div></div>
  </div>
</div>
{% endif %}
{% endblock %}
````

- [ ] **Step 2: Verify**

Run: `curl -s -o NUL -w "%{http_code}\n" http://127.0.0.1:8000/dashboard`

Expected: `302` (redirect to login) if no session cookie, or `200` if you have a session. Either way is fine — what we're verifying is that the template doesn't throw a Jinja error.

If you have your dev session cookie handy:
`curl -s -o NUL -w "%{http_code}\n" -b "session=..." http://127.0.0.1:8000/dashboard`
Expected: `200`

- [ ] **Step 3: Commit**

```
git add app/templates/main/dashboard.html
git commit -m "feat(ui): redesign dashboard with quiet greeting + KPI/quick-action cards"
```

---

## Task 5: Restyle list pages

**Files:**
- Modify: `app/templates/reports/list.html` (page-header + segmented + empty-state)
- Modify: `app/templates/found/list.html` (page-header + empty-state)
- Modify: `app/templates/claims/list.html` (page-header + empty-state)
- Modify: `app/templates/matches/list.html` (page-header + empty-state)
- Modify: `app/templates/notifications/list.html` (page-header + empty-state)
- Modify: `app/templates/admin/users.html` (page-header)

- [ ] **Step 1: Replace `app/templates/reports/list.html`**

Use Write with:

````html
{% extends "base.html" %}
{% block title %}{% if mine %}My reports{% else %}Lost reports{% endif %}{% endblock %}
{% block content %}
<div class="page-header">
  <div>
    <h2 class="page-title">{% if mine %}My lost reports{% else %}Lost reports{% endif %}</h2>
    <div class="segmented-control">
      <a class="{% if not mine %}active{% endif %}" href="{{ url_for('reports.index') }}">All</a>
      <a class="{% if mine %}active{% endif %}" href="{{ url_for('reports.index', mine=1) }}">Mine</a>
    </div>
  </div>
  <a class="btn btn-primary" href="{{ url_for('reports.new') }}">
    <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
    Report a lost item
  </a>
</div>

{% if not mine %}
<p class="text-muted small mb-4">
  Browsing all lost reports &mdash; only the reporter and staff see full details
  (description, location, exact date).
</p>
{% endif %}

{% if pagination.items %}
<div class="row g-3">
  {% for report in pagination.items %}
    <div class="col-md-4">
      <div class="card item-card h-100 position-relative">
        {% if report.photo_path %}
          <img src="{{ url_for('static', filename=report.photo_path) }}"
               class="card-img-top" style="height: 200px; object-fit: cover;" alt="">
        {% else %}
          <div class="card-photo-empty">no photo</div>
        {% endif %}
        <div class="card-body">
          <h5 class="card-title mb-1">{{ report.item_name }}</h5>
          <p class="card-text mb-3">
            {{ report.category or "uncategorized" }} &middot; posted {{ report.created_at.strftime("%b %d") }}
          </p>
          {% set color = {'reported': 'warning', 'matched': 'info', 'claimed': 'primary', 'closed': 'secondary'}[report.status] %}
          <span class="badge bg-{{ color }}">{{ report.status|capitalize }}</span>
          <a href="{{ url_for('reports.detail', report_id=report.report_id) }}" class="stretched-link"></a>
        </div>
      </div>
    </div>
  {% endfor %}
</div>

{% if pagination.pages > 1 %}
<nav class="mt-4">
  <ul class="pagination">
    {% for page_num in pagination.iter_pages() %}
      {% if page_num %}
        <li class="page-item {% if page_num == pagination.page %}active{% endif %}">
          <a class="page-link" href="?page={{ page_num }}{% if mine %}&amp;mine=1{% endif %}">{{ page_num }}</a>
        </li>
      {% else %}
        <li class="page-item disabled"><span class="page-link">&hellip;</span></li>
      {% endif %}
    {% endfor %}
  </ul>
</nav>
{% endif %}

{% else %}
<div class="empty-state">
  <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
  </svg>
  <h3 class="empty-title">No lost reports yet</h3>
  <p class="empty-text">Be the first to file a report &mdash; we&apos;ll watch for matches as found items are logged.</p>
  <a class="btn btn-primary" href="{{ url_for('reports.new') }}">+ File a report</a>
</div>
{% endif %}
{% endblock %}
````

- [ ] **Step 2: Replace `app/templates/found/list.html`**

Use Write with:

````html
{% extends "base.html" %}
{% block title %}Found items{% endblock %}
{% block content %}
<div class="page-header">
  <h2 class="page-title">Found items</h2>
  <a class="btn btn-primary" href="{{ url_for('found.new') }}">
    <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
    Log a found item
  </a>
</div>

{% if pagination.items %}
<div class="row g-3">
  {% for item in pagination.items %}
    <div class="col-md-4">
      <div class="card item-card h-100 position-relative">
        {% if item.photo_path %}
          <img src="{{ url_for('static', filename=item.photo_path) }}"
               class="card-img-top" style="height: 200px; object-fit: cover;" alt="">
        {% else %}
          <div class="card-photo-empty">no photo</div>
        {% endif %}
        <div class="card-body">
          <h5 class="card-title mb-1">{{ item.item_name }}</h5>
          <p class="card-text mb-3">
            {{ item.location_found or "&mdash;" }} &middot; {{ item.date_found or "n/a" }}
          </p>
          {% set color = {'logged': 'success', 'matched': 'info', 'released': 'secondary'}[item.status] %}
          <span class="badge bg-{{ color }}">{{ item.status|capitalize }}</span>
          <a href="{{ url_for('found.detail', item_id=item.item_id) }}" class="stretched-link"></a>
        </div>
      </div>
    </div>
  {% endfor %}
</div>

{% if pagination.pages > 1 %}
<nav class="mt-4">
  <ul class="pagination">
    {% for page_num in pagination.iter_pages() %}
      {% if page_num %}
        <li class="page-item {% if page_num == pagination.page %}active{% endif %}">
          <a class="page-link" href="?page={{ page_num }}">{{ page_num }}</a>
        </li>
      {% else %}
        <li class="page-item disabled"><span class="page-link">&hellip;</span></li>
      {% endif %}
    {% endfor %}
  </ul>
</nav>
{% endif %}

{% else %}
<div class="empty-state">
  <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M16.5 9.4 7.55 4.24"/>
    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
    <path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>
  </svg>
  <h3 class="empty-title">No found items logged yet</h3>
  <p class="empty-text">When someone turns in an item to the office, it shows up here.</p>
  <a class="btn btn-primary" href="{{ url_for('found.new') }}">+ Log the first one</a>
</div>
{% endif %}
{% endblock %}
````

- [ ] **Step 3: Replace `app/templates/claims/list.html`**

Use Write with:

````html
{% extends "base.html" %}
{% block title %}Claims{% endblock %}
{% block content %}
{% set is_staff = current_user.role in ("staff", "admin") %}

<div class="page-header">
  <h2 class="page-title">{% if is_staff %}All claims{% else %}My claims{% endif %}</h2>
</div>

{% if claims %}
<div class="table-responsive">
  <table class="table align-middle">
    <thead>
      <tr>
        <th>#</th>
        <th>Item</th>
        {% if is_staff %}<th>Claimant</th>{% endif %}
        <th>Status</th>
        <th>Submitted</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      {% for c in claims %}
        {% set status_color = {'pending': 'warning', 'approved': 'success', 'rejected': 'danger', 'released': 'primary'}[c.status] %}
        <tr>
          <td class="text-muted">{{ c.claim_id }}</td>
          <td>
            <strong>{{ c.match.lost_report.item_name }}</strong>
            <div class="small text-muted">found: {{ c.match.found_item.item_name }}</div>
          </td>
          {% if is_staff %}<td>{{ c.claimant.name }}</td>{% endif %}
          <td><span class="badge bg-{{ status_color }}">{{ c.status|capitalize }}</span></td>
          <td class="small text-muted">{{ c.submitted_at.strftime("%b %d, %Y") }}</td>
          <td>
            <a class="btn btn-sm btn-outline-primary"
               href="{{ url_for('claims.detail', claim_id=c.claim_id) }}">View</a>
          </td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
<div class="empty-state">
  <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>
  </svg>
  <h3 class="empty-title">No claims yet</h3>
  <p class="empty-text">
    {% if is_staff %}
      Claims will appear here when students request items matched to their lost reports.
    {% else %}
      When one of your lost reports is matched, you&apos;ll be able to claim the item from there.
    {% endif %}
  </p>
</div>
{% endif %}
{% endblock %}
````

- [ ] **Step 4: Replace `app/templates/matches/list.html`**

Use Write with:

````html
{% extends "base.html" %}
{% block title %}Matches{% endblock %}
{% block content %}
<div class="page-header">
  <h2 class="page-title">Confirmed matches</h2>
</div>

{% if matches %}
<div class="table-responsive">
  <table class="table align-middle">
    <thead>
      <tr>
        <th>#</th>
        <th>Lost report</th>
        <th>Found item</th>
        <th>Confidence</th>
        <th>Matched at</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      {% for m in matches %}
        <tr>
          <td class="text-muted">{{ m.match_id }}</td>
          <td>
            <a href="{{ url_for('reports.detail', report_id=m.lost_report.report_id) }}">
              {{ m.lost_report.item_name }}
            </a>
            <div class="small text-muted">by {{ m.lost_report.user.name }}</div>
          </td>
          <td>
            <a href="{{ url_for('found.detail', item_id=m.found_item.item_id) }}">
              {{ m.found_item.item_name }}
            </a>
          </td>
          <td>
            <span class="badge bg-info">{{ "%.0f%%"|format((m.confidence_score or 0) * 100) }}</span>
          </td>
          <td class="small text-muted">{{ m.matched_at.strftime("%b %d, %Y %H:%M") }}</td>
          <td>
            <a class="btn btn-sm btn-outline-primary"
               href="{{ url_for('matches.detail', match_id=m.match_id) }}">View</a>
          </td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
<div class="empty-state">
  <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
  </svg>
  <h3 class="empty-title">No matches confirmed yet</h3>
  <p class="empty-text">Open a lost report or found item &mdash; staff can confirm matches from there.</p>
</div>
{% endif %}
{% endblock %}
````

- [ ] **Step 5: Replace `app/templates/notifications/list.html`**

Use Write with:

````html
{% extends "base.html" %}
{% block title %}Notifications{% endblock %}
{% block content %}
<div class="page-header">
  <h2 class="page-title">Notifications</h2>
  {% if notifs and unread_notifications > 0 %}
  <form method="post" action="{{ url_for('notifications.mark_all_read') }}">
    <button class="btn btn-outline-secondary btn-sm">Mark all as read</button>
  </form>
  {% endif %}
</div>

{% if notifs %}
<div class="list-group">
  {% for n in notifs %}
    <a href="{{ url_for('notifications.open_', notification_id=n.notification_id) }}"
       class="list-group-item {% if not n.is_read %}list-group-item-light{% endif %}">
      <div class="d-flex justify-content-between align-items-start gap-2">
        <div>
          {% if not n.is_read %}<span class="badge badge-soft-primary me-2">new</span>{% endif %}
          <strong>{{ n.title }}</strong>
          {% if n.body %}<div class="text-muted small mt-1">{{ n.body }}</div>{% endif %}
        </div>
        <small class="text-muted text-nowrap">{{ n.created_at.strftime("%b %d, %H:%M") }}</small>
      </div>
    </a>
  {% endfor %}
</div>
{% else %}
<div class="empty-state">
  <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
    <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
  </svg>
  <h3 class="empty-title">No notifications yet</h3>
  <p class="empty-text">
    You&apos;ll get one when your lost report is matched, your claim is reviewed, or your item is released.
  </p>
</div>
{% endif %}
{% endblock %}
````

- [ ] **Step 6: Replace `app/templates/admin/users.html`**

Use Write with:

````html
{% extends "base.html" %}
{% block title %}Manage users{% endblock %}
{% block content %}
<div class="page-header">
  <div>
    <h2 class="page-title">Users</h2>
    <span class="text-muted small">{{ users|length }} registered</span>
  </div>
</div>

<div class="table-responsive">
  <table class="table align-middle">
    <thead>
      <tr>
        <th>#</th>
        <th>Name</th>
        <th>Email</th>
        <th>Phone</th>
        <th>Role</th>
        <th>Joined</th>
        <th style="min-width: 200px;">Change role</th>
      </tr>
    </thead>
    <tbody>
      {% for u in users %}
      <tr>
        <td class="text-muted">{{ u.user_id }}</td>
        <td>
          <strong>{{ u.name }}</strong>
          {% if u.user_id == current_user.user_id %}
            <span class="badge badge-soft-secondary ms-1">you</span>
          {% endif %}
        </td>
        <td><span class="text-muted small">{{ u.email }}</span></td>
        <td><span class="text-muted small">{{ u.phone or "&mdash;" }}</span></td>
        <td>
          {% set color = {"student": "secondary", "staff": "primary", "admin": "warning"}[u.role] %}
          <span class="badge bg-{{ color }}">{{ u.role|capitalize }}</span>
        </td>
        <td class="small text-muted">{{ u.created_at.strftime("%b %d, %Y") }}</td>
        <td>
          <form method="post" action="{{ url_for('admin.set_role', user_id=u.user_id) }}"
                class="d-flex gap-2">
            <select name="role" class="form-select form-select-sm" style="max-width: 110px;">
              <option value="student" {% if u.role == "student" %}selected{% endif %}>Student</option>
              <option value="staff"   {% if u.role == "staff"   %}selected{% endif %}>Staff</option>
              <option value="admin"   {% if u.role == "admin"   %}selected{% endif %}>Admin</option>
            </select>
            <button class="btn btn-sm btn-outline-primary">Save</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
````

- [ ] **Step 7: Verify each list page renders**

Run these in sequence (all should print `200` or `302` — `200` if you're logged in, `302` if the route redirects to login):
```
curl -s -o NUL -w "%{http_code}\n" http://127.0.0.1:8000/reports/
curl -s -o NUL -w "%{http_code}\n" http://127.0.0.1:8000/found/
curl -s -o NUL -w "%{http_code}\n" http://127.0.0.1:8000/claims/
curl -s -o NUL -w "%{http_code}\n" http://127.0.0.1:8000/matches/
curl -s -o NUL -w "%{http_code}\n" http://127.0.0.1:8000/notifications/
curl -s -o NUL -w "%{http_code}\n" http://127.0.0.1:8000/admin/users
```

What matters: no `500` errors (which would mean a Jinja syntax bug).

- [ ] **Step 8: Commit**

```
git add app/templates/reports/list.html app/templates/found/list.html app/templates/claims/list.html app/templates/matches/list.html app/templates/notifications/list.html app/templates/admin/users.html
git commit -m "feat(ui): apply page-header / segmented-control / empty-state to list pages"
```

---

## Task 6: Add status timelines and tidy detail pages

**Files:**
- Modify: `app/templates/reports/detail.html`
- Modify: `app/templates/found/detail.html`
- Modify: `app/templates/claims/detail.html`
- Modify: `app/templates/matches/detail.html`

- [ ] **Step 1: Replace `app/templates/reports/detail.html`**

Use Write with:

````html
{% extends "base.html" %}
{% block title %}{{ report.item_name }}{% endblock %}
{% block content %}
{% set is_owner = report.user_id == current_user.user_id %}
{% set stages = ["reported", "matched", "claimed", "closed"] %}
{% set current_index = stages.index(report.status) %}

<a href="{{ url_for('reports.index') }}" class="text-muted small">&larr; Back to lost reports</a>

<div class="row mt-3 g-4">
  <div class="col-md-5">
    {% if report.photo_path %}
      <img src="{{ url_for('static', filename=report.photo_path) }}" class="img-fluid rounded" alt="">
    {% else %}
      <div class="card-photo-empty rounded" style="height: 280px;">no photo uploaded</div>
    {% endif %}
  </div>
  <div class="col-md-7">
    <h2 class="mb-3">{{ report.item_name }}</h2>

    <ol class="status-timeline">
      {% for s in stages %}
        {% set idx = loop.index0 %}
        <li class="status-step {% if idx < current_index %}status-step--done{% elif idx == current_index %}status-step--active{% endif %}">
          {{ s|capitalize }}
        </li>
      {% endfor %}
    </ol>

    <dl class="row mb-3">
      <dt class="col-sm-4">Category</dt>
      <dd class="col-sm-8">{{ report.category or "&mdash;" }}</dd>

      <dt class="col-sm-4">Reported on</dt>
      <dd class="col-sm-8">{{ report.created_at.strftime("%b %d, %Y") }}</dd>

      {% if is_authorized %}
      <dt class="col-sm-4">Reported by</dt>
      <dd class="col-sm-8">{{ report.user.name }}</dd>

      <dt class="col-sm-4">Location lost</dt>
      <dd class="col-sm-8">{{ report.location or "&mdash;" }}</dd>

      <dt class="col-sm-4">Date lost</dt>
      <dd class="col-sm-8">{{ report.date_lost or "n/a" }}</dd>
      {% endif %}
    </dl>

    {% if is_authorized and report.description %}
    <h6 class="text-muted">Description</h6>
    <p>{{ report.description }}</p>
    {% endif %}

    {% if not is_authorized %}
    <div class="alert alert-light small mt-3">
      <strong>Privacy:</strong> Description, location, and the exact date of loss
      are visible only to the reporter and to staff. If you found this item,
      please <a href="{{ url_for('found.new') }}">log it as found</a> &mdash; staff
      will review the match and notify the owner.
    </div>
    {% endif %}
  </div>
</div>

{% if is_authorized and report.match %}
<hr>
<div class="alert alert-info d-flex justify-content-between align-items-center flex-wrap gap-2">
  <div>
    <strong>Matched</strong> with
    <a href="{{ url_for('found.detail', item_id=report.match.found_item.item_id) }}">
      {{ report.match.found_item.item_name }}
    </a>
    &middot;
    <a href="{{ url_for('matches.detail', match_id=report.match.match_id) }}">view match</a>
  </div>
  {% if is_owner and report.match.found_item.status != "released" %}
    {% set my_claim = report.match.claims | selectattr("claimant_id", "equalto", current_user.user_id)
                                          | rejectattr("status", "equalto", "rejected")
                                          | list | first %}
    {% if my_claim %}
      <a class="btn btn-sm btn-outline-primary"
         href="{{ url_for('claims.detail', claim_id=my_claim.claim_id) }}">
        View my claim ({{ my_claim.status }})
      </a>
    {% else %}
      <a class="btn btn-sm btn-primary"
         href="{{ url_for('claims.new', match_id=report.match.match_id) }}">Claim this item</a>
    {% endif %}
  {% endif %}
</div>
{% elif is_authorized and candidates %}
<hr>
<h4 class="mb-3">Possible matches</h4>
<p class="text-muted small">
  Top {{ candidates|length }} found item(s) that might be this report. Staff can confirm a match below.
</p>
<div class="row g-3">
  {% for item, score, reasons in candidates %}
    <div class="col-md-6">
      <div class="card h-100">
        <div class="row g-0">
          <div class="col-4">
            {% if item.photo_path %}
              <img src="{{ url_for('static', filename=item.photo_path) }}"
                   class="rounded-start" style="width:100%; height:100%; object-fit:cover;" alt="">
            {% else %}
              <div class="card-photo-empty h-100">no photo</div>
            {% endif %}
          </div>
          <div class="col-8">
            <div class="card-body py-2">
              <div class="d-flex justify-content-between align-items-start">
                <h6 class="mb-1">{{ item.item_name }}</h6>
                <span class="badge badge-soft-primary" title="Match confidence">{{ "%.0f%%"|format(score * 100) }}</span>
              </div>
              <p class="text-muted small mb-1">
                {{ item.location_found or "&mdash;" }} &middot; {{ item.date_found or "n/a" }}
              </p>
              {% if reasons %}
              <p class="small mb-2" style="color: var(--color-success);">
                Why: {{ reasons | join(' &middot; ') }}
              </p>
              {% endif %}
              <div class="d-flex gap-2">
                <a class="btn btn-sm btn-outline-secondary"
                   href="{{ url_for('found.detail', item_id=item.item_id) }}">View</a>
                {% if current_user.role in ("staff", "admin") %}
                <form method="post" action="{{ url_for('matches.confirm') }}" class="d-inline">
                  <input type="hidden" name="lost_report_id" value="{{ report.report_id }}">
                  <input type="hidden" name="found_item_id" value="{{ item.item_id }}">
                  <input type="hidden" name="score" value="{{ score }}">
                  <button class="btn btn-sm btn-primary">Confirm match</button>
                </form>
                {% endif %}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  {% endfor %}
</div>
{% elif is_authorized and report.status == "reported" %}
<hr>
<p class="text-muted">No likely matches yet. We&apos;ll keep looking as new found items are logged.</p>
{% endif %}
{% endblock %}
````

- [ ] **Step 2: Replace `app/templates/found/detail.html`**

Use Write with:

````html
{% extends "base.html" %}
{% block title %}{{ item.item_name }}{% endblock %}
{% block content %}
{% set stages = ["logged", "matched", "released"] %}
{% set current_index = stages.index(item.status) %}

<a href="{{ url_for('found.index') }}" class="text-muted small">&larr; Back to found items</a>

<div class="row mt-3 g-4">
  <div class="col-md-5">
    {% if item.photo_path %}
      <img src="{{ url_for('static', filename=item.photo_path) }}" class="img-fluid rounded" alt="">
    {% else %}
      <div class="card-photo-empty rounded" style="height: 280px;">no photo uploaded</div>
    {% endif %}
  </div>
  <div class="col-md-7">
    <h2 class="mb-3">{{ item.item_name }}</h2>

    <ol class="status-timeline">
      {% for s in stages %}
        {% set idx = loop.index0 %}
        <li class="status-step {% if idx < current_index %}status-step--done{% elif idx == current_index %}status-step--active{% endif %}">
          {{ s|capitalize }}
        </li>
      {% endfor %}
    </ol>

    <dl class="row mb-3">
      <dt class="col-sm-4">Logged by</dt>
      <dd class="col-sm-8">
        {% if item.logged_by %}user #{{ item.logged_by }}{% else %}&mdash;{% endif %}
      </dd>

      <dt class="col-sm-4">Category</dt>
      <dd class="col-sm-8">{{ item.category or "&mdash;" }}</dd>

      <dt class="col-sm-4">Location found</dt>
      <dd class="col-sm-8">{{ item.location_found or "&mdash;" }}</dd>

      <dt class="col-sm-4">Date found</dt>
      <dd class="col-sm-8">{{ item.date_found or "n/a" }}</dd>

      <dt class="col-sm-4">Logged on</dt>
      <dd class="col-sm-8">{{ item.created_at.strftime("%b %d, %Y %H:%M") }}</dd>
    </dl>

    {% if item.description %}
    <h6 class="text-muted">Description</h6>
    <p>{{ item.description }}</p>
    {% endif %}
  </div>
</div>

{% if item.match %}
<hr>
<div class="alert alert-info">
  <strong>Matched</strong> with the lost report
  <a href="{{ url_for('reports.detail', report_id=item.match.lost_report.report_id) }}">
    {{ item.match.lost_report.item_name }}
  </a>
  &middot;
  <a href="{{ url_for('matches.detail', match_id=item.match.match_id) }}">view match</a>
</div>
{% elif candidates %}
<hr>
<h4 class="mb-3">Possible matches</h4>
<p class="text-muted small">
  Top {{ candidates|length }} lost report(s) that might be looking for this item.
</p>
<div class="row g-3">
  {% for report, score, reasons in candidates %}
    <div class="col-md-6">
      <div class="card h-100">
        <div class="row g-0">
          <div class="col-4">
            {% if report.photo_path %}
              <img src="{{ url_for('static', filename=report.photo_path) }}"
                   class="rounded-start" style="width:100%; height:100%; object-fit:cover;" alt="">
            {% else %}
              <div class="card-photo-empty h-100">no photo</div>
            {% endif %}
          </div>
          <div class="col-8">
            <div class="card-body py-2">
              <div class="d-flex justify-content-between align-items-start">
                <h6 class="mb-1">{{ report.item_name }}</h6>
                <span class="badge badge-soft-primary" title="Match confidence">{{ "%.0f%%"|format(score * 100) }}</span>
              </div>
              <p class="text-muted small mb-1">
                {{ report.location or "&mdash;" }} &middot; {{ report.date_lost or "n/a" }}
              </p>
              {% if reasons %}
              <p class="small mb-1" style="color: var(--color-success);">
                Why: {{ reasons | join(' &middot; ') }}
              </p>
              {% endif %}
              <p class="small mb-2 text-muted">by {{ report.user.name }}</p>
              <div class="d-flex gap-2">
                <a class="btn btn-sm btn-outline-secondary"
                   href="{{ url_for('reports.detail', report_id=report.report_id) }}">View</a>
                {% if current_user.role in ("staff", "admin") %}
                <form method="post" action="{{ url_for('matches.confirm') }}" class="d-inline">
                  <input type="hidden" name="lost_report_id" value="{{ report.report_id }}">
                  <input type="hidden" name="found_item_id" value="{{ item.item_id }}">
                  <input type="hidden" name="score" value="{{ score }}">
                  <button class="btn btn-sm btn-primary">Confirm match</button>
                </form>
                {% endif %}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  {% endfor %}
</div>
{% elif item.status == "logged" %}
<hr>
<p class="text-muted">No likely lost reports match this yet.</p>
{% endif %}
{% endblock %}
````

- [ ] **Step 3: Replace `app/templates/claims/detail.html`**

Use Write with:

````html
{% extends "base.html" %}
{% block title %}Claim #{{ claim.claim_id }}{% endblock %}
{% block content %}
{% set status_color = {'pending': 'warning', 'approved': 'success', 'rejected': 'danger', 'released': 'primary'}[claim.status] %}

<a href="{{ url_for('claims.index') }}" class="text-muted small">&larr; Back to claims</a>

<div class="page-header mt-3">
  <h2 class="page-title">Claim #{{ claim.claim_id }}</h2>
  <span class="badge bg-{{ status_color }}">{{ claim.status|capitalize }}</span>
</div>

{# Claims have 3 main stages + a Rejected branch off Pending. #}
{% if claim.status == "rejected" %}
<ol class="status-timeline">
  <li class="status-step status-step--done">Pending</li>
  <li class="status-step status-step--danger">Rejected</li>
</ol>
{% else %}
{% set cstages = ["pending", "approved", "released"] %}
{% set cindex = cstages.index(claim.status) %}
<ol class="status-timeline">
  {% for s in cstages %}
    {% set idx = loop.index0 %}
    <li class="status-step {% if idx < cindex %}status-step--done{% elif idx == cindex %}status-step--active{% endif %}">
      {{ s|capitalize }}
    </li>
  {% endfor %}
</ol>
{% endif %}

<div class="row g-4">
  <div class="col-md-6">
    <div class="card h-100">
      <div class="card-header bg-warning-subtle">Lost report</div>
      <div class="card-body">
        <h5>{{ claim.match.lost_report.item_name }}</h5>
        <p class="text-muted small mb-2">
          {{ claim.match.lost_report.location or "&mdash;" }} &middot;
          {{ claim.match.lost_report.date_lost or "n/a" }}
        </p>
        <a class="btn btn-sm btn-outline-secondary"
           href="{{ url_for('reports.detail', report_id=claim.match.lost_report.report_id) }}">
          View report
        </a>
      </div>
    </div>
  </div>
  <div class="col-md-6">
    <div class="card h-100">
      <div class="card-header bg-success-subtle">Found item</div>
      <div class="card-body">
        <h5>{{ claim.match.found_item.item_name }}</h5>
        <p class="text-muted small mb-2">
          {{ claim.match.found_item.location_found or "&mdash;" }} &middot;
          {{ claim.match.found_item.date_found or "n/a" }}
        </p>
        <a class="btn btn-sm btn-outline-secondary"
           href="{{ url_for('found.detail', item_id=claim.match.found_item.item_id) }}">
          View item
        </a>
      </div>
    </div>
  </div>
</div>

<div class="mt-4">
  <h5>Claimant</h5>
  <p class="mb-1">
    <strong>{{ claim.claimant.name }}</strong>
    <span class="text-muted small ms-2">{{ claim.claimant.email }}</span>
  </p>
  <p class="text-muted small">
    Submitted {{ claim.submitted_at.strftime("%b %d, %Y at %H:%M") }}
  </p>

  {% if claim.notes %}
  <h6 class="text-muted mt-3">Notes from claimant</h6>
  <p>{{ claim.notes }}</p>
  {% endif %}

  {% if claim.verifier %}
  <p class="text-muted small">
    {{ claim.status|capitalize }} by {{ claim.verifier.name }}
    {% if claim.resolved_at %}on {{ claim.resolved_at.strftime("%b %d, %Y at %H:%M") }}{% endif %}
  </p>
  {% endif %}
</div>

{% if current_user.role in ("staff", "admin") %}
<hr>
<h5 class="mb-3">Staff actions</h5>
<div class="d-flex gap-2 flex-wrap">
  {% if claim.status == "pending" %}
    <form method="post" action="{{ url_for('claims.approve', claim_id=claim.claim_id) }}" class="d-inline">
      <button class="btn btn-success">Approve</button>
    </form>
    <form method="post" action="{{ url_for('claims.reject', claim_id=claim.claim_id) }}" class="d-inline"
          onsubmit="return confirm('Reject this claim?');">
      <button class="btn btn-outline-danger">Reject</button>
    </form>
  {% elif claim.status == "approved" %}
    <form method="post" action="{{ url_for('claims.release', claim_id=claim.claim_id) }}" class="d-inline"
          onsubmit="return confirm('Mark item as released to the claimant? This closes the lost report.');">
      <button class="btn btn-primary">Mark as released</button>
    </form>
    <form method="post" action="{{ url_for('claims.reject', claim_id=claim.claim_id) }}" class="d-inline"
          onsubmit="return confirm('Reject this approved claim?');">
      <button class="btn btn-outline-danger">Reject</button>
    </form>
  {% else %}
    <p class="text-muted small mb-0">No further actions &mdash; claim is {{ claim.status }}.</p>
  {% endif %}
</div>
{% endif %}
{% endblock %}
````

- [ ] **Step 4: Replace `app/templates/matches/detail.html`**

Use Write with:

````html
{% extends "base.html" %}
{% block title %}Match #{{ match.match_id }}{% endblock %}
{% block content %}
{% set is_owner = match.lost_report.user_id == current_user.user_id %}
{% set is_staff = current_user.role in ("staff", "admin") %}

<a href="{% if is_staff %}{{ url_for('matches.index') }}{% else %}{{ url_for('main.dashboard') }}{% endif %}"
   class="text-muted small">&larr; Back</a>

<div class="page-header mt-3">
  <h2 class="page-title">Match #{{ match.match_id }}</h2>
  <span class="badge badge-soft-info">
    Confidence: {{ "%.0f%%"|format((match.confidence_score or 0) * 100) }}
  </span>
</div>

<div class="row g-4">
  <div class="col-md-6">
    <div class="card h-100">
      <div class="card-header bg-warning-subtle">Lost report</div>
      <div class="card-body">
        <h5>{{ match.lost_report.item_name }}</h5>
        <p class="text-muted small mb-2">
          {{ match.lost_report.location or "&mdash;" }} &middot;
          {{ match.lost_report.date_lost or "n/a" }}
        </p>
        <p class="small">Reported by <strong>{{ match.lost_report.user.name }}</strong></p>
        <a class="btn btn-sm btn-outline-secondary"
           href="{{ url_for('reports.detail', report_id=match.lost_report.report_id) }}">View report</a>
      </div>
    </div>
  </div>

  <div class="col-md-6">
    <div class="card h-100">
      <div class="card-header bg-success-subtle">Found item</div>
      <div class="card-body">
        <h5>{{ match.found_item.item_name }}</h5>
        <p class="text-muted small mb-2">
          {{ match.found_item.location_found or "&mdash;" }} &middot;
          {{ match.found_item.date_found or "n/a" }}
        </p>
        <a class="btn btn-sm btn-outline-secondary"
           href="{{ url_for('found.detail', item_id=match.found_item.item_id) }}">View item</a>
      </div>
    </div>
  </div>
</div>

{% if is_owner and match.found_item.status != "released" %}
  {% set my_claim = match.claims | selectattr("claimant_id", "equalto", current_user.user_id)
                                  | rejectattr("status", "equalto", "rejected")
                                  | list | first %}
  {% if my_claim %}
    <div class="alert alert-info mt-4">
      You have a {{ my_claim.status }} claim on this item.
      <a href="{{ url_for('claims.detail', claim_id=my_claim.claim_id) }}">View claim &rarr;</a>
    </div>
  {% else %}
    <div class="mt-4">
      <a class="btn btn-primary btn-lg" href="{{ url_for('claims.new', match_id=match.match_id) }}">
        Claim this item
      </a>
    </div>
  {% endif %}
{% endif %}

{% if match.claims %}
<hr>
<h5>Claims on this match</h5>
<ul class="list-group">
  {% for c in match.claims %}
    {% set sc = {'pending': 'warning', 'approved': 'success', 'rejected': 'danger', 'released': 'primary'}[c.status] %}
    <li class="list-group-item d-flex justify-content-between align-items-center">
      <div>
        <strong>{{ c.claimant.name }}</strong>
        <span class="text-muted small ms-2">{{ c.submitted_at.strftime("%b %d, %Y") }}</span>
      </div>
      <div>
        <span class="badge bg-{{ sc }} me-2">{{ c.status|capitalize }}</span>
        <a class="btn btn-sm btn-outline-primary"
           href="{{ url_for('claims.detail', claim_id=c.claim_id) }}">View</a>
      </div>
    </li>
  {% endfor %}
</ul>
{% endif %}

<div class="mt-4">
  <p class="text-muted small mb-2">Matched on {{ match.matched_at.strftime("%b %d, %Y %H:%M") }}</p>

  {% if is_staff %}
  <form method="post" action="{{ url_for('matches.dissolve', match_id=match.match_id) }}"
        onsubmit="return confirm('Dissolve this match? Both items will revert to their original status.');">
    <button class="btn btn-outline-danger btn-sm">Dissolve match</button>
  </form>
  {% endif %}
</div>
{% endblock %}
````

- [ ] **Step 5: Verify all four detail pages**

Run:
```
python -c "from app import create_app; app = create_app(); print('ok')"
```
Expected: `ok` (no Jinja import errors).

Then ask the user to navigate to a real lost-report detail page (e.g. `http://127.0.0.1:8000/reports/1`) to visually confirm the timeline renders. For now, just confirm the app boots.

- [ ] **Step 6: Commit**

```
git add app/templates/reports/detail.html app/templates/found/detail.html app/templates/claims/detail.html app/templates/matches/detail.html
git commit -m "feat(ui): add status timelines + redesign detail pages"
```

---

## Task 7: Rewrite auth pages with auth-shell

**Files:**
- Modify: `app/templates/auth/login.html`
- Modify: `app/templates/auth/register.html`

- [ ] **Step 1: Replace `app/templates/auth/login.html`**

Use Write with:

````html
{% extends "base.html" %}
{% block title %}Log in{% endblock %}
{% block content %}
<div class="auth-shell">
  <div class="auth-card">
    <h1 class="auth-title">Log in</h1>
    <form method="post" novalidate>
      {{ form.hidden_tag() }}
      <div class="mb-3">
        {{ form.email.label(class="form-label") }}
        {{ form.email(class="form-control", autofocus=true) }}
        {% for error in form.email.errors %}
          <div class="form-text text-danger">{{ error }}</div>
        {% endfor %}
      </div>
      <div class="mb-4">
        {{ form.password.label(class="form-label") }}
        {{ form.password(class="form-control") }}
        {% for error in form.password.errors %}
          <div class="form-text text-danger">{{ error }}</div>
        {% endfor %}
      </div>
      {{ form.submit(class="btn btn-primary w-100") }}
    </form>
    <p class="auth-footer">
      No account? <a href="{{ url_for('auth.register') }}">Register</a>
    </p>
  </div>
</div>
{% endblock %}
````

- [ ] **Step 2: Replace `app/templates/auth/register.html`**

Use Write with:

````html
{% extends "base.html" %}
{% block title %}Register{% endblock %}
{% block content %}
<div class="auth-shell">
  <div class="auth-card">
    <h1 class="auth-title">Create an account</h1>
    <form method="post" novalidate>
      {{ form.hidden_tag() }}

      <div class="mb-3">
        {{ form.name.label(class="form-label") }}
        {{ form.name(class="form-control", autofocus=true) }}
        {% for error in form.name.errors %}
          <div class="form-text text-danger">{{ error }}</div>
        {% endfor %}
      </div>

      <div class="mb-3">
        {{ form.email.label(class="form-label") }}
        {{ form.email(class="form-control") }}
        {% for error in form.email.errors %}
          <div class="form-text text-danger">{{ error }}</div>
        {% endfor %}
      </div>

      <div class="mb-3">
        {{ form.phone.label(class="form-label") }}
        {{ form.phone(class="form-control") }}
        {% for error in form.phone.errors %}
          <div class="form-text text-danger">{{ error }}</div>
        {% endfor %}
      </div>

      <div class="mb-3">
        {{ form.password.label(class="form-label") }}
        {{ form.password(class="form-control") }}
        {% for error in form.password.errors %}
          <div class="form-text text-danger">{{ error }}</div>
        {% endfor %}
      </div>

      <div class="mb-4">
        {{ form.confirm.label(class="form-label") }}
        {{ form.confirm(class="form-control") }}
        {% for error in form.confirm.errors %}
          <div class="form-text text-danger">{{ error }}</div>
        {% endfor %}
      </div>

      {{ form.submit(class="btn btn-primary w-100") }}
    </form>
    <p class="auth-footer">
      Already have an account? <a href="{{ url_for('auth.login') }}">Log in</a>
    </p>
  </div>
</div>
{% endblock %}
````

- [ ] **Step 3: Verify**

Run:
```
curl -s -o NUL -w "%{http_code}\n" http://127.0.0.1:8000/auth/login
curl -s -o NUL -w "%{http_code}\n" http://127.0.0.1:8000/auth/register
```
Expected: both `200`.

- [ ] **Step 4: Commit**

```
git add app/templates/auth/login.html app/templates/auth/register.html
git commit -m "feat(ui): wrap login + register in auth-shell card"
```

---

## Task 8: Verify new-record form pages

**Files:**
- Modify: `app/templates/reports/new.html` (wrap form section in a card for consistency)
- Modify: `app/templates/found/new.html` (same)
- Modify: `app/templates/claims/new.html` (already uses cards; verify)

These three forms already use `form-control` / `form-label` classes, so the form-input styling is already applied by the new CSS (form-control is overridden in §6.3 of the spec). We just wrap each form in a card for consistency with the rest of the redesigned app.

- [ ] **Step 1: Replace `app/templates/reports/new.html`**

Use Write with:

````html
{% extends "base.html" %}
{% block title %}Report a lost item{% endblock %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-md-7">
    <h2 class="page-title mb-4">Report a lost item</h2>
    <div class="card">
      <div class="card-body">
        <form method="post" enctype="multipart/form-data" novalidate>
          {{ form.hidden_tag() }}

          <div class="mb-3">
            {{ form.item_name.label(class="form-label") }}
            {{ form.item_name(class="form-control", placeholder="e.g. Black leather wallet") }}
            {% for e in form.item_name.errors %}<div class="form-text text-danger">{{ e }}</div>{% endfor %}
          </div>

          <div class="mb-3">
            {{ form.description.label(class="form-label") }}
            {{ form.description(class="form-control", rows=4, placeholder="Color, distinguishing marks, contents&hellip;") }}
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              {{ form.category.label(class="form-label") }}
              {{ form.category(class="form-select") }}
            </div>
            <div class="col-md-6 mb-3">
              {{ form.date_lost.label(class="form-label") }}
              {{ form.date_lost(class="form-control") }}
            </div>
          </div>

          <div class="mb-3">
            {{ form.location.label(class="form-label") }}
            {{ form.location(class="form-control", placeholder="e.g. Library 2nd floor") }}
          </div>

          <div class="mb-4">
            {{ form.photo.label(class="form-label") }}
            {{ form.photo(class="form-control") }}
            {% for e in form.photo.errors %}<div class="form-text text-danger">{{ e }}</div>{% endfor %}
            <div class="form-text">Max 3 MB. JPG / PNG / GIF / WEBP.</div>
          </div>

          <div class="d-flex gap-2">
            {{ form.submit(class="btn btn-primary") }}
            <a class="btn btn-outline-secondary" href="{{ url_for('reports.index') }}">Cancel</a>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}
````

- [ ] **Step 2: Replace `app/templates/found/new.html`**

Use Write with:

````html
{% extends "base.html" %}
{% block title %}Log a found item{% endblock %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-md-7">
    <h2 class="page-title mb-4">Log a found item</h2>
    <div class="card">
      <div class="card-body">
        <form method="post" enctype="multipart/form-data" novalidate>
          {{ form.hidden_tag() }}

          <div class="mb-3">
            {{ form.item_name.label(class="form-label") }}
            {{ form.item_name(class="form-control", placeholder="e.g. Silver student ID") }}
            {% for e in form.item_name.errors %}<div class="form-text text-danger">{{ e }}</div>{% endfor %}
          </div>

          <div class="mb-3">
            {{ form.description.label(class="form-label") }}
            {{ form.description(class="form-control", rows=4) }}
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              {{ form.category.label(class="form-label") }}
              {{ form.category(class="form-select") }}
            </div>
            <div class="col-md-6 mb-3">
              {{ form.date_found.label(class="form-label") }}
              {{ form.date_found(class="form-control") }}
            </div>
          </div>

          <div class="mb-3">
            {{ form.location_found.label(class="form-label") }}
            {{ form.location_found(class="form-control", placeholder="e.g. Cafeteria table 4") }}
          </div>

          <div class="mb-4">
            {{ form.photo.label(class="form-label") }}
            {{ form.photo(class="form-control") }}
            {% for e in form.photo.errors %}<div class="form-text text-danger">{{ e }}</div>{% endfor %}
            <div class="form-text">Max 3 MB. JPG / PNG / GIF / WEBP.</div>
          </div>

          <div class="d-flex gap-2">
            {{ form.submit(class="btn btn-primary") }}
            <a class="btn btn-outline-secondary" href="{{ url_for('found.index') }}">Cancel</a>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}
````

- [ ] **Step 3: Replace `app/templates/claims/new.html`**

Use Write with:

````html
{% extends "base.html" %}
{% block title %}Claim this item{% endblock %}
{% block content %}
<a href="{{ url_for('matches.detail', match_id=match.match_id) }}" class="text-muted small">&larr; Back to match</a>

<div class="row justify-content-center mt-3">
  <div class="col-md-7">
    <h2 class="page-title mb-4">Claim this item</h2>

    <div class="card mb-4">
      <div class="card-body">
        <h5 class="mb-2">{{ match.found_item.item_name }}</h5>
        <p class="text-muted small mb-1">
          Found at {{ match.found_item.location_found or "&mdash;" }} on
          {{ match.found_item.date_found or "n/a" }}
        </p>
        <p class="small mb-0">
          Matched with your report:
          <a href="{{ url_for('reports.detail', report_id=match.lost_report.report_id) }}">
            {{ match.lost_report.item_name }}
          </a>
        </p>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <form method="post" novalidate>
          {{ form.hidden_tag() }}
          <div class="mb-3">
            {{ form.notes.label(class="form-label") }}
            {{ form.notes(class="form-control") }}
            <div class="form-text">Helps staff verify ownership when you pick up the item.</div>
          </div>
          <div class="d-flex gap-2">
            {{ form.submit(class="btn btn-primary") }}
            <a class="btn btn-outline-secondary"
               href="{{ url_for('matches.detail', match_id=match.match_id) }}">Cancel</a>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}
````

- [ ] **Step 4: Verify**

Run:
```
curl -s -o NUL -w "%{http_code}\n" http://127.0.0.1:8000/reports/new
curl -s -o NUL -w "%{http_code}\n" http://127.0.0.1:8000/found/new
```
Expected: `200` or `302` (302 if not logged in — that's fine, no Jinja errors).

- [ ] **Step 5: Commit**

```
git add app/templates/reports/new.html app/templates/found/new.html app/templates/claims/new.html
git commit -m "feat(ui): wrap new-record forms in card for consistent surface treatment"
```

---

## Task 9: Final verification

**Files:**
- Inspect-only

- [ ] **Step 1: Confirm git log shows 8 new commits**

Run: `git log --oneline -10`

Expected: 8 new commits (one per Task 1-8) with `feat(ui):` prefixes, plus the older commits from M1 and M2 below them.

- [ ] **Step 2: Confirm Flask boots cleanly one final time**

Run: `python -c "from app import create_app; app = create_app(); print('ok')"`
Expected: `ok`

- [ ] **Step 3: Confirm core pages return 200**

Run each:
```
curl -s -o NUL -w "/ -> %{http_code}\n" http://127.0.0.1:8000/
curl -s -o NUL -w "/auth/login -> %{http_code}\n" http://127.0.0.1:8000/auth/login
curl -s -o NUL -w "/auth/register -> %{http_code}\n" http://127.0.0.1:8000/auth/register
curl -s -o NUL -w "/static/css/style.css -> %{http_code}\n" http://127.0.0.1:8000/static/css/style.css
```
Expected: all `200`.

- [ ] **Step 4: Hand off to user for visual review**

The implementer's job is done. Ask the user to open `http://127.0.0.1:8000/` in a browser and click through:
- Landing page (logged out) — hero + 3 feature cards
- Register/Login — auth-shell + auth-card
- Dashboard (after login) — greeting + KPI cards + quick-action cards
- Lost reports list — page-header + segmented control + photo cards (or empty state)
- Found items list — page-header + photo cards (or empty state)
- A detail page (after seeding some test data) — status timeline visible

- [ ] **Step 5: No commit — Task 9 is verification only.**

---

## Acceptance criteria recap (from spec §9)

1. ✅ Full token block in `app/static/css/style.css`, no hex codes outside `:root`. — *Task 1.*
2. ✅ Inter loaded via single `<link>` in `base.html`, applied sitewide. — *Tasks 1, 2.*
3. ✅ Light navbar (no `navbar-dark bg-dark`). — *Task 2.*
4. ✅ Footer reads "IT106 — Caraga State University". — *Task 2.*
5. ✅ Every list page uses `.page-header` + `.empty-state`. — *Task 5.*
6. ✅ Lost-report and found-item detail pages render `.status-timeline`. — *Task 6.*
7. ✅ Auth pages render inside `.auth-shell` + `.auth-card`. — *Task 7.*
8. ✅ Status badges site-wide render as soft-tinted pills (`.badge.bg-*` overrides). — *Task 1.*
9. ✅ Primary buttons site-wide use `--color-primary` indigo. — *Task 1.*
10. ✅ Pages load without console/Jinja errors. — *Verified per-task.*
11. ✅ Existing routes still work — no backend code touched.
12. ✅ No new Python deps, no new JS files, no build step. — *No `pip install`, no JS files added.*
