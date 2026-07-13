# Third-Party Actions, Pinning, and Supply Chain

Covers: vetting third-party actions, commit-SHA pinning and impostor commits, automated
dependency updates, and maintaining curated shared workflows (C5, S5, S6).

---

## Use third-party actions with caution (S5)

Minimize third-party action usage in general — where the GitHub API can implement the same logic
directly (a `curl`/`gh` call in a `run:` step), that's less attack surface than pulling in an
external action.

Where a third-party action is genuinely needed, vet it before adding it:

- **Origin and trust:** is the publisher a known individual/org, or an anonymous account?
- **Activity:** multiple active contributors, recent commits, responsive to issues — a single
  maintainer who's been silent for two years is a bigger supply-chain risk (account takeover,
  abandonment).
- **Stability:** is the code straightforward to read, or so complex/obfuscated it's hard to
  audit what it actually does?
- **Permissions requested:** does the action ask for more repository/token access than its
  stated purpose needs?

---

## Pin every action and reusable workflow to a full commit SHA (C5)

**Why tags/branches aren't enough:** `uses: some-org/some-action@v2` resolves `v2` to whatever
commit the tag currently points to — and tags are mutable. A compromised maintainer account (or a
malicious update to the action itself) can repoint `v2` to different code without your workflow
file changing at all.

```yaml
# ❌ Mutable — the code that actually runs can change without any diff to this file
- uses: some-org/some-action@v2
- uses: some-org/some-action@main

# ✅ Pinned — this exact commit is what runs, always. Comment the version for readability.
- uses: some-org/some-action@a1b2c3d4e5f678901234567890abcdef12345678 # v2.1.0
```

**Detection pattern** — flag any `uses:` line whose ref after `@` is not a 40-character hex
string:

```bash
grep -rEn "uses: [^@]+@[^ ]+" .github/workflows/*.yml .github/actions/*/action.yml 2>/dev/null \
  | grep -vE "@[0-9a-f]{40}([[:space:]]|$)"
```
(This will also catch local/relative `uses: ./` references and `uses: docker://...` — those are
expected exceptions, not findings.)

### Impostor commits

Pinning to a SHA isn't quite the whole story: GitHub resolves a commit SHA by finding *any*
matching object reachable from *any* fork of the repository, and will execute it regardless of
which fork it actually originated from. This means a SHA that looks like it belongs to the
upstream, trusted org could in principle be a commit that only exists in an attacker's fork.

**Fix:** verify the pinned commit actually belongs to the specified org/repo, not just that the
hash resolves to *something*. Don't do this by hand — use Zizmor's `impostor-commit` rule
(`https://docs.zizmor.sh/audits/#impostor-commit`) as part of the static-analysis step described
in `references/repo-and-runner-hardening.md`, and treat any finding from it as a CRITICAL (C5)
gate failure.

---

## Automated dependency updates, with a cooldown (S6)

Pinning to a SHA means updates are no longer automatic — use Dependabot or Renovate so pins get
bumped deliberately rather than going stale indefinitely.

**Dependabot** (`.github/dependabot.yml`):
```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    cooldown:
      default-days: 4   # wait a few days after a release before adopting it
```

**Renovate** (`renovate.json`):
```json
{
  "extends": ["config:base"],
  "packageRules": [
    {
      "matchManagers": ["github-actions"],
      "minimumReleaseAge": "4 days"
    }
  ]
}
```

**Why the delay matters:** a newly published action version — including a newly compromised or
maliciously updated one — hasn't had time for the community to notice and report problems. A
short cooldown (a few days is enough) lets that detection window pass before you pull the update
in, without meaningfully slowing down legitimate maintenance.

---

## Maintain curated shared workflows and actions

If more than one repository needs the same CI logic, don't let every repo hand-roll (and
independently mis-pin) its own copy. Establish one centralized, security-reviewed repository of
reusable workflows/actions and have every other repo call into it with `workflow_call` — that
gives you a single place to apply every control in this skill, instead of N places that can each
drift out of compliance independently.

Reference implementation: [grafana/shared-workflows](https://github.com/grafana/shared-workflows)
— in particular its
[reusable Zizmor workflow](https://github.com/grafana/shared-workflows/blob/main/.github/workflows/reusable-zizmor.yml)
is a good template for standardizing the static-analysis step described in
`references/repo-and-runner-hardening.md` across many repos at once.
