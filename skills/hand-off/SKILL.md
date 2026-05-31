---
name: hand-off
description: Delegates a defined scope of work to a fresh Claude Code subagent, with full current-context preserved across the boundary. Use this skill whenever the user invokes `/hand-off` or asks (in any phrasing) to hand off, delegate, spin off, fork, or pass work to another agent or a fresh agent. Also use when the user mentions running out of context and wanting to continue elsewhere, or wants to scope a chunk of work to its own session. Captures current context into a handoff directory, spawns a subagent via the Task tool to complete the work, then synthesizes the resulting output back into the parent conversation. Handoff directories persist on disk as an audit trail.
---

# Hand-off

Delegate a defined scope of work to a fresh Claude Code subagent, with full context preserved across the boundary. Each handoff is recorded as a folder at `<project-root>/.handoffs/<feature>/` containing `input.md` (the brief) and `output.md` (the result). In git projects, `baseline.txt` is also captured to enable recovery if the subagent fails to write `output.md`. All files persist on disk as an audit trail.

## When to use

Trigger this skill when:

- The user types `/hand-off` (literal slash-command style)
- The user asks to "hand off", "delegate to a subagent", "spin this off", "fork this", or "pass this to a fresh agent"
- The user signals context exhaustion and wants a chunk of work moved to its own session ("I'm running out of context, let me spin this off")

## Workflow

### 1. Identify the scope (and clarify if unclear)

Before writing anything, determine:

- **What is being handed off?** The specific task or set of tasks the subagent must complete.
- **What context does the subagent need?** Relevant files, decisions already made, constraints, and the current state of the workspace.

If either is unclear, **stop and ask the user** before proceeding. Do not guess. Examples of useful clarifying questions:

- "Is the handoff just task X, or should it also include the follow-up Y we discussed?"
- "Should the subagent see the work we did on `<file>`, or start fresh?"
- "What does 'done' look like for this handoff?"
- "Any constraints I should pass along — files to avoid, conventions to respect?"

The context captured in `input.md` is dependent on what's in the current conversation; surface what's relevant rather than dumping everything. If you're not sure what's relevant, ask.

### 2. Set up the handoff directory

**2a. Find the project root.** Walk up from the current working directory until you find a project marker. Accepted markers (any one suffices):

- `.git/`
- `package.json`
- `pyproject.toml`
- `Cargo.toml`
- `go.mod`
- `pom.xml`
- `build.gradle` / `build.gradle.kts`
- `Gemfile`
- `composer.json`

Use the directory containing the first marker found as the base. In a monorepo with nested markers, this gives you the nearest (innermost) project, which is usually correct — if the user wants a different root, they'll say so.

If no marker is found anywhere up the tree, **ask the user** where to place `.handoffs/`. Offer concrete options: the current working directory, the home directory (`~/.handoffs/`), or a custom path. Do not silently default.

**2b. Choose the slug.** Derive a short kebab-case `<feature>` slug from the scope (e.g., `oauth-login`, `dashboard-refactor`, `migrate-postgres-15`). Keep it concise — a few words at most. If the user named the handoff explicitly, use their name.

If the scope is messy or could slug a few different ways, **propose 2-3 candidates and let the user pick** rather than choosing arbitrarily. For example:

> The scope here could slug a few ways — which do you prefer?
> 1. `auth-timeout-debug`
> 2. `refresh-token-upload-bug`
> 3. `intermittent-auth-timeout`

**2c. Handle collisions.** Check whether `<project-root>/.handoffs/<feature>/` already exists:

- If it does not exist, create it and use it.
- If it does exist, auto-suffix: try `<feature>-2/`, then `<feature>-3/`, and so on, until you find a path that does not exist. Create that one.

Never delete, rename, or modify past handoff folders — they are part of the audit trail.

**2d. Announce, and (first time only) resolve the gitignore question.** Tell the user which directory you're using before writing into it.

If this is the first time `.handoffs/` is being created in this project (i.e., the parent `.handoffs/` directory did not exist before this call) AND the project is a git repo (a `.git/` directory exists at the root) AND `.handoffs/` is not already in `.gitignore`, **stop and ask the user** before proceeding:

> I'm creating `.handoffs/` in this project for the first time. Do you want it added to `.gitignore`?
>
> - **Commit it**: useful as a shared audit trail of work-in-progress decisions.
> - **Ignore it**: useful if handoff docs contain private reasoning, sensitive context, or noise you don't want in history.

This question **blocks the workflow** — wait for the user's answer before moving to step 3. After the answer:

