# UI/UX Redesign — Design Spec ("Quiet Polish")

**Date:** 2026-05-19
**Milestone:** Frontend redesign (not a numbered milestone in the M1–M8 roadmap, but supports M6 screenshots and the "Frontend Design & Usability" 10-rubric-point category)
**Goal:** Replace the default Bootstrap-template look with a custom modern-minimal design system. Keep Bootstrap's grid + utility classes for layout; override every visual primitive (colors, buttons, cards, forms, navbar, tables, badges, alerts, pagination) through a substantial custom CSS theme layer. Aesthetic: quiet, polished, restrained — indigo accent on neutrals, soft shadows, generous whitespace, 8px corner radius.

---

## 1. Why this redesign

The current frontend is vanilla Bootstrap 5 with 18 lines of custom CSS. It reads as "Bootstrap demo" — generic, undifferentiated, and visibly templated. For the IT106 defense, M6 screenshots, and the 10-point "Frontend Design & Usability" rubric, this is the lowest-effort highest-impact upgrade available.

The chosen approach — **Quiet Polish** — restyles every Bootstrap surface in place using CSS variables and Bootstrap-class overrides, so we keep the grid/utility wins (huge timesaver) but the user-visible product stops looking like Bootstrap.

## 2. Scope

**In scope:**
- New custom CSS theme layer in `app/static/css/style.css` — fully rewritten (~400–500 lines).
- Inter font loaded once via a single `<link>` tag in `base.html`.
- `base.html` shell refactor: light navbar (replaces `navbar-dark bg-dark`), tighter footer ("ITE18" → "IT106 — Caraga State University"), updated alert markup.
- All 17 page templates updated to use new helper classes (e.g., `.badge-soft-warning`, `.btn-ghost`) and any structural tweaks the design requires (e.g., status timeline, sidebar-less auth shell).
- No new JavaScript. No build step. No CSS preprocessor. No new Python dependencies.
- Continues to use the existing Bootstrap 5 CDN load — we override Bootstrap, not replace it.

**Out of scope:**
- Dark mode (deferred; light-only for v1).
- Layout overhaul (sidebar nav, etc.) — top-nav stays.
- Icon library beyond inline SVG (no Font Awesome / Heroicons npm install). Lucide icons inlined as SVG where needed.
- Interactive JavaScript improvements (animations beyond CSS transitions, tooltips beyond Bootstrap's own, modals beyond Bootstrap's own).
- Server-side template logic changes (Jinja conditionals, route handlers, model code — all untouched).
- Responsive behavior beyond what the existing Bootstrap grid already provides — verified at desktop / tablet / mobile but no custom media queries beyond a few for typography sizes.

## 3. Tech approach

- **Bootstrap 5.3 stays** — loaded via CDN in `base.html`.
- **`app/static/css/style.css` is rewritten** as the theme layer, loaded *after* Bootstrap so it wins specificity by source order.
- **Pattern:** override Bootstrap's class names (`.btn`, `.btn-primary`, `.card`, `.alert`, etc.) directly. No `!important` needed — source order is enough.
- **Add new helper classes** where Bootstrap doesn't have an equivalent (e.g., `.badge-soft-warning`, `.btn-ghost`, `.status-timeline`).
- **Tokens** live in a single `:root { ... }` block at the top of the file. Every rule below references variables. No hex codes outside `:root`.
- **Inter** loaded with `<link rel="preconnect" href="https://fonts.googleapis.com"> <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin> <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">` — one weight-grouped request. Cached after first hit.

## 4. Design tokens

Single source of truth, top of `style.css`:

```css
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
  --color-primary-on:   #ffffff;

  /* Status tints (soft, not saturated) */
  --color-success: #047857;  --color-success-soft: #ecfdf5;
  --color-warning: #b45309;  --color-warning-soft: #fffbeb;
  --color-danger:  #b91c1c;  --color-danger-soft:  #fef2f2;
  --color-info:    #0e7490;  --color-info-soft:    #ecfeff;

  /* Spacing */
  --space-1: 4px;   --space-2: 8px;   --space-3: 12px;
  --space-4: 16px;  --space-5: 24px;  --space-6: 32px;  --space-7: 48px;

  /* Radii */
  --radius-sm: 6px;  --radius-md: 8px;  --radius-lg: 12px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-lg: 0 4px 12px rgba(0,0,0,0.06);

  /* Typography */
  --font-sans: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, monospace;
  --text-xs: 12px;  --text-sm: 13px;  --text-base: 14px;
  --text-lg: 16px;  --text-xl: 20px;  --text-2xl: 24px;  --text-3xl: 32px;
  --leading-tight: 1.25;  --leading-normal: 1.5;  --leading-relaxed: 1.625;
}
```

