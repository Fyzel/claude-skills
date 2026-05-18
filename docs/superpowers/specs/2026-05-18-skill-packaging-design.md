# Skill Packaging & Publishing — Design Spec

**Date:** 2026-05-18  
**Branch:** cicd/promotion  
**Status:** Approved

---

## Goal

A GitHub Actions workflow that packages each Claude Code skill in the repository as a self-contained `.skill` zip file and publishes it as its own GitHub Release, triggered manually on demand.

---

## Trigger

`workflow_dispatch` only. No automatic triggers on push or tag.

## Permissions

The workflow job requires `permissions: contents: write` to create releases and upload release assets. The `gh` CLI used for release operations authenticates automatically via the `GITHUB_TOKEN` secret available on all Actions runners — no additional secret configuration is needed.

---

## Skill Discovery

The job iterates every top-level directory of the repository. A directory is treated as a skill if and only if it contains a `SKILL.md` file at its root. Directories without `SKILL.md` are silently skipped.

---

## Packaging

Each discovered skill directory is zipped recursively into `<skill-name>.skill`. The archive's internal layout is **flat** — no wrapping directory. All files and subdirectories from the skill directory sit directly at the zip root, so a consumer can unzip into a named folder and immediately get the canonical skill structure.

Example — `suno-songwriter/` produces `suno-songwriter.skill`:
```
SKILL.md
references/
  tag-reference.md
```

All file types and all subdirectory depths are included. No exclusions beyond what is not part of the skill directory itself (e.g., `.git` is never inside a skill directory).

---

## Release Strategy

Each skill gets its own distinct GitHub Release per workflow run:

| Field | Value |
|---|---|
| Tag | `<skill-name>-<short-sha>` (e.g. `suno-songwriter-9af4351`) |
| Release title | `<skill-name> @ <short-sha>` (e.g. `suno-songwriter @ 9af4351`) |
| Asset | `<skill-name>.skill` |

**Idempotency:** Before creating a release, the job checks whether a release with that tag already exists. If it does, the skill is skipped (not an error). This prevents failures when the workflow is triggered more than once on the same commit.

---

## Job Structure

Single job, `ubuntu-latest`:

1. Checkout repository
2. Compute short SHA (`git rev-parse --short HEAD`, 7 characters)
3. For each top-level directory:
   a. Skip if `SKILL.md` absent
   b. Zip directory contents (flat) into `<skill-name>.skill`
   c. Check if release tag `<skill-name>-<short-sha>` already exists via `gh release view`
   d. If exists: print skip message, continue
   e. If not exists: create release and upload `.skill` asset via `gh release create`
