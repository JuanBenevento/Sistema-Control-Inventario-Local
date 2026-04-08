# Skill Registry

**Delegator use only.** Any agent that launches sub-agents reads this registry to resolve compact rules, then injects them directly into sub-agent prompts. Sub-agents do NOT read this registry or individual SKILL.md files.

See `_shared/skill-resolver.md` for the full resolution protocol.

## User Skills

| Trigger | Skill | Path |
|---------|-------|------|
| When creating a GitHub issue, reporting a bug, or requesting a feature | issue-creation | /home/juanm/.config/opencode/skills/issue-creation/SKILL.md |
| When creating a pull request, opening a PR, or preparing changes for review | branch-pr | /home/juanm/.config/opencode/skills/branch-pr/SKILL.md |
| When user says "judgment day", "review adversarial", "dual review" | judgment-day | /home/juanm/.config/opencode/skills/judgment-day/SKILL.md |
| When user asks to create a new skill, add agent instructions, or document patterns for AI | skill-creator | /home/juanm/.config/opencode/skills/skill-creator/SKILL.md |

## Compact Rules

### issue-creation
- ALWAYS link to a GitHub issue before any PR or branch creation
- Issue title: concise, imperative mood (e.g., "Add dark mode support")
- Issue body: Problem → Expected → Actual → Steps to Reproduce
- Include labels: bug/feature/enhancement, priority, area/component
- For bugs: include error messages, stack traces, environment details

### branch-pr
- NEVER commit directly to main/master
- Branch naming: `type/issue-number-description` (e.g., `feat/42-dark-mode`)
- Commits: conventional commits (`fix:`, `feat:`, `docs:`, `refactor:`)
- PR title: same format as issue title
- PR description: Summary → Changes → Testing → Screenshots (if UI)

### judgment-day
- Launch TWO independent blind judges simultaneously
- Judges review WITHOUT knowledge of each other or the fix
- Synthesize findings: combine unique issues, deduplicate overlaps
- Apply fixes for CRITICAL issues immediately
- Re-judge after fixes; escalate if both fail after 2 iterations

### skill-creator
- Skill file: `SKILL.md` with YAML frontmatter (name, description, license, metadata)
- Description must include "Trigger:" line for automatic context detection
- Rules section: specific, actionable, no ambiguity
- Compact rules: 5-15 lines, sub-agent actionable, no fluff

## Project Conventions

No convention files found (AGENTS.md, CLAUDE.md, .cursorrules, etc.).

## Project Standards

| Category | Status |
|----------|--------|
| Python Version | 3.11 |
| Framework | PySide6 (Qt for Python) |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite |
| Architecture | Layered (models, database, repository, ui, utils) |
| Test Runner | NOT FOUND |
| Linter | NOT FOUND |
| Type Checker | NOT FOUND |
