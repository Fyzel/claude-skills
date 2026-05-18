# Skill Packaging & Publishing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a manually-triggered GitHub Actions workflow that discovers skill directories, zips each one as a flat `.skill` archive, and publishes it as its own versioned GitHub Release.

**Architecture:** A single `workflow_dispatch` job iterates top-level directories, skips any without `SKILL.md`, zips each skill's contents flat (no wrapping directory) into `<skill-name>.skill`, checks for an existing release tag, and creates a new release + uploads the asset if none exists.

**Tech Stack:** GitHub Actions, `gh` CLI (pre-installed on `ubuntu-latest`), `zip`, `yamllint` (validation only)

---

### Task 1: Create workflow directory and validate tooling

**Files:**
- Create: `.github/workflows/publish-skills.yml`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Verify `yamllint` is available for local validation**

```bash
yamllint --version 2>/dev/null || pip install yamllint
```

Expected: prints a version string, e.g. `yamllint 1.35.1`

- [ ] **Step 3: Commit the empty directory placeholder**

`.github/workflows/` won't be tracked by git until a file is added — proceed directly to Task 2.

---

### Task 2: Write the workflow file

**Files:**
- Create: `.github/workflows/publish-skills.yml`

- [ ] **Step 1: Write the workflow file**

Create `.github/workflows/publish-skills.yml` with this exact content:

```yaml
name: Package and Publish Skills

on:
  workflow_dispatch:

jobs:
  publish-skills:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install zip
        run: sudo apt-get install -y zip

      - name: Package and publish skills
        run: |
          SHORT_SHA=$(git rev-parse --short HEAD)

          for dir in */; do
            skill_name="${dir%/}"

            if [ ! -f "${skill_name}/SKILL.md" ]; then
              echo "Skipping ${skill_name}: no SKILL.md"
              continue
            fi

            echo "Processing: ${skill_name}"
            tag="${skill_name}-${SHORT_SHA}"

            if gh release view "${tag}" > /dev/null 2>&1; then
              echo "Release ${tag} already exists, skipping"
              continue
            fi

            asset="${skill_name}.skill"
            (cd "${skill_name}" && zip -r "../${asset}" .)

            gh release create "${tag}" \
              --title "${skill_name} @ ${SHORT_SHA}" \
              --notes "Packaged from commit ${SHORT_SHA}" \
              "${asset}"

            rm -f "${asset}"
            echo "Published: ${tag}"
          done
```

- [ ] **Step 2: Validate YAML syntax**

```bash
yamllint .github/workflows/publish-skills.yml
```

Expected: no output (clean). If errors appear, fix indentation or quoting and re-run until clean.

- [ ] **Step 3: Optionally validate Actions-specific syntax with actionlint**

```bash
bash <(curl -Ls https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash) 2>/dev/null
./actionlint .github/workflows/publish-skills.yml
rm -f actionlint
```

Expected: no output (clean). Common actionlint errors and fixes:
- `shellcheck reported issue` → fix the flagged shell line
- `unexpected key "env"` → check indentation; `env` must be at job level, not step level
- `value "write" is not allowed` → verify the permission key name matches the Actions docs

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/publish-skills.yml
git commit -m "feat: add workflow to package and publish skills as .skill files"
```

---

### Task 3: Smoke-test the packaging logic locally

**Files:**
- No file changes — verification only

The shell loop can be tested locally before pushing, using the actual repo state.

- [ ] **Step 1: Run the packaging portion of the script locally**

```bash
SHORT_SHA=$(git rev-parse --short HEAD)

for dir in */; do
  skill_name="${dir%/}"

  if [ ! -f "${skill_name}/SKILL.md" ]; then
    echo "Skipping ${skill_name}: no SKILL.md"
    continue
  fi

  asset="${skill_name}.skill"
  (cd "${skill_name}" && zip -r "../${asset}" .)
  echo "Created: ${asset}"
done
```

- [ ] **Step 2: Verify the archive contents**

For each `.skill` file produced, confirm the flat structure (no wrapping directory):

```bash
# Replace suno-songwriter with the actual skill name if different
unzip -l suno-songwriter.skill
```

Expected output — files should appear at the root, not under a subdirectory:

```
Archive:  suno-songwriter.skill
  Length      Date    Time    Name
---------  ---------- -----  ----
     ...   ...        ...    SKILL.md
     ...   ...        ...    references/tag-reference.md
```

If you see `suno-songwriter/SKILL.md` instead of `SKILL.md`, the `cd` trick failed — check the shell script.

- [ ] **Step 3: Clean up local artifacts**

```bash
rm -f *.skill
```

- [ ] **Step 4: Commit the verification result (no file changes — no commit needed)**

If Step 2 revealed a structural problem, fix the `zip` invocation in `.github/workflows/publish-skills.yml`, re-run yamllint, and amend or make a new commit before proceeding.

---

### Task 4: Push branch and verify workflow appears in GitHub UI

**Files:**
- No file changes

- [ ] **Step 1: Push the branch**

```bash
git push -u origin cicd/promotion
```

- [ ] **Step 2: Confirm the workflow is visible**

```bash
gh workflow list
```

Expected: `Package and Publish Skills` appears in the list with status `active`.

If it shows `disabled` or does not appear, GitHub may not have indexed the workflow yet — wait 30 seconds and re-run.

- [ ] **Step 3: Trigger the workflow manually**

```bash
gh workflow run "Package and Publish Skills" --ref cicd/promotion
```

Expected: exits cleanly with a run URL printed.

- [ ] **Step 4: Watch the run**

```bash
gh run watch
```

Expected: all steps green. If the `Package and publish skills` step fails, read the log:

```bash
gh run view --log-failed
```

Common failure causes:
- `gh: command not found` — shouldn't happen on `ubuntu-latest`; check `runs-on`
- `zip: command not found` — add `sudo apt-get install -y zip` as a step before the script
- `Resource not accessible by integration` — `permissions: contents: write` is missing or misindented

- [ ] **Step 5: Verify the release was created**

```bash
gh release list
```

Expected: a release named `suno-songwriter @ <short-sha>` appears with `suno-songwriter.skill` as its asset.

```bash
gh release view "suno-songwriter-$(git rev-parse --short HEAD)"
```

- [ ] **Step 6: Verify idempotency — trigger the workflow a second time on the same commit**

```bash
gh workflow run "Package and Publish Skills" --ref cicd/promotion
gh run watch
```

Expected: run completes successfully, log shows `Release suno-songwriter-<sha> already exists, skipping`. No duplicate release is created.
