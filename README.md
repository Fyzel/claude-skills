# claude-skills

A collection of custom skills for [Claude Code](https://claude.ai/code). Each skill is a self-contained directory containing a `SKILL.md` and optional supporting reference files.

## Table of Contents

- [Skills](#skills)
  - [suno-songwriter](#suno-songwriter)
- [Skill Structure](#skill-structure)

---

## Skills

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