Body: `font-family: var(--font-sans); font-size: var(--text-base); color: var(--color-text); background: var(--color-bg); line-height: var(--leading-normal);`

## 5. Layout shell (`base.html`)

### 5.1 Navbar

Replace `<nav class="navbar navbar-expand-lg navbar-dark bg-dark">` with `<nav class="navbar navbar-expand-lg site-nav">`.

CSS:
```css
.site-nav {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: var(--space-3) 0;
  position: sticky; top: 0; z-index: 1000;
}
.site-nav .navbar-brand {
  font-size: var(--text-lg); font-weight: 600;
  color: var(--color-primary); letter-spacing: -0.01em;
}
.site-nav .nav-link {
  color: var(--color-text-muted);
  font-size: var(--text-sm); font-weight: 500;
  padding: var(--space-2) var(--space-3);
  position: relative;
}
.site-nav .nav-link:hover { color: var(--color-text); }
.site-nav .nav-link.active {
  color: var(--color-primary);
}
.site-nav .nav-link.active::after {
  content: ""; position: absolute; left: var(--space-3); right: var(--space-3);
  bottom: -8px; height: 2px; background: var(--color-primary); border-radius: 1px;
}
```

Right-side actions (notifications, dashboard, log out / log in, register) become ghost buttons + one primary indigo register button. The red `badge bg-danger` on the notifications button becomes a small indigo dot:

```css
.notif-dot {
  position: absolute; top: 6px; right: 6px;
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--color-primary);
}
```

### 5.2 Footer

Replace the existing footer with:
```html
<footer class="site-footer">
  <div class="container">
    Lost &amp; Found Management System · IT106 — Caraga State University
  </div>
</footer>
```

CSS:
```css
.site-footer {
  border-top: 1px solid var(--color-border);
  padding: var(--space-5) 0; margin-top: var(--space-7);
  color: var(--color-text-muted); font-size: var(--text-xs);
  text-align: center;
}
```

### 5.3 Page container

Override Bootstrap's `.container` for the main element only:
```css
main.container {
  max-width: 1120px;
  padding-top: var(--space-6); padding-bottom: var(--space-6);
}
```

### 5.4 Flash messages

Replace `.alert-{category}` rendering with soft-tinted alerts. Bootstrap's `alert-success/warning/danger/info` get overridden:
```css
.alert {
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  border: 1px solid;
}
.alert-success { background: var(--color-success-soft); color: var(--color-success); border-color: var(--color-success-soft); }
.alert-warning { background: var(--color-warning-soft); color: var(--color-warning); border-color: var(--color-warning-soft); }
.alert-danger,
.alert-error   { background: var(--color-danger-soft);  color: var(--color-danger);  border-color: var(--color-danger-soft); }
.alert-info    { background: var(--color-info-soft);    color: var(--color-info);    border-color: var(--color-info-soft); }
```

## 6. Core components

### 6.1 Buttons

