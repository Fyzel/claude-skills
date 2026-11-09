# Secrets and Token Handling

Covers: eliminating static credentials via OIDC, secure handling when elimination isn't possible,
`secrets: inherit`, masking, secret scanning, and `actions/checkout` credential persistence
(C7, C8, C9, S8, S9, S10, S11).

---

## Eliminate static credentials — migrate to OIDC / trusted publishing (S8)

Static long-lived credentials (personal access tokens, static cloud access keys, static registry
tokens) are the highest-value target for secrets exfiltration — steal one and it works until
someone notices and rotates it. Most major cloud providers and package registries now support
OIDC-based short-lived token exchange ("trusted publishing"): the workflow proves its identity to
the provider via a GitHub-issued OIDC token, and gets back a token that's valid only for that run.

```yaml
# ✅ AWS via OIDC — no static AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY in secrets at all
permissions:
  id-token: write
  contents: read
steps:
  - uses: aws-actions/configure-aws-credentials@<sha> # vX.Y.Z
    with:
      role-to-assume: arn:aws:iam::123456789012:role/github-actions-deploy
      aws-region: us-east-1
```

```yaml
# ✅ PyPI trusted publishing — no PYPI_API_TOKEN secret needed
permissions:
  id-token: write
steps:
  - uses: pypa/gh-action-pypi-publish@<sha> # release/v1
```

Check the target provider's docs for OIDC/trusted-publishing support before assuming a static
secret is required — see GitHub's
[Security hardening for deployments](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments)
for the current list of integrations and setup steps per provider.

---

## If a static credential is genuinely unavoidable (S9, C9)

- **Never hardcode it in the workflow file.** Always reference it via `secrets.<NAME>`.
- **Pass it at the step level, not the job level.** A job-level `env:` block exposes the secret
  to every step in that job, including third-party actions that don't need it; scoping to the
  one step that actually needs it limits the blast radius if any other step in the job is
  compromised.
  ```yaml
  # ❌ Every step in the job can read DEPLOY_TOKEN, needed or not
  jobs:
    deploy:
      env:
        DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
      steps: [...]

  # ✅ Only the step that needs it gets it
  jobs:
    deploy:
      steps:
        - run: ./deploy.sh
          env:
            DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
  ```
- **Prefer [environment-level secrets](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)**
  over repository/org secrets where possible — they're only accessible when a job explicitly
  targets that `environment:`, which is a meaningfully smaller exposure surface than "available
  to any workflow in the repo."
- **Rotate regularly**, and treat any accidental exposure (see secret scanning below) as an
  immediate rotation trigger, not just a cleanup task.

---

## Eliminate `secrets: inherit` on reusable workflow calls (C7)

`secrets: inherit` passes **every** secret the calling workflow has access to — org, repo, and
environment secrets — into the called workflow, whether or not it needs them. This turns a
reusable workflow with a narrow, audited purpose into something with the same secret exposure as
its caller.

```yaml
# ❌ The called workflow gets every secret the caller has, needed or not
jobs:
  call-deploy:
    uses: org/shared-workflows/.github/workflows/deploy.yml@<sha>
    secrets: inherit

# ✅ Explicit — only what deploy.yml actually declares as required
jobs:
  call-deploy:
    uses: org/shared-workflows/.github/workflows/deploy.yml@<sha>
    secrets:
      DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

**Detection:**
```bash
grep -rn "secrets: inherit" .github/workflows/
```
Any match is a C7 finding — resolve by listing the called workflow's declared `secrets:` inputs
and passing exactly those.

---

## `actions/checkout` and `persist-credentials` (C8)

By default, `actions/checkout` persists the `GITHUB_TOKEN` credentials in the local git config
after checkout, so that later steps in the job can perform authenticated git operations (push,
etc.) without re-authenticating. If the job doesn't need to push or otherwise authenticate to
GitHub via git, that persisted credential is unnecessary risk — any step that runs after checkout
(including a compromised third-party action) can use it.

```yaml
# ❌ Default — credentials persist in .git/config for the rest of the job
- uses: actions/checkout@<sha>

# ✅ No persisted credential unless this job specifically needs to push
- uses: actions/checkout@<sha>
  with:
    persist-credentials: false
```

Only omit `persist-credentials: false` (i.e. leave the default) for jobs that genuinely perform
git operations requiring authentication (e.g. a job that commits a changelog and pushes it back).

---

## Mask sensitive data (S10)

`GITHUB_TOKEN` and anything referenced via `secrets.*` is automatically masked in logs. Anything
sensitive that *isn't* a registered GitHub secret — e.g. a value derived at runtime, or fetched
from an external API — is not masked automatically and needs an explicit mask:

```yaml
- run: |
    TEMP_CREDENTIAL=$(some-command-that-outputs-a-secret)
    echo "::add-mask::$TEMP_CREDENTIAL"
    echo "TEMP_CREDENTIAL=$TEMP_CREDENTIAL" >> "$GITHUB_ENV"
```

Mask *before* the value can appear in any log output, not after.

---

## Secret scanning (S11)

Catch leaked secrets before they merge, at two points:

- **Pre-commit** — run a scanner (e.g. `gitleaks`, `trufflehog`) as a pre-commit hook so leaks
  never leave the developer's machine:
  ```yaml
  # .pre-commit-config.yaml
  repos:
    - repo: https://github.com/gitleaks/gitleaks
      rev: <pinned-tag-or-sha>
      hooks:
        - id: gitleaks
  ```
- **Pull request** — run the same (or GitHub's native secret scanning / push protection) as a
  required CI check, failing the build on any detection so it can't merge:
  ```yaml
  - uses: gitleaks/gitleaks-action@<sha> # vX.Y.Z
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  ```

Treat a detection as a hard fail, not a warning — the point is to force remediation (rotate +
scrub history) before the secret is ever merged into a shared branch.
