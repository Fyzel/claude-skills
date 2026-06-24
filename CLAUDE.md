# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

A collection of custom **Claude Code skills** — prompt-driven instruction sets that Claude Code loads on demand to handle specific tasks. Skills are plain Markdown files with YAML frontmatter. Python tooling (`requirements.txt`, `.venv`) exists for validation and pre-commit hooks; there is no application build system or test suite.

## Skill File Structure

Each skill lives under the `skills/` directory:

```
skills/
  <skill-name>/
    SKILL.md              # The skill itself (required)
    references/           # Supporting reference material (optional)
      <reference>.md
```

`SKILL.md` must begin with YAML frontmatter:

```yaml
---
name: <kebab-case-identifier>
description: <natural-language trigger description>
---
```

The `description` field is the most critical part of any skill. Claude Code reads it to decide whether to auto-invoke the skill in a given conversation. It should:
- Cover the canonical trigger phrases ("create a song", "write lyrics")
- Cover fuzzy/adjacent triggers ("turning a poem into a song", "requesting a chorus")
- Explicitly note when to trigger even without the primary keyword ("even when the user does not say the word 'Suno'")

## Plugin Marketplace

This repo doubles as a **Claude Code plugin marketplace**, so each skill is installable individually as a plugin.

- `.claude-plugin/marketplace.json` (repo root) is the catalog. It lists one plugin entry per skill, each with a relative `source` pointing at the skill directory (e.g. `"./skills/suno-songwriter"`).
- Each `skills/<name>/.claude-plugin/plugin.json` is that skill's plugin manifest. Because the skill's `SKILL.md` sits at the plugin root (no nested `skills/` dir, no `skills` manifest field), Claude Code auto-loads it as a single-skill plugin; the invocation name comes from the `SKILL.md` frontmatter `name`.
- Users install with `/plugin marketplace add Fyzel/claude-skills` then `/plugin install <skill-name>@claude-skills`.

When adding a new skill, also add a matching entry to `marketplace.json` and a `.claude-plugin/plugin.json` in the skill directory, then validate both:

```sh
claude plugin validate .                       # marketplace.json
claude plugin validate ./skills/<name> --strict  # the skill's plugin manifest
```

The `.skill` publishing pipeline (below) excludes `.claude-plugin/` from the archive, so the plugin manifest does not leak into the Agent Skill releases.

## Reference Files

Large reference files are too big to read in full. Skills that use them must instruct Claude to **scan section headers first**, then read only the relevant entries for the current task. When editing reference files, preserve the heading structure — it is the navigation surface.

## Adding a New Skill

1. Create `skills/<skill-name>/SKILL.md` with frontmatter (`name`, `description`) and the full skill instructions.
2. Install the skill by placing it at `~/.claude/skills/<skill-name>/` (personal, all projects) or `.claude/skills/<skill-name>/` (project-scoped). Skills are file-based — no settings.json registration required.
3. If the skill references large lookup tables or tag catalogs, put them under `skills/<skill-name>/references/` and instruct the skill to read them selectively by section.
4. Add a `.claude-plugin/plugin.json` in the skill directory and a matching plugin entry in `.claude-plugin/marketplace.json` so the skill is installable from the marketplace (see [Plugin Marketplace](#plugin-marketplace)).
5. Run the skill validator to confirm structure before committing: `skills/skill-validator/scripts/validate-skills.py`

## Skill Authoring Conventions

- **Two-phase structure** works well for creative/generation skills: an *interview* phase to gather the brief, then a *composition/output* phase. Skip the interview if the user already supplied sufficient context.
- **Hard limits vs. advisory targets**: distinguish between limits that cause silent failures in downstream tools (hard — non-negotiable) and optimal ranges that improve quality (advisory — state them, but don't enforce them as gates).
- **Output as fenced code blocks**: anything the user needs to copy-paste verbatim should be in its own fenced code block with nothing extra inside.
- **Character counts**: when a downstream tool has a character limit, compute counts — do not estimate.

## Branch Flow and CI/CD

This repo uses a three-branch promotion pipeline: `dev` → `test` → `main`.

- Push to `dev` automatically opens a PR promoting `dev` → `test`.
- Push to `test` automatically opens a PR promoting `test` → `main`.
- Merge to `main` triggers skill packaging/publishing and wiki publishing.
- All changes require review from @Fyzel (enforced via CODEOWNERS).

All commits must be GPG-signed. Configure git signing before committing:
```sh
git config commit.gpgsign true
```

Branch naming conventions (all cut from `dev`, PR back into `dev`):
- `feat/*` — new skills or features
- `doc/*` — documentation-only updates

Promotion PRs require two GitHub repo settings configured:
- **Secret** `PROMOTE_TOKEN` — a PAT with `repo` scope (used to open PRs across branches; `GITHUB_TOKEN` cannot open PRs targeting protected branches in some configurations).
- **Variable** `PROMOTION_ASSIGNEE` — GitHub username to assign promotion PRs to.

## Skill Publishing

On every merge to `main`, two workflows run:

**`publish-skills.yml`** — discovers skill directories under `skills/*/`, zips each one into `<skill-name>.skill` (flat archive — no wrapping directory), and creates a GitHub Release tagged `<skill-name>-v<count+1>`, where `count` is the number of existing matching tags for that skill. Releases are idempotent: an existing tag is skipped, not an error.

The `.skill` archive contains exactly the `skills/<skill-name>/` directory contents at the zip root (flat — no wrapping directory):
```
SKILL.md
references/
  <reference>.md
```

**`publish-wiki.yml`** — builds the GitHub repo wiki from skills. The `Home.md` page is a generated index table (skill name + description from frontmatter). Each skill gets its own wiki page: the `SKILL.md` content with frontmatter stripped, followed by any files under `references/` appended verbatim. The wiki is only updated when content changes.

## Python Tooling

Python tooling is managed via `.venv` and `requirements.txt`:

```sh
python -m venv .venv
pip install -r requirements.txt
```

Packages: `pylint`, `bandit`, `pre-commit`, `PyYAML`.

## Pre-commit Hooks

Pre-commit is configured with five hooks (`.pre-commit-config.yaml`). All run against local tools that must be installed:

- **actionlint** — lints GitHub Actions workflow files (requires `actionlint`)
- **package-skills** — validates all `SKILL.md` files on any commit touching `skills/` (requires `.venv`)
- **trivy-secrets** — secret detection scan of the whole repo (requires `trivy`)
- **pylint** — lints any Python files (requires `pylint`)
- **bandit** — security scan of any Python files (requires `bandit -r -ll`)

Install hooks after cloning:
```sh
pre-commit install
```

Run all hooks manually:
```sh
pre-commit run --all-files
```