```css
.btn {
  border-radius: var(--radius-md);
  font-size: var(--text-sm); font-weight: 500;
  padding: var(--space-2) var(--space-4);
  height: 36px; line-height: 1; border: 1px solid transparent;
  transition: background 120ms ease, border-color 120ms ease, color 120ms ease;
  display: inline-flex; align-items: center; gap: var(--space-2);
}
.btn-sm { height: 28px; padding: var(--space-1) var(--space-3); font-size: var(--text-xs); }
.btn-lg { height: 44px; padding: var(--space-3) var(--space-5); font-size: var(--text-base); }

.btn-primary {
  background: var(--color-primary); color: var(--color-primary-on);
}
.btn-primary:hover { background: var(--color-primary-hover); color: var(--color-primary-on); }

.btn-outline-primary,
.btn-outline-secondary,
.btn-outline-light,
.btn-outline-warning {
  background: transparent; color: var(--color-text);
  border-color: var(--color-border-strong);
}
.btn-outline-primary:hover,
.btn-outline-secondary:hover,
.btn-outline-light:hover,
.btn-outline-warning:hover {
  background: var(--color-surface-subtle); color: var(--color-text);
}

.btn-light { background: var(--color-surface); border-color: var(--color-border-strong); color: var(--color-text); }
.btn-light:hover { background: var(--color-surface-subtle); color: var(--color-text); }

/* New: ghost button — no border, no bg, hover tint */
.btn-ghost { background: transparent; color: var(--color-text-muted); border-color: transparent; }
.btn-ghost:hover { background: var(--color-surface-subtle); color: var(--color-text); }
```

### 6.2 Cards

```css
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
.card-body { padding: var(--space-4); }
.card-title { font-size: var(--text-lg); font-weight: 600; margin-bottom: var(--space-1); }
.card-text { font-size: var(--text-sm); color: var(--color-text-muted); }

/* Stretched-link hover lifts the card very slightly */
.card:has(.stretched-link:hover) { box-shadow: var(--shadow-md); }
```

Photo cards (list-page item cards) keep `.card-img-top` but with `border-top-left-radius: var(--radius-lg); border-top-right-radius: var(--radius-lg);`.

The "no photo" placeholder div on list pages:
```css
.card-photo-empty {
  height: 200px;
  background: var(--color-surface-subtle);
  color: var(--color-text-subtle);
  font-size: var(--text-xs); text-transform: uppercase; letter-spacing: 0.05em;
  display: flex; align-items: center; justify-content: center;
}
```

### 6.3 Forms

```css
.form-label { display: block; font-size: var(--text-sm); font-weight: 500; margin-bottom: var(--space-1); color: var(--color-text); }
.form-control, .form-select {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-base);
  color: var(--color-text);
  width: 100%; line-height: var(--leading-normal);
  transition: border-color 120ms ease, box-shadow 120ms ease;
}
.form-control:focus, .form-select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-soft);
  outline: none;
}
.form-control::placeholder { color: var(--color-text-subtle); }
.form-text { font-size: var(--text-xs); color: var(--color-text-muted); margin-top: var(--space-1); }

.form-control.is-invalid { border-color: var(--color-danger); }
.invalid-feedback { color: var(--color-danger); font-size: var(--text-xs); }
```

### 6.4 Tables

```css
.table {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border-collapse: separate; border-spacing: 0;
}
.table th {
  background: var(--color-surface-subtle);
  color: var(--color-text-muted);
  font-size: var(--text-xs); font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.05em;
  padding: var(--space-3) var(--space-4); text-align: left;
  border-bottom: 1px solid var(--color-border);
}
.table td {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm); color: var(--color-text);
  border-bottom: 1px solid var(--color-border);
}
.table tr:last-child td { border-bottom: 0; }
.table tr:hover td { background: var(--color-surface-subtle); }
```

Bootstrap's `.table-striped` is overridden to be a no-op (rules above already give clean rows). Don't use it.

### 6.5 Badges (status indicators)

New soft-tinted badge classes. Bootstrap's existing `.badge.bg-*` rules get overridden to point at the soft palette. We also add `.badge-soft-*` aliases for clarity:

```css
.badge {
  display: inline-flex; align-items: center;
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs); font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.04em;
  border-radius: 9999px; line-height: 1;
}

.badge.bg-warning, .badge-soft-warning { background: var(--color-warning-soft); color: var(--color-warning); }
.badge.bg-info,    .badge-soft-info    { background: var(--color-info-soft);    color: var(--color-info); }
.badge.bg-primary, .badge-soft-primary { background: var(--color-primary-soft); color: var(--color-primary); }
.badge.bg-success, .badge-soft-success { background: var(--color-success-soft); color: var(--color-success); }
.badge.bg-danger,  .badge-soft-danger  { background: var(--color-danger-soft);  color: var(--color-danger); }
.badge.bg-secondary, .badge-soft-secondary {
  background: var(--color-surface-subtle); color: var(--color-text-muted);
}
```

