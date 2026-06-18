---
name: github-doc-sync
description: >
  Keep a GitHub project's documentation in sync with the code after a change — propagate
  feature, CLI, config, exit-code, or install changes across the README, in-repo guide files
  (CLAUDE.md, CONTRIBUTING, docs/), and the GitHub wiki. Use this skill whenever the user says
  "sync the docs", "update the docs", "doc sync", "update README and wiki", "keep docs in sync",
  after resolving an issue or merging a feature, or when a hook/reminder flags that source changed
  and docs may be stale. Works for any GitHub repo. Requires `git`; the wiki step needs the
  repo's wiki enabled, and pushing needs `gh`/git push access.
---

# GitHub Doc Sync

Propagate a code change into every place the project documents it: README, in-repo guides
(CLAUDE.md / CONTRIBUTING / `docs/`), and the GitHub wiki. One pass, no drift.

## When to use

- After a change to a user-facing feature, CLI flag, config schema, exit code, or install
  steps.
- When the user says "sync the docs", "update README and wiki", or resolves an issue and
  wants docs caught up.
- When a project hook or memory reminds that source changed and docs may be stale.

## Step 0 — Find what each project treats as "docs"

Don't assume. Detect the doc surfaces present in this repo:

- **README**: `README.md` (or `.rst`/`.adoc`) at repo root.
- **In-repo guides**: `CLAUDE.md`, `CONTRIBUTING.md`, `docs/`, `AGENTS.md` — whichever exist.
- **Wiki**: GitHub wikis are a *separate git repo* at `OWNER/REPO.wiki.git`. Check it exists:

  ```sh
  SLUG=$(gh repo view --json nameWithOwner -q .nameWithOwner)
  git ls-remote "https://github.com/$SLUG.wiki.git" >/dev/null 2>&1 && echo "wiki exists"
  ```

Only sync surfaces that actually exist. If the project has a memory note or CLAUDE.md rule
about which docs to keep synced, honor it.

## Step 1 — Identify what changed

Determine the user-facing delta from the diff, not guesswork:

```sh
git diff --stat HEAD~1   # or against the merge-base of the feature branch
```

Map the change to doc-relevant facts: new/changed CLI flag, config key, exit code, default,
install/dependency step, supported behavior. Things that do **not** change docs (internal
refactor, test-only, comment) → skip; say so.

## Step 2 — Update the README

Sync the affected sections: usage/CLI, configuration schema, exit codes, install steps,
feature list. Match the README's existing structure and tone — edit in place, don't rewrite.

## Step 3 — Update in-repo guides

- `CLAUDE.md`: keep the module/responsibility tables, CLI summary, and exit-code list
  accurate — these guide future sessions.
- `CONTRIBUTING.md` / `docs/`: update if the change touches build, test, or contribution flow.

## Step 4 — Update the GitHub wiki

The wiki is a separate repo. Clone, edit the relevant pages, commit, push:

```sh
SLUG=$(gh repo view --json nameWithOwner -q .nameWithOwner)
tmp=$(mktemp -d)
git clone "https://github.com/$SLUG.wiki.git" "$tmp"
# edit pages in $tmp (Home.md, Usage.md, Configuration.md, etc. — match existing page names)
git -C "$tmp" add -A
git -C "$tmp" commit -m "docs: sync wiki with <change>"
git -C "$tmp" push
```

Match existing wiki page names and the sidebar (`_Sidebar.md`) if present. Don't invent a new
page when an existing one covers the topic.

## Step 5 — Verify consistency

Cross-check the three surfaces agree on the same facts (a CLI flag's name, an exit code's
meaning, a config key's default). The most common drift is one surface updated and another
missed — confirm all of them now match the code.

## Step 6 — Wrap up

Report what was updated per surface (README sections, in-repo files, wiki pages) and what was
intentionally skipped. README and in-repo edits land in the working tree (commit only when the
user asks). Wiki pushes are **live immediately** — confirm with the user before pushing wiki
changes if there is any doubt.

## Gotchas

- **Wiki is a separate repo**: edits to `OWNER/REPO.wiki.git` are not part of the code PR and
  push live on commit — there is no review step. Treat a wiki push like publishing.
- **Detect, don't assume**: not every repo has a wiki, CLAUDE.md, or `docs/`. Skip absent
  surfaces instead of creating them unprompted.
- **Match house style**: edit existing sections/pages in place; preserve heading structure,
  tables, and tone rather than rewriting.
- **Internal-only changes**: refactors, tests, and comments usually need no doc change — say
  so rather than touching docs needlessly.
