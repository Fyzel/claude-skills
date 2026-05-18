# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

A collection of custom **Claude Code skills** — prompt-driven instruction sets that Claude Code loads on demand to handle specific tasks. Skills are plain Markdown files with YAML frontmatter; there is no build system, package manager, or test suite.

## Skill File Structure

Each skill lives in its own subdirectory:

```
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

## Reference Files

Large reference files (like `suno-songwriter/references/tag-reference.md`) are too big to read in full. Skills that use them must instruct Claude to **scan section headers first**, then read only the relevant entries for the current task. When editing reference files, preserve the heading structure — it is the navigation surface.

## Adding a New Skill

1. Create `<skill-name>/SKILL.md` with frontmatter (`name`, `description`) and the full skill instructions.
2. Register it in the Claude Code settings so it appears in the skill list (typically via the plugin or settings.json `skills` array — check your local Claude Code config).
3. If the skill references large lookup tables or tag catalogs, put them under `<skill-name>/references/` and instruct the skill to read them selectively by section.

## Skill Authoring Conventions (from existing skill)

- **Two-phase structure** works well for creative/generation skills: an *interview* phase to gather the brief, then a *composition/output* phase. Skip the interview if the user already supplied sufficient context.
- **Hard limits vs. advisory targets**: distinguish between limits that cause silent failures in downstream tools (hard — non-negotiable) and optimal ranges that improve quality (advisory — state them, but don't enforce them as gates).
- **Output as fenced code blocks**: anything the user needs to copy-paste verbatim should be in its own fenced code block with nothing extra inside.
- **Character counts**: when a downstream tool has a character limit, compute counts — do not estimate.