This means existing template code like `<span class="badge bg-warning">Reported</span>` automatically uses the new soft tint — no template changes required for that.

### 6.6 Pagination

Strip Bootstrap's heavy pagination styling:
```css
.pagination {
  display: flex; justify-content: center; gap: var(--space-3);
  padding: 0; margin-top: var(--space-5);
  list-style: none;
}
.page-item .page-link {
  background: transparent; border: 0;
  color: var(--color-text-muted);
  font-size: var(--text-sm); font-weight: 500;
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
}
.page-item.disabled .page-link { color: var(--color-text-subtle); }
```

## 7. Page-level treatments

### 7.1 Landing page (`index.html`)

Hero (top of page):
```html
<section class="hero">
  <h1 class="hero-title">Lost &amp; Found Tracking</h1>
  <p class="hero-subtitle">Report lost items, log found ones, and reunite them — all in one place.</p>
  <div class="hero-cta">...buttons...</div>
</section>
```

CSS:
```css
.hero { text-align: center; padding: var(--space-7) 0 var(--space-6); }
.hero-title { font-size: var(--text-3xl); font-weight: 700; letter-spacing: -0.02em; margin-bottom: var(--space-3); }
.hero-subtitle { font-size: var(--text-lg); color: var(--color-text-muted); max-width: 640px; margin: 0 auto var(--space-5); }
.hero-cta { display: flex; gap: var(--space-3); justify-content: center; flex-wrap: wrap; }
```

Below the hero, the existing 3-column feature cards get the new card style automatically. Add an inline Lucide SVG icon (24px, `--color-primary`) above each card title.

### 7.2 Dashboard (`main/dashboard.html`)

Welcome strip:
```html
<div class="dashboard-greeting">
  <h1>Hi, {{ user.name }}</h1>
  <span class="badge badge-soft-primary">{{ user.role|capitalize }}</span>
</div>
```

CSS:
```css
.dashboard-greeting h1 { font-size: var(--text-2xl); font-weight: 600; margin-bottom: var(--space-2); letter-spacing: -0.01em; }
.dashboard-greeting { margin-bottom: var(--space-6); }
```

KPI cards: existing `.card` style applies. Override the conditional `border-warning` / `border-success` / `border-info` accents to be a **left 3px border** instead of a full border:
```css
.card.border-warning { border-color: var(--color-border); border-left: 3px solid var(--color-warning); }
.card.border-success { border-color: var(--color-border); border-left: 3px solid var(--color-success); }
.card.border-info    { border-color: var(--color-border); border-left: 3px solid var(--color-info); }
.card.border-warning .card-body,
.card.border-success .card-body,
.card.border-info    .card-body { padding-left: calc(var(--space-4) - 3px); }
```

KPI numbers (`<h2>`) inside KPI cards: override to be 32px with `letter-spacing: -0.02em` so they feel like stats, not headings:
```css
.card-body h2 { font-size: var(--text-3xl); font-weight: 600; letter-spacing: -0.02em; line-height: 1; }
.card-body h6 { font-size: var(--text-xs); font-weight: 500; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: var(--space-1); }
```

Quick-action cards (existing 3-column grid below KPIs): default card style applies. Inline Lucide icon (20px) prepended to each `.card-title`.

### 7.3 List pages (lost / found / claims / matches / notifications / admin/users)

Header strip standardized:
```html
<div class="page-header">
  <div>
    <h2 class="page-title">Lost reports</h2>
    <div class="segmented-control">...</div>
  </div>
  <a class="btn btn-primary" href="...">+ Report a lost item</a>
</div>
```

CSS:
```css
.page-header {
  display: flex; justify-content: space-between; align-items: flex-end;
  flex-wrap: wrap; gap: var(--space-3); margin-bottom: var(--space-5);
}
.page-title { font-size: var(--text-2xl); font-weight: 600; letter-spacing: -0.01em; margin: 0; }
.segmented-control { display: inline-flex; background: var(--color-surface-subtle); border-radius: var(--radius-md); padding: 2px; margin-top: var(--space-2); }
.segmented-control a {
  font-size: var(--text-xs); font-weight: 500; padding: var(--space-1) var(--space-3);
  color: var(--color-text-muted); border-radius: var(--radius-sm); text-decoration: none;
}
.segmented-control a.active { background: var(--color-surface); color: var(--color-text); box-shadow: var(--shadow-sm); }
```

