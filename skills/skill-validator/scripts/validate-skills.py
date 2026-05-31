"""Validate Claude Code skill files against Anthropic's SKILL.md requirements."""

import re
import sys
import zipfile
import argparse
from pathlib import Path

import yaml


def find_repo_root():
    p = Path(__file__).resolve().parent
    while p != p.parent:
        if (p / ".git").exists():
            return p
        p = p.parent
    raise RuntimeError("Could not find repo root (.git not found)")


SKILLS_DIR = find_repo_root() / "skills"
MAX_DESC_CHARS = 1536


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
    if end is None:
        return None, text
    try:
        fm = yaml.safe_load("\n".join(lines[1:end])) or {}
        if not isinstance(fm, dict):
            return None, text
    except yaml.YAMLError:
        return None, text
    return fm, "\n".join(lines[end + 1:])


def validate_skill(skill_dir):
    issues = []
    warnings = []

    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return [f"SKILL.md missing in {skill_dir}"], []

    text = skill_file.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    if fm is None:
        issues.append("no YAML frontmatter found (must start with ---)")
        return issues, warnings

    if "name" not in fm:
        issues.append("frontmatter missing required 'name' field")
    elif fm["name"] != skill_dir.name:
        issues.append(f"name '{fm['name']}' does not match directory '{skill_dir.name}'")

    if "description" not in fm:
        issues.append("frontmatter missing required 'description' field")
    else:
        if re.search(r'<[^>]+>', fm["description"]):
            issues.append("description contains XML tags — Claude Code rejects these on load")
        desc_len = len(fm["description"]) + len(fm.get("when_to_use", ""))
        if desc_len > MAX_DESC_CHARS:
            issues.append(
                f"description+when_to_use is {desc_len} chars, exceeds {MAX_DESC_CHARS} limit"
            )
        elif desc_len > MAX_DESC_CHARS * 0.9:
            warnings.append(f"description+when_to_use is {desc_len}/{MAX_DESC_CHARS} chars (>90% of limit)")
        else:
            warnings.append(f"description+when_to_use: {desc_len}/{MAX_DESC_CHARS} chars")

    if not body.strip():
        warnings.append("skill body is empty (no content after frontmatter)")

    return issues, warnings


def simulate_package(skill_dir):
    test_dir = skill_dir / ".test"
    test_dir.mkdir(exist_ok=True)
    out_path = test_dir / f"{skill_dir.name}.skill"
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in skill_dir.rglob("*"):
            if f.is_file() and not f.is_relative_to(test_dir):
                zf.write(f, f.relative_to(skill_dir))
    return out_path.stat().st_size


def main():
    parser = argparse.ArgumentParser(description="Validate Claude Code skill files")
    parser.add_argument("skill", nargs="?", help="specific skill name to validate (default: all)")
    parser.add_argument("--no-package", action="store_true", help="skip packaging simulation")
    args = parser.parse_args()

    if args.skill:
        candidates = [SKILLS_DIR / args.skill]
    else:
        candidates = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith("."))

    if not candidates:
        print("No skills found.")
        sys.exit(1)

    any_fail = False

    for skill_dir in candidates:
        if not skill_dir.exists():
            print(f"[FAIL] {skill_dir.name}: directory not found")
            any_fail = True
            continue

        issues, warnings = validate_skill(skill_dir)
        failed = bool(issues)
        if failed:
            any_fail = True

        status = "FAIL" if failed else "PASS"
        print(f"[{status}] {skill_dir.name}")

        for issue in issues:
            print(f"  ERROR:   {issue}")
        for warning in warnings:
            print(f"  INFO:    {warning}")

        if not args.no_package and (skill_dir / "SKILL.md").exists():
            size = simulate_package(skill_dir)
            print(f"  PACKAGE: {size} bytes")

        print()

    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
