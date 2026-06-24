# claude-skills

A collection of custom skills for [Claude Code](https://claude.ai/code). Each skill is a self-contained directory containing a `SKILL.md` and optional supporting reference files. The repo also doubles as a [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) — each skill is installable individually as a plugin.

## Table of Contents

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Option A — Plugin marketplace (recommended)](#option-a--plugin-marketplace-recommended)
  - [Option B — Install a single skill manually](#option-b--install-a-single-skill-manually)
  - [Option C — Install from a packaged `.skill` release](#option-c--install-from-a-packaged-skill-release)
- [Skills](#skills)
  - [hand-off](#hand-off)
  - [skill-validator](#skill-validator)
  - [suno-songwriter](#suno-songwriter)
- [Skill Structure](#skill-structure)
- [Development](#development)

---

## Installation

Pick whichever method fits. The marketplace (Option A) is the easiest to keep updated; Options B and C install skills without registering a marketplace.

### Prerequisites

- [Claude Code](https://claude.ai/code) installed and authenticated (`claude` on your `PATH`).
- `git` (for the marketplace and for cloning this repo).

### Option A — Plugin marketplace (recommended)

This repo is a Claude Code plugin marketplace. Each skill is published as its own plugin, so you can install only the ones you want. Run these inside a Claude Code session:

```sh
# Register the marketplace (one time)
/plugin marketplace add Fyzel/claude-skills

# Install individual skills
/plugin install suno-songwriter@claude-skills
/plugin install hand-off@claude-skills
/plugin install pr-comment-triage@claude-skills
/plugin install github-doc-sync@claude-skills
/plugin install skill-validator@claude-skills

# Refresh after the marketplace updates
/plugin marketplace update claude-skills
```

Browse and toggle installed plugins anytime with `/plugin`. The marketplace catalog lives at [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json); each skill carries its own plugin manifest at `skills/<name>/.claude-plugin/plugin.json`.

### Option B — Install a single skill manually

Skills are file-based — no marketplace or `settings.json` registration required. Copy the skill directory to one of Claude Code's skill locations:

| Scope | Destination |
|---|---|
| Personal (all projects) | `~/.claude/skills/<skill-name>/` |
| Project-scoped | `<project>/.claude/skills/<skill-name>/` |

```sh
git clone https://github.com/Fyzel/claude-skills.git
# Personal install of one skill (Linux / macOS):
mkdir -p ~/.claude/skills
cp -r claude-skills/skills/suno-songwriter ~/.claude/skills/

# Windows (PowerShell):
# Copy-Item -Recurse claude-skills\skills\suno-songwriter $HOME\.claude\skills\
```

Claude Code discovers the skill on the next session — `SKILL.md` must sit at `<skill-name>/SKILL.md`.

### Option C — Install from a packaged `.skill` release

Every merge to `main` publishes each skill as a `<skill-name>.skill` archive on the [Releases](https://github.com/Fyzel/claude-skills/releases) page (tagged `<skill-name>-v<N>`). A `.skill` file is a flat zip of the skill directory. Download it and unzip into a skill location:

```sh
# Example: install suno-songwriter from a downloaded archive (Linux / macOS)
mkdir -p ~/.claude/skills/suno-songwriter
unzip suno-songwriter.skill -d ~/.claude/skills/suno-songwriter/
```

---

## Skills

### hand-off

**Trigger phrases:** `/hand-off`, "hand off", "delegate to a subagent", "spin this off", "pass this to a fresh agent", or any mention of context exhaustion and wanting to continue elsewhere.

Delegates a defined scope of work to a fresh Claude Code subagent with full context preserved across the boundary. Each handoff is recorded under `<project-root>/.handoffs/<feature>/`:

| File | Purpose |
|---|---|
| `input.md` | Brief written by parent agent: scope, context, constraints, success criteria |
| `output.md` | Results written by subagent (required completion criterion) |
| `baseline.txt` | Git state snapshot for recovery if `output.md` is missing (git projects only) |

**How it works:**

1. **Clarify** — confirms scope, context needed, and "done" criteria before writing anything.
2. **Set up** — creates `.handoffs/<feature>/`, resolves `.gitignore` question on first use in a git repo.
3. **Write `input.md`** — captures scope, context, current state, constraints, and success criteria.
4. **Spawn subagent** — uses the Task tool; subagent reads `input.md` and must write `output.md`.
5. **Synthesize** — verifies `output.md` exists, then summarizes results back into the parent conversation. Offers recovery options (diff reconstruction, re-run, manual inspect) if `output.md` is missing.

**Location:** [`skills/hand-off/`](skills/hand-off/)

---

### skill-validator

**Trigger phrases:** "validate skill", "lint skill", "check skill", "verify SKILL.md", or any request to confirm a skill is correctly structured before publishing or importing.

Validates `SKILL.md` files in the `skills/` directory against Anthropic's structural requirements:

| Check | Detail |
|---|---|
| `name` present | Must exist in frontmatter |
| `name` matches directory | `name: foo` must be in `skills/foo/` |
| `description` present | Must exist in frontmatter |
| Description length | `description` + `when_to_use` ≤ 1,536 chars |
| No XML tags in description | Claude Code rejects skills with `<tag>` syntax in description |
| Frontmatter delimited | Must open and close with `---` |

Packaging simulation writes a `.skill` archive to `skills/<name>/.test/<name>.skill` for local install testing.

**Location:** [`skills/skill-validator/`](skills/skill-validator/)

---

### suno-songwriter

**Trigger phrases:** "create a song", "write a song", "write lyrics", "create a Suno song", or any request for original lyrics — even without the word "Suno".

Composes original songs and delivers them as three copy-paste-ready blocks for the [Suno AI music generator](https://suno.com) (v5.5):

| Block | Paste into | Hard limit |
|---|---|---|
| Lyrics + meta tags | Suno **Lyrics** field | 5,000 chars |
| Style description | Suno **Styles** field | 1,000 chars |
| 10–20 title options | — | 100 chars each |

**How it works:**

1. **Interview** — asks about concept, mood, genre, instrumentation, vocals, pace, time signature, and language in a single batch. Skipped if you've already provided a full brief.
2. **Compose** — writes the song using [Suno meta tags](suno-songwriter/references/tag-reference-llm.md) for structure, dynamics, and vocal direction. Handles pronunciation rules (acronyms vs. initialisms), explicit content flagging, and non-English translation automatically.

**Location:** [`skills/suno-songwriter/`](skills/suno-songwriter/)

**Credit:** Tag reference and Suno documentation by [stayen](https://github.com/stayen/suno-reference).

---

## Skill Structure

```
.claude-plugin/
  marketplace.json        # Plugin marketplace catalog (lists every skill as a plugin)
skills/
  <skill-name>/
    SKILL.md              # Skill instructions with YAML frontmatter (name, description)
    .claude-plugin/
      plugin.json         # Plugin manifest — makes the skill installable via the marketplace
    scripts/              # Driver scripts bundled with the skill (optional)
    references/           # Supporting reference files (optional)
    .test/                # Local test artifacts — gitignored, not published
```

The `description` field in `SKILL.md` frontmatter controls when Claude Code auto-invokes the skill — write it to cover both canonical and fuzzy trigger phrases.

## Development

Requires Python 3.9+ and a virtual environment:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux / macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
pre-commit install
```

Validate all skill files and produce local `.skill` packages:

```sh
# Windows
.venv/Scripts/python skills/skill-validator/scripts/validate-skills.py

# Linux / macOS
.venv/bin/python skills/skill-validator/scripts/validate-skills.py
```

The validator also runs automatically on every commit that touches `skills/` (validation only — no packaging).

## License

Licensed under the [Apache License, Version 2.0](LICENSE).

## Publishing

On every merge to `main`:

- Each skill directory is zipped into a `<skill-name>.skill` archive (`.test/` excluded) and published as a GitHub Release tagged `<skill-name>-v<N>`.
- The GitHub wiki is auto-generated from all skills: a `Home` index page plus one page per skill (frontmatter stripped, reference files appended).
