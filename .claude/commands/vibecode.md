---
description: Code a task with the engineering + engineering-team knowledge bases loaded as context
argument-hint: <what you want to build, fix, or refactor>
---

# /vibecode — Engineering knowledge-base mode

You are about to perform an engineering task:

**Task:** $ARGUMENTS

## Knowledge bases to consult

Before touching code, scan these two local knowledge-base folders for patterns, skills, agents, plugins, references, and team practices that apply to the task:

- `engineering/` — engineering plugins (agenthub, autoresearch-agent, behuman, caveman, chaos-engineering, code-tour, data-quality-auditor, demo-video, docker-development, feature-flags-architect, …). Each plugin typically has a `SKILL.md`, optional `agents/`, `commands/`, `references/`, `scripts/`, and `.claude-plugin/plugin.json` describing capabilities.
- `engineering-team/` — senior-role agents and team-structure guides (`README.md`, `START_HERE.md`, `TEAM_STRUCTURE_GUIDE.md`, plus `senior-backend`, `senior-frontend`, `senior-architect`, `senior-data-engineer`, `senior-devops`, `code-reviewer`, `playwright-pro`, `a11y-audit`, etc.).

## Process

1. **Discover.** Use Glob/Grep over `engineering/**` and `engineering-team/**` to list candidate folders whose names match the task domain. Read each candidate's `SKILL.md`, `README.md`, or `CLAUDE.md` to confirm relevance.
2. **Load.** Read the relevant `references/`, `assets/`, or `scripts/` from the matched skills.
3. **Apply.** Execute the task using the patterns you loaded — follow the same conventions, file structure, and process the matched skills prescribe.
4. **Cite.** In your final message, list the specific knowledge-base files you drew from (e.g., `engineering/chaos-engineering/skills/chaos-engineering/references/experiment_design.md`) so the user can verify.

## Guardrails

- If the task is exploratory or unclear, ask one clarifying question before scanning the KB.
- If no skill in the KB matches, say so explicitly instead of inventing one — then proceed with first-principles engineering.
- Stay within the project's existing tech stack unless the task is explicitly about adopting a new tool.