The btn-group "All / Mine" toggle on reports/found list pages becomes `.segmented-control`.

Item-card photo grid (3-column on desktop, 2 on tablet, 1 on mobile) — uses default `.card` + a hover-shadow rule:
```css
.item-card:hover { box-shadow: var(--shadow-md); }
```

Empty state:
```html
<div class="empty-state">
  <svg class="empty-icon" ...></svg>
  <h3 class="empty-title">No reports yet</h3>
  <p class="empty-text">Be the first to file a lost-item report.</p>
  <a class="btn btn-primary" href="...">+ File a report</a>
</div>
```

CSS:
```css
.empty-state { text-align: center; padding: var(--space-7) var(--space-4); }
.empty-icon { width: 48px; height: 48px; color: var(--color-text-subtle); margin-bottom: var(--space-4); }
.empty-title { font-size: var(--text-xl); font-weight: 600; margin-bottom: var(--space-2); }
.empty-text { color: var(--color-text-muted); margin-bottom: var(--space-5); max-width: 360px; margin-left: auto; margin-right: auto; }
```

### 7.4 Detail pages (lost report / found item)

Two-column on desktop, single-column on mobile. Existing Bootstrap `row` / `col-md-*` grid handles responsiveness.

Status timeline component (replaces lonely `<span class="badge">`):
```html
<ol class="status-timeline">
  <li class="status-step status-step--done">Reported</li>
  <li class="status-step status-step--active">Matched</li>
  <li class="status-step">Claimed</li>
  <li class="status-step">Closed</li>
</ol>
```

CSS:
```css
.status-timeline { display: flex; list-style: none; padding: 0; margin: var(--space-4) 0; gap: var(--space-2); }
.status-step {
  position: relative; flex: 1; padding-top: var(--space-4);
  font-size: var(--text-xs); font-weight: 500; color: var(--color-text-subtle);
  text-transform: uppercase; letter-spacing: 0.04em; text-align: left;
}
.status-step::before {
  content: ""; position: absolute; top: 0; left: 0;
  width: 12px; height: 12px; border-radius: 50%;
  background: var(--color-border); border: 2px solid var(--color-surface);
  box-shadow: 0 0 0 2px var(--color-border);
}
.status-step::after {
  content: ""; position: absolute; top: 5px; left: 12px; right: 0;
  height: 2px; background: var(--color-border);
}
.status-step:last-child::after { display: none; }
.status-step--done    { color: var(--color-success); }
.status-step--done::before, .status-step--done::after { background: var(--color-success); box-shadow: 0 0 0 2px var(--color-success); }
.status-step--active { color: var(--color-primary); }
.status-step--active::before { background: var(--color-primary); box-shadow: 0 0 0 2px var(--color-primary); }
```

Each detail page's Jinja template builds the timeline `<ol>` based on the entity's current `status`, with prior states marked `status-step--done`, the current state marked `status-step--active`, and future states left plain.

**Per-entity stage definitions** (these mirror the model enums in [app/models.py](../../../app/models.py)):

- **Lost report** (`LostReport.status`): `Reported → Matched → Claimed → Closed`. Four steps.
- **Found item** (`FoundItem.status`): `Logged → Matched → Released`. Three steps.
- **Claim** (`Claim.status`): `Pending → Approved → Released`, with `Rejected` as a terminal branch off Pending. Render four steps: `Pending → Approved → Released` as the main row, and if the claim was rejected, replace the second-and-third steps with a single `Rejected` step styled with `--color-danger` (no further progression). Picking one of the two visual treatments per template is fine — the implementer can keep it simple by showing the main 3-step row and adding a small `.badge-soft-danger` "Rejected" pill beside the timeline when `status == "rejected"`.

Match-candidates row on lost-report detail: horizontal scroll of mini candidate cards, each showing photo thumbnail + item name + confidence score in a `.badge-soft-primary`.

### 7.5 Auth pages (`auth/login.html`, `auth/register.html`)

Branding-only navbar variant (no nav links, just brand + tiny "Back" link). Centered card on a `--color-bg` page:

