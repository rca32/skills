# Repository instructions

This repository is the source of truth for personal, reusable Codex skills.

## Layout

- Put each installable skill at `skills/<skill-name>/`.
- Keep the required `SKILL.md`, recommended `agents/openai.yaml`, and only the
  scripts, references, or assets that the skill actually uses.
- Keep the root `README.md` skill table current.

## Authoring

- Use `writing-great-skills` for predictability, information hierarchy, and
  pruning; use `skill-creator` for scaffolding and validation.
- Prefer a concise model-invoked description only when automatic discovery is
  valuable. Keep procedural completion criteria observable.
- Keep each meaning in one authoritative location and disclose branch-specific
  reference behind a direct pointer from `SKILL.md`.
- Make fragile or concurrent operations deterministic with tested scripts.
- Keep credentials, account data, and machine-specific absolute paths out of
  committed skills.

## Validation

- Run `quick_validate.py` for every changed skill.
- Execute every changed bundled script against disposable inputs.
- Forward-test complex skills without leaking the intended answer and without
  mutating production systems.
- Review Standards and Spec independently before publishing.

## Distribution

- Treat `$CODEX_HOME/skills` as installed output; edit this repository instead.
- Publish the source change first, then reinstall the affected skill from
  `rca32/skills` and verify the installed copy.