- **"Commit it"**: do nothing to `.gitignore`, proceed.
- **"Ignore it"**: append `.handoffs/` to `.gitignore` (creating the file if it doesn't exist), then proceed.

Do not modify `.gitignore` without the user's explicit say-so.

### 3. Write `input.md`

Write `<project-root>/.handoffs/<feature>/input.md` using this structure (omit sections that genuinely don't apply, but err on the side of including them):

```markdown
# Hand-off: <short title>

## Scope of work
<What the subagent must accomplish. Clear, unambiguous, specific.>

## Context
<Background. Why this work matters. The larger picture the subagent needs to understand.>

## Current state
<What's been done so far. Files created or modified (with paths). Decisions already made. Where things stand right now.>

## Constraints and conventions
<Anything the subagent must respect: coding style, file locations, tools to use or avoid, things not to touch, user preferences expressed earlier.>

## Success criteria
<How the subagent knows it's done. Acceptance conditions.>

## Open questions
<Anything unresolved. If you have a recommended call, state it; otherwise note that the subagent has discretion.>

## Deliverable
Write `output.md` in this same directory when complete, containing:
1. **Summary of work performed** — what was actually done
2. **Results achieved** — concrete outputs, file paths, key findings
3. **Recommendations and follow-ups** — open questions, suggested next steps, things the parent agent or user should be aware of

Writing this file is a required completion criterion. The handoff is not complete until `output.md` exists with all three sections.
```

### 4. Capture baseline and spawn the subagent

**4a. Capture baseline (git projects only).** If the project root contains a `.git/` directory, capture the working state to `<project-root>/.handoffs/<feature>/baseline.txt` **before** spawning the subagent. Contents:

```
HEAD: <output of `git rev-parse HEAD`>
working_tree: <`clean` or `dirty` — based on `git status --porcelain`>
captured_at: <ISO 8601 timestamp>
```

If the working tree is dirty at capture time, note it in the file. This makes any later diff-based recovery approximate (we can't cleanly separate the subagent's changes from pre-existing pending changes), but proceed regardless — the user explicitly asked for the handoff. Do not stash, commit, or otherwise modify the user's working tree.

If the project is not a git repo, skip this step. Recovery options will be more limited if `output.md` is missing.

**4b. Spawn the subagent.** Use the Task tool with a prompt along these lines, substituting the actual absolute path to the handoff directory:

> Read `<absolute-path>/.handoffs/<feature>/input.md`. It contains the full scope, context, and success criteria for the work you must complete.
>
> **Writing `<absolute-path>/.handoffs/<feature>/output.md` is a required completion criterion — your work is not done until that file exists with all three required sections.** Do not return without writing it.
>
> Complete the work, then write `output.md` with: (1) summary of work performed, (2) results achieved, (3) recommendations and follow-ups. Return a short confirmation message after the file is written.

Pass absolute paths (not paths relative to cwd) so the subagent isn't dependent on its own working directory.

Choose the subagent type that best fits the task. Use `general-purpose` when no specialized type fits.

### 5. Synthesize the output back

After the subagent returns:

**5a. Verify `output.md` exists** at `<project-root>/.handoffs/<feature>/output.md`. Writing it is a required completion criterion. If the file is **present**, skip to 5c. If the file is **missing**, the handoff is incomplete — do not treat the subagent's return message as a substitute. Proceed to 5b.

**5b. Handle a missing `output.md`.** Surface the subagent's return message verbatim, explain that the required output file wasn't written, and offer recovery options based on whether a baseline was captured:

*If `baseline.txt` exists (git project):*

1. **Reconstruct from diff** — run `git diff <baseline-SHA>` (note: **no** `..HEAD` — that would only catch committed changes, and subagents typically don't commit) and `git status --porcelain` to inventory what changed since the baseline. `git diff <baseline-SHA>` compares the baseline commit against the current working tree, capturing both committed and uncommitted changes. **Exclude `.handoffs/` from the change list** — it contains the handoff's own metadata (input.md, baseline.txt, etc.), not subagent work. Use a pathspec exclusion (e.g., `git diff <baseline-SHA> -- . ':(exclude).handoffs/'`) and filter `.handoffs/` out of the porcelain output. List new untracked files, modified files, and a short summary of the remaining changes. Draft an `output.md` from that and present it to the user for confirmation before treating the handoff as complete. If the baseline noted a dirty working tree, warn the user that the reconstructed diff is approximate.
2. **Re-run the subagent** (possibly with a stronger prompt that emphasizes writing `output.md`).
3. **Revise the brief** and try again.
4. **Abandon** the handoff.

*If `baseline.txt` does not exist (non-git project):*

1. **Re-run the subagent** (possibly with a stronger prompt).
2. **Inspect manually** — ask the user which files they expect the subagent to have touched, then read those and help reconstruct `output.md`.
3. **Revise the brief** and try again.
4. **Abandon** the handoff.

**5c. Summarize the output back.** Once `output.md` exists (either originally written by the subagent or reconstructed and confirmed by the user), read it and summarize the key points back to the user in the conversation:

- What the subagent accomplished
- Results the user should review (with file paths)
- Follow-ups or open questions the subagent flagged

If the subagent reported failure or returned partial work even with `output.md` present, surface that clearly and ask the user how to proceed.

## Notes

- The `.handoffs/` directory is the audit trail. Never delete, rename, or modify past handoff folders automatically.
- The subagent inherits the project's toolchain but **not** the parent's conversation history — anything it needs must be in `input.md` or files it can read from disk.
- When in doubt about location, slug, or scope: ask the user. Do not silently default on the things that matter.
