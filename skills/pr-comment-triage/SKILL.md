---
name: pr-comment-triage
description: >
  Triage and resolve pull-request review comments end to end — fetch reviewer comments
  (especially GitHub Copilot automated review), fix each one in code, run the project's
  tests, then post a threaded reply under each original comment by its comment ID. Use this
  skill whenever the user says "check the Copilot comment(s) on PR N", "address the review
  comments", "reply to the review comments", "resolve PR feedback", "handle the PR comments",
  or asks to go through a reviewer's findings on a pull request. Works for any reviewer
  (Copilot, humans, bots) and any language or repo. Requires the `gh` CLI to be authenticated.
---

# PR Comment Triage

Resolve pull-request review comments in one pass: fetch → fix → test → reply threaded.
Built for GitHub Copilot's automated review, but works for any reviewer and any project.

## When to use

User asks to look at, address, or reply to review comments on a PR. Phrases like
"check the Copilot comment on PR 67", "reply to the review comments", "resolve the PR
feedback".

## Prerequisites

- `gh` CLI authenticated — verify with `gh auth status`.
- The PR number. If not given, derive it:
  `gh pr view --json number -q .number` (current branch) or `gh pr list`.
- The repo slug `OWNER/REPO`. Don't hardcode it — derive it:
  `gh repo view --json nameWithOwner -q .nameWithOwner`.

## Workflow

### 1. Fetch the comments

Get inline review comments with their IDs (the ID is required to reply in-thread):

```sh
gh api repos/OWNER/REPO/pulls/PR/comments \
  --jq '.[] | {id, user: .user.login, path, line, body}'
```

For PR-level (non-inline) review summaries, also check:

```sh
gh pr view PR --json reviews --jq '.reviews[] | {author: .author.login, state, body}'
```

Filter to the reviewer the user named (e.g. `Copilot`) if they specified one. Otherwise
handle all unresolved comments.

### 2. Summarize before acting

Present a short table: file:line → problem → proposed fix. Group real bugs vs. doc/test
gaps vs. nits. Get the user's go-ahead unless they already said "fix them".

### 3. Fix each comment

- Read the cited file at the cited line before editing — line numbers from the API are
  against the PR head commit and may have drifted.
- Make the smallest correct change that addresses the comment.
- Distinguish: code bug (fix it), missing test (add a regression test that locks in the
  behaviour), misleading doc/docstring (correct it), nit (fix or note why skipping).

### 4. Verify

Run the project's own tests for the touched area before replying, so replies are truthful.
Detect the test command from the repo rather than assuming one — common cases:

| Signal in repo                                      | Test command                                                                                                                     |
|-----------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| `pytest.ini` / `pyproject.toml` / `tests/` (Python) | `pytest -q` (use the project venv if present, e.g. `.venv/Scripts/python.exe -m pytest` on Windows, `.venv/bin/pytest` on POSIX) |
| `package.json` with a `test` script                 | `npm test` (or `pnpm test` / `yarn test`)                                                                                        |
| `Cargo.toml`                                        | `cargo test`                                                                                                                     |
| `go.mod`                                            | `go test ./...`                                                                                                                  |
| `Makefile` with a `test` target                     | `make test`                                                                                                                      |

If unsure which to run, check the project's README/CONTRIBUTING or CLAUDE.md, or ask the
user. Only claim a comment is fixed after the relevant test passes.

### 5. Reply threaded, by comment ID

Reply **under** each original comment (not a new top-level comment) using the replies
endpoint with the original comment's `id`:

```sh
gh api repos/OWNER/REPO/pulls/PR/comments/COMMENT_ID/replies \
  -f body='Concise reply: what changed and where.'
```

Reply rules:
- One reply per original comment, threaded to its ID.
- State what changed (function/file) and, for tests, name the test added.
- Honest: if a comment was intentionally not actioned, say why instead of claiming a fix.
- Replies are public on GitHub — confirm with the user before posting if there is any doubt.

### 6. Wrap up

Report which comments were fixed, tests run + result, and that replies posted. Do **not**
commit or push unless the user asks — ask whether to commit the fixes to the PR branch.

## Gotchas

- **Comment ID vs. line**: the `/replies` endpoint needs the comment `id`, not the line
  number. Always re-fetch IDs in the same session (step 1) before replying.
- **Drifted line numbers**: API `line` is against PR head; read the file to confirm the
  real location before editing.
- **Shell quoting**: when running `gh api ... -f body='...'`, use single quotes so the
  shell does not expand the body. On Windows/PowerShell, prefer a single-quoted string or a
  literal here-string; avoid mixing shells in one command.
- **Doc-sync**: if a fix changes a user-facing feature, CLI, or config, also update the
  project's docs (README, contributor docs, wiki) as that project requires.