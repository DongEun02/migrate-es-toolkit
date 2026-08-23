---
name: can-migrate-es-toolkit
description: Analyze a GitHub repository to determine whether its lodash dependency can be migrated to es-toolkit. Use when the user asks whether a specific repository can replace lodash or lodash-es with es-toolkit, wants migration feasibility or risk assessed, or wants a GitHub issue proposal for removing lodash.
---

# Assess lodash-to-es-toolkit migration

Accept a GitHub repository URL and an optional ISO 639-1 response language. Default to English.

This file is an adapter, not the workflow. It carries only what differs under Codex.

## Load the shared workflow

1. Resolve the real path of the directory containing this `SKILL.md`, following symlinks. Call it `<skill-directory>`.
2. Resolve `<source-root>` as three directories above `<skill-directory>`.
3. Read `<source-root>/.claude/commands/can-migrate-es-toolkit.md` completely before starting.

Do not run the assessment from this file alone. Every gate, execution rule, score band, verification tier, and report heading is defined there and nowhere else.

## Codex mappings

- `TodoWrite` → Codex's plan-tracking capability. Keep at most one step in progress.
- `WebFetch` and web-search instructions → Codex web access.
- `{skill_directory}/scripts/<name>.py` → `<source-root>/scripts/<name>.py`.
- `/can-migrate-es-toolkit <repository-url> [response-language]` → `$can-migrate-es-toolkit <repository-url> [response-language]`.
- The workflow's isolated-clone rule covers `<source-root>` too: when this skill is symlinked, the checkout it points into is not a scratch directory. Never modify it during an assessment.
