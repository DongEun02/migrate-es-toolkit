---
name: can-migrate-es-toolkit
description: Analyze a GitHub repository to determine whether its lodash dependency can be migrated to es-toolkit. Use when the user asks whether a specific repository can replace lodash or lodash-es with es-toolkit, wants migration feasibility or risk assessed, or wants a GitHub issue proposal for removing lodash.
---

# Assess lodash-to-es-toolkit migration

Accept a GitHub repository URL and an optional ISO 639-1 response language. Default to English.

## Load the shared workflow

1. Resolve the real path of the directory containing this `SKILL.md`, following symlinks. Call it `<skill-directory>`.
2. Resolve `<source-root>` as three directories above `<skill-directory>`.
3. Read `<source-root>/.claude/commands/can-migrate.md` completely before starting the assessment.
4. Follow its gates, scoring rules, verification tiers, and report requirements in order.

Treat the shared file as the canonical workflow. Apply these Codex-specific mappings while following it:

- Replace `TodoWrite` with Codex's plan-tracking capability and keep at most one step in progress.
- Use Codex web access for `WebFetch` or web-search instructions, and verify important claims against primary sources or repository code.
- Resolve `{skill_directory}/scripts/measure_bundle_size.py` as `<source-root>/scripts/measure_bundle_size.py`.
- Resolve `{skill_directory}/scripts/migrate_lodash_imports.py` as `<source-root>/scripts/migrate_lodash_imports.py`.
- Treat `/can-migrate-es-toolkit <repository-url> [response-language]` as `$can-migrate-es-toolkit <repository-url> [response-language]`.
- Use an isolated temporary directory for target-repository clones. Never modify the repository containing this skill during an assessment.

## Preserve workflow integrity

- Run the migration gate and early-termination checks before organizational research.
- Run Tier 0 before making any size-based claim.
- Do not draft an issue when the shared workflow says to skip it.
- Report exact measurements and verification levels; do not imply an unrun tier passed.
- Respond in the requested language while preserving the workflow's required English verdict labels verbatim.
