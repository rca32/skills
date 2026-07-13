# Codex Skills

Personal, reusable Codex skills maintained as the source of truth for daily
work. Each installable skill lives under `skills/<skill-name>/`.

## Available skills

| Skill | Purpose |
| --- | --- |
| `work-github-issue` | Collision-safe GitHub issue lifecycle for agents sharing one account |

## Install

Ask Codex to install `skills/work-github-issue` from `rca32/skills`, or run the
installed `skill-installer` workflow with that repository and path. Restart the
session after installation so the skill catalog refreshes.

Treat `$CODEX_HOME/skills` as installed output. Make changes in this repository,
validate them, publish them, and reinstall the affected skill.

## Validate

```bash
python3 skills/work-github-issue/scripts/test_issue_lease.py -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/work-github-issue
```
