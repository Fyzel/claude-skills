# AI Assistants Running in CI/CD

Covers C10 in the main gate: workflows that invoke an AI assistant (Claude Code, GitHub Copilot,
a custom LLM-based reviewer, an issue-triage bot, etc.) directly as part of the pipeline.

---

## The risk

An AI assistant step is typically fed untrusted content as part of its task — a PR diff, an
issue body, a comment thread — so that it can review, summarize, or respond to it. That content
is also, from the model's perspective, just more text in its context. If the workflow running the
assistant has access to secrets or a `write`-scoped `GITHUB_TOKEN`, and the trigger can be fired
by an untrusted user (any GitHub account opening an issue or PR, for instance), a prompt injection
hidden in that content can manipulate the assistant into taking actions the workflow author never
intended — including actions that exfiltrate secrets or misuse the token.

This is not a hypothetical: the
["clinejection" attack](https://adnanthekhan.com/posts/clinejection/) is a documented real-world
example of exactly this pattern being exploited against an AI-assistant-driven CI workflow.

## Mitigation

**Limit the assistant's capabilities to the minimum required for its actual task.** If the job is
"summarize this PR diff as a comment," the assistant doesn't need write access to the repo beyond
posting that one comment, doesn't need shell/tool access to run arbitrary commands, and doesn't
need secrets in its environment at all. Scope down aggressively:

```yaml
# ❌ Broad — AI review step runs with repo write access and full secret set, triggered by
# anyone who can open a PR (including forks, if this runs on pull_request_target)
jobs:
  ai-review:
    permissions:
      contents: write
      pull-requests: write
    env:
      DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
      CLOUD_API_KEY: ${{ secrets.CLOUD_API_KEY }}
    steps:
      - uses: some-ai-review-action@<sha>

# ✅ Narrow — only what posting a review comment requires, nothing else in scope
jobs:
  ai-review:
    permissions:
      pull-requests: write   # just enough to post a comment
      contents: read
    steps:
      - uses: some-ai-review-action@<sha>
        # no unrelated secrets in this job's env at all
```

**Apply every other control in this skill to the workflow the assistant runs in as if it were any
other privileged step** — sanitize any context passed to it the same way you would for a shell
command (see `references/dangerous-triggers.md` § Sanitize user input), avoid running it under
`pull_request_target` on untrusted content, and treat its `GITHUB_TOKEN`/secret scope with the
same minimize-by-default discipline as C6/C7/C9. An AI assistant step is not a special case that
gets an exemption from the rest of the gate — if anything, its exposure to attacker-controlled
natural-language input makes it a higher-priority target for the same controls.
