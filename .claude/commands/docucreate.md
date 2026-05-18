---
description: Create a document using the patterns and templates in the documentation/ knowledge base
argument-hint: <document type or topic — e.g., "sprint plan for M2", "API audit", "growth strategy">
---

# /docucreate — Documentation-base mode

You are about to create a document:

**Topic / type:** $ARGUMENTS

## Knowledge base to consult

Before drafting anything, scan the local `documentation/` folder for the closest matching style, structure, and template. The folder contains:

- **Top-level reference docs** — `GIST_CONTENT.md`, `GROWTH_STRATEGY.md`, `PYTHON_TOOLS_AUDIT.md`, `TEST_COVERAGE_ANALYSIS.md`, `WORKFLOW.md`
- **Sprint deliverables** — `documentation/delivery/sprint-*/` containing `PROGRESS.md`, `context.md`, `plan.md` per sprint
- **Implementation plans** — `documentation/implementation/` containing reimplementation plans, refactoring plans, marketing-skills plans, monthly implementation plans

Each subfolder has its own conventions (headings, tables, status emojis, link styles). Read them before drafting.

## Process

1. **Discover.** Glob `documentation/**` and read the file/folder names. Identify 1–3 existing documents that most resemble what the user is asking for.
2. **Load.** Read those 1–3 documents fully so you absorb their structure, tone, heading hierarchy, table conventions, and length.
3. **Outline.** Produce a short outline (headings only) and confirm with the user before drafting the full document — unless the user has told you to draft straight through.
4. **Draft.** Write the document following the closest template's style. Match its formatting, voice, and level of detail.
5. **Place.** Save the document in the most appropriate location:
   - One-off audits / strategies → `documentation/<NAME>.md`
   - Sprint work → `documentation/delivery/sprint-<date>/`
   - Implementation plans → `documentation/implementation/`
   - If a brand-new category, propose the path and confirm with the user.
6. **Cite.** In your final message, list the existing docs you modeled the new one after.

## Guardrails

- Match the existing style — don't invent a new template if a close one exists.
- Use absolute or repo-root-relative Markdown links (the existing docs do).
- Keep the document focused on a single deliverable. If the topic is too broad, propose splitting it into multiple documents first.
- Never overwrite an existing document silently. If a same-named file exists, ask before replacing.
