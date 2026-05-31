---
name: skill-validator
description: Validate Claude Code skill files (SKILL.md) against Anthropic's structural requirements. Use this skill whenever the user asks to validate, lint, check, or verify a skill file or skill structure. Triggers on "validate skill", "lint skill", "check skill", "verify SKILL.md", "does my skill meet requirements", or any request to confirm a skill is correctly structured before publishing or importing.
---

# Skill Validator

Validates `SKILL.md` files in the `skills/` directory against Anthropic's requirements using `skills/skill-validator/scripts/validate-skills.py`.

## What it checks

- `name` field present and matches the skill's directory name
- `description` field present
- No XML tags (`<...>`) in `description` — Claude Code rejects these on load
- Combined `description` + `when_to_use` length ≤ 1,536 characters
- Frontmatter parsed via PyYAML (handles block scalars correctly)
- Packaging simulation writes `skills/<name>/.test/<name>.skill` and reports archive size

## Run

Validate all skills:

```sh
# Windows
.venv/Scripts/python skills/skill-validator/scripts/validate-skills.py

# Linux / macOS
.venv/bin/python skills/skill-validator/scripts/validate-skills.py
```

Validate one skill by name:

```sh
# Windows
.venv/Scripts/python skills/skill-validator/scripts/validate-skills.py <skill-name>

# Linux / macOS
.venv/bin/python skills/skill-validator/scripts/validate-skills.py <skill-name>
```

Skip packaging simulation:

```sh
# Windows
.venv/Scripts/python skills/skill-validator/scripts/validate-skills.py --no-package

# Linux / macOS
.venv/bin/python skills/skill-validator/scripts/validate-skills.py --no-package
```

Exit code `0` = all pass. Exit code `1` = one or more failures.

## Setup

Requires Python in `.venv`:

```sh
python -m venv .venv
pip install -r requirements.txt
```
