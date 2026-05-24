# claude-skills

A collection of custom skills for [Claude Code](https://claude.ai/code). Each skill is a self-contained directory containing a `SKILL.md` and optional supporting reference files.

## Table of Contents

- [Skills](#skills)
  - [hand-off](#hand-off)
  - [suno-songwriter](#suno-songwriter)
- [Skill Structure](#skill-structure)

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

**Location:** [`skills/handoff/`](skills/handoff/)

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

**Location:** [`suno-songwriter/`](suno-songwriter/)

**Credit:** Tag reference and Suno documentation by [stayen](https://github.com/stayen/suno-reference).

---

## Skill Structure

```
<skill-name>/
  SKILL.md              # Skill instructions with YAML frontmatter (name, description)
  references/           # Supporting reference files (optional)
```

The `description` field in `SKILL.md` frontmatter controls when Claude Code auto-invokes the skill — write it to cover both canonical and fuzzy trigger phrases.

## Publishing

On every merge to `main`:

- Each skill directory is zipped into a `<skill-name>.skill` archive and published as a GitHub Release tagged `<skill-name>-v<N>`.
- The GitHub wiki is auto-generated from all skills: a `Home` index page plus one page per skill (frontmatter stripped, reference files appended).