```html
<div class="auth-shell">
  <div class="auth-card">
    <h1 class="auth-title">Log in</h1>
    <form>...</form>
    <p class="auth-footer">No account? <a href="...">Register</a></p>
  </div>
</div>
```

CSS:
```css
.auth-shell { display: flex; align-items: center; justify-content: center; min-height: calc(100vh - 200px); padding: var(--space-5) var(--space-4); }
.auth-card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-lg); box-shadow: var(--shadow-md); padding: var(--space-6); width: 100%; max-width: 400px; }
.auth-title { font-size: var(--text-xl); font-weight: 600; margin-bottom: var(--space-5); letter-spacing: -0.01em; }
.auth-footer { font-size: var(--text-sm); color: var(--color-text-muted); margin: var(--space-5) 0 0; text-align: center; }
.auth-footer a { color: var(--color-primary); font-weight: 500; }
```

Auth pages get a minimal `{% block navbar %}` override on `base.html` (or a flag passed by the route) — but the simplest path is just to use the existing navbar with the auth/* templates and accept that "Lost / Found / etc." links won't be there because the user isn't authenticated. The current `{% if current_user.is_authenticated %}` block in base.html already hides the nav for unauth visitors. So no shell change is needed.

## 8. Implementation notes

### 8.1 File organization

```
app/static/css/
└── style.css          # single file, ~400–500 lines, fully rewritten
app/templates/
├── base.html          # navbar/footer rewrite, Inter <link>, alert markup
├── index.html         # hero structure + 3 feature cards with inline SVG icons
├── main/dashboard.html # greeting strip, KPI/quick-action grid (new classes only)
├── reports/list.html  # page-header, segmented-control, item-card, empty-state
├── reports/detail.html # status-timeline, match-candidates row
├── reports/new.html   # form-label / form-control conventions (no change to fields)
├── found/list.html, found/detail.html, found/new.html
├── matches/list.html, matches/detail.html
├── claims/list.html, claims/detail.html, claims/new.html
├── notifications/list.html
├── admin/users.html
└── auth/login.html, auth/register.html
```

### 8.2 Bootstrap classes the design REPLACES (no template change needed)

These selectors are overridden in style.css; existing template usage continues to work:
- `.btn`, `.btn-primary`, `.btn-outline-*`, `.btn-light`, `.btn-sm`, `.btn-lg`
- `.card`, `.card-body`, `.card-title`, `.card-text`, `.card-img-top`
- `.form-label`, `.form-control`, `.form-select`, `.form-text`, `.invalid-feedback`
- `.table`, `.table thead/tbody/tr/th/td`
- `.badge`, `.badge.bg-*`
- `.alert`, `.alert-*`
- `.pagination`, `.page-item`, `.page-link`
- `.navbar`, `.navbar-brand`, `.nav-link`

### 8.3 Bootstrap classes the design ADDS (templates need to be edited to use them)

These are new helper classes that don't exist in Bootstrap; templates must opt in:
- `.site-nav`, `.site-footer`
- `.btn-ghost`
- `.badge-soft-warning`, `.badge-soft-info`, `.badge-soft-primary`, `.badge-soft-success`, `.badge-soft-danger`, `.badge-soft-secondary`
- `.hero`, `.hero-title`, `.hero-subtitle`, `.hero-cta`
- `.page-header`, `.page-title`
- `.segmented-control`
- `.item-card`, `.card-photo-empty`
- `.empty-state`, `.empty-icon`, `.empty-title`, `.empty-text`
- `.status-timeline`, `.status-step`, `.status-step--done`, `.status-step--active`
- `.dashboard-greeting`
- `.auth-shell`, `.auth-card`, `.auth-title`, `.auth-footer`
- `.notif-dot`

### 8.4 Inline Lucide SVG icons

We don't pull in a JS icon library. Instead, copy raw SVG markup from <https://lucide.dev> for the few icons we need:
- `search` — landing feature card "Report a lost item"
- `package` — landing feature card "Log a found item"
- `circle-check` — landing feature card "Track status"
- `bell` — navbar notifications button
- `plus` — primary "+ File a report" buttons
- `arrow-right` — small inline action arrows

All inlined directly in templates with `class="icon"` and styled by:
```css
.icon { width: 16px; height: 16px; stroke-width: 2; vertical-align: -2px; }
.icon-lg { width: 24px; height: 24px; }
.icon-xl { width: 48px; height: 48px; }
```

### 8.5 Order of operations during implementation

1. **Tokens + body** — write `:root`, replace `body` rule. Verify Inter loads (visit any page).
2. **Layout shell** — rewrite navbar + footer markup in `base.html`, restyle. Verify on landing.
3. **Buttons** — override Bootstrap btn rules. Verify on landing CTA + auth pages.
4. **Cards** — override Bootstrap card rules. Verify on landing feature cards + dashboard KPI cards.
5. **Forms** — override Bootstrap form rules. Verify on `reports/new.html` and auth pages.
6. **Tables** — override Bootstrap table rules. Verify on `admin/users.html`.
7. **Badges** — override `.badge.bg-*`, add `.badge-soft-*`. Verify status badges on list/detail pages.
8. **Alerts** — override `.alert-*`. Verify by triggering any flash message (e.g., log out then log back in, or submit an invalid form, to surface a flash).
9. **Pagination** — override `.pagination`. Verify on `reports/list.html` after seeding a few reports.
10. **Landing page** — add `.hero`, `.hero-title`, `.hero-subtitle`, `.hero-cta`. Inline icons.
11. **Dashboard** — add `.dashboard-greeting`, restyle KPI cards. Inline icons on quick-action cards.
12. **List pages** — add `.page-header`, `.segmented-control`, `.item-card`, `.card-photo-empty`, `.empty-state` to reports/list.html, found/list.html, claims/list.html, matches/list.html, notifications/list.html, admin/users.html.
13. **Detail pages** — add `.status-timeline` to reports/detail.html, found/detail.html, claims/detail.html, matches/detail.html.
14. **Auth pages** — rewrite login.html and register.html with `.auth-shell` / `.auth-card`.
15. **New forms** — verify reports/new.html, found/new.html, claims/new.html.

Each step ends with a manual browser check — load the affected page in the dev server and confirm the visual matches the spec. No automated visual regression test exists in this codebase; the verification is eyeballing.

## 9. Acceptance criteria

The redesign is complete when:

1. `app/static/css/style.css` contains the full token block (§4), is loaded after Bootstrap in `base.html`, and every hex color anywhere in the file is sourced from `:root` (no inline hex codes outside `:root`).
2. Inter is loaded via a single `<link>` in `base.html` and applied site-wide through `body { font-family: var(--font-sans); }`.
3. The navbar is light (`--color-surface` background, 1px bottom border) — not the original `navbar-dark bg-dark`.
4. The footer reads "Lost & Found Management System · IT106 — Caraga State University" (not the original "ITE18" text).
5. Every list page (reports, found, claims, matches, notifications, admin/users) uses the new `.page-header` + `.segmented-control` (where applicable) + `.empty-state` markup.
6. Lost-report and found-item detail pages render the `.status-timeline` component reflecting the item's current status.
7. Auth pages (login, register) render inside `.auth-shell` + `.auth-card`.
8. Status badges across the app render as soft-tinted pills (not Bootstrap's saturated colors).
9. Primary buttons site-wide use `--color-primary` indigo (not Bootstrap's `#0d6efd`).
10. Visiting `http://127.0.0.1:8000/` and clicking through 4-5 pages renders without console errors, without HTML validation errors, and visibly matches the design described in §5–§7. Confirmed by manual eyeballing in Chrome at desktop (1440px), tablet (768px), and mobile (375px) viewports.
11. All existing routes still work — the redesign does not break any backend behavior, form submission, or API endpoint.
12. No new Python dependencies. No new JavaScript files. No build step.

## 10. What this unblocks

- **M6 (system screenshots):** every screenshot now has a consistent, polished design language. Login → dashboard → list → detail → form sequence renders as a single intentional product.
- **Rubric category "Frontend Design & Usability" (10 pts):** the project moves from "vanilla Bootstrap" (5–6 pts realistic) to "custom design system on top of Bootstrap" (9–10 pts realistic).
- **Defense (M7):** clear talking point — "I built a custom design system using CSS variables and Bootstrap class overrides; here's the token file and here's how each primitive is themed."
