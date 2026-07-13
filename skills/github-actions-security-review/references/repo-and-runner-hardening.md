# Repository and Runner Hardening

Covers: treating the pipeline as critical production code, incident response readiness, static
analysis (CodeQL actions scanning + Zizmor), repository settings, egress restriction, self-hosted
runner caution, and artifact/cache poisoning prevention (S1, S2, S3, S4, S12, plus two
organizational principles).

---

## Treat the CI/CD pipeline as critical production code

A pipeline usually has access to more sensitive credentials and endpoints than the application
code it builds — arguably making it the *more* critical asset. Apply the same secure-development
practices to workflow files as to production application code: threat modeling, secure code
review on every workflow change, security validation, and periodic penetration testing of the
pipeline itself. If a workflow change wouldn't get casual, unreviewed sign-off for prod app code,
it shouldn't get one here either.

Further reading:
- [NIST SP 800-204D — Strategies for the Integration of Software Supply Chain Security in DevSecOps CI/CD Pipelines](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-204D.pdf)
- [OWASP CI/CD Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html)
- [OWASP Secure Pipeline Verification Standard](https://owasp.org/www-project-spvs)

## Assume failure and have an incident response plan

Design for the pipeline being breached, not just for preventing it. Define roles, communication
paths, and escalation steps for a pipeline-compromise incident before one happens — deciding this
during an active exfiltration is too late. Learn from public post-mortems of real CI/CD
compromises (e.g. the
[Trivy post-mortem](https://github.com/aquasecurity/trivy/discussions/10462) and the
[Cline post-mortem](https://cline.bot/blog/post-mortem-unauthorized-cline-cli-npm)) — both are
worth reading end-to-end for the specific mechanics of how trusted pipelines got compromised.

---

## Enable static analysis for GitHub Actions workflows (S1)

Two complementary tools, used together for defense in depth:

- **CodeQL, `actions` scanning** — free for public repos. Enable either via a workflow file or
  the repo UI:
  ```yaml
  # .github/workflows/codeql.yml
  name: "CodeQL"
  on:
    push:
      branches: [main]
    pull_request:
      branches: [main]
    schedule:
      - cron: '0 6 * * *'   # scheduled scan, not just PR-triggered
  permissions:
    security-events: write
  jobs:
    analyze:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@<sha>
        - uses: github/codeql-action/init@<sha>
          with:
            languages: actions
        - uses: github/codeql-action/analyze@<sha>
  ```
  Or via **Settings → Advanced Security → Code scanning → CodeQL analysis**, confirming
  `GitHub Actions` appears under the Languages section.

- **[Zizmor](https://docs.zizmor.sh/)** — a dedicated GitHub Actions static analyzer, catches
  patterns CodeQL doesn't (e.g. the impostor-commit check referenced in
  `references/pinning-and-supply-chain.md`). Run it as a required check:
  ```yaml
  - uses: zizmorcore/zizmor-action@<sha> # or `pip install zizmor && zizmor .`
  ```

**Wire both into branch protection as required status checks** — a scan that runs but doesn't
block merges catches nothing in practice. At minimum, block merges on high/critical findings.
Also run a scheduled scan (not just PR-triggered) so findings against already-merged workflows
get tracked and remediated, and periodically upgrade both tools since detection rules improve
over time.

If this needs to scale across many repos, standardize via a centralized reusable workflow rather
than copy-pasting the same scan config everywhere — see the
[Grafana shared-workflows Zizmor example](https://github.com/grafana/shared-workflows/blob/main/.github/workflows/reusable-zizmor.yml)
referenced in `references/pinning-and-supply-chain.md`.

---

## Harden repository settings (S12)

These live in repo/org settings, not in workflow YAML — flag them as items to verify manually
(or via `gh api`) rather than something a file diff will show:

| Setting | Where | Why |
|---|---|---|
| `Require approval for all external contributors` | Settings → Actions → General | Workflows triggered by a fork PR from a non-member don't run automatically — this is the primary defense against untrusted-code execution via PR. |
| Default `GITHUB_TOKEN` permissions → **read-only** | Settings → Actions → General → Workflow permissions | Sets the floor; workflows must then explicitly opt into any `write` scope they need, rather than getting it by default. |
| Branch protection: required reviews, required status checks, signed commits, `CODEOWNERS` | Settings → Branches | Prevents a single compromised or malicious commit from reaching a protected branch unreviewed. |

Check via the CLI where the UI isn't handy:
```bash
gh api repos/{owner}/{repo} --jq '.allow_forking, .default_branch'
gh api repos/{owner}/{repo}/actions/permissions/workflow --jq '.default_workflow_permissions'
gh api repos/{owner}/{repo}/branches/{branch}/protection
```

> **Watch for a specific footgun:** `Require approval for first-time contributors` (as opposed to
> *all* external contributors) is weaker than it looks. An attacker can submit an innocuous
> first PR (e.g. a typo fix) to earn approval, then submit a follow-up PR with malicious changes
> that runs without further review, because they're no longer a "first-time" contributor. Prefer
> `Require approval for all external contributors`.

---

## Restrict egress traffic from GitHub-hosted runners (S2)

Hosted runners have outbound internet access by default, which is exactly what's needed to
exfiltrate a secret to an attacker-controlled endpoint. Monitor and restrict egress with a tool
like [Harden-Runner](https://github.com/step-security/harden-runner):

```yaml
steps:
  - uses: step-security/harden-runner@<sha> # vX
    with:
      egress-policy: audit   # start in audit mode, then tighten to `block` with an allowlist
```

Start in `audit` mode to build a baseline of legitimate outbound calls, then switch to `block`
with an explicit allowlist once you know what's expected.

---

## Self-hosted runners with extra caution (S3)

Self-hosted runners typically have internal network access and may retain cached credentials or
data between jobs. Because they execute arbitrary attacker-supplied code by design, a compromised
job can pivot into persistent access on the runner host itself, not just exfiltrate a token.

**Never use self-hosted runners on a public repository** — anyone who can fork the repo and open
a PR can potentially get code execution on that runner.

If a public repo genuinely needs a self-hosted runner:
- Apply the same secure-development rigor as production infrastructure (threat modeling, code
  review, validation, penetration testing, patching, hardening).
- Enable `Require approval for all external contributors` and manually review + approve every
  external-contributor workflow run before it executes.
- Use **ephemeral** (e.g. container-based) runners, destroyed after each job — no persistence
  across runs.
- Never store sensitive data on the runner host — anyone able to trigger a workflow effectively
  has access to whatever's on that machine.
- Restrict the runner's network reach; don't give it a path to sensitive internal infrastructure.

---

## Prevent artifact poisoning (S4)

Artifact/cache poisoning: an attacker injects malicious content into a shared cache or a stored
dependency (see
[GitHub Actions Cache Poisoning](https://adnanthekhan.com/2024/05/06/the-monsters-in-your-build-cache-github-actions-cache-poisoning)),
and a later, more privileged workflow — often a release/publish pipeline — restores and trusts
that cache, executing the poisoned content in a privileged context. This can compromise released
artifact integrity or exfiltrate production secrets.

**Fix:** disable caching (`actions/cache`, language-specific cache options in setup actions, etc.)
in any release or publish workflow. Caching is a build-speed optimization; a release pipeline
running with production secrets and write access to published artifacts isn't the place to accept
that risk for the sake of a faster build.

```yaml
# ❌ Release pipeline restores a cache another (less trusted) workflow could have poisoned
- uses: actions/setup-node@<sha>
  with:
    cache: 'npm'

# ✅ Release pipeline always installs clean
- uses: actions/setup-node@<sha>
  # no cache: key here — or explicitly `cache: ''`
- run: npm ci
```
