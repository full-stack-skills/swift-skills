#!/usr/bin/env python3
"""Validate swift-skills structure and optionally execute golden Swift packages."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
SCENARIOS = ROOT / "evaluation" / "scenarios.json"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, lines
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, lines
    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip("\"'")
    return metadata, lines


def markdown_errors(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    errors: list[str] = []
    if sum(line.startswith("```") for line in lines) % 2:
        errors.append(f"{path.relative_to(ROOT)}: unclosed fenced code block")
    for number, line in enumerate(lines, 1):
        for target in LINK_PATTERN.findall(line):
            target = target.strip().strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            local = target.split("#", 1)[0]
            if local and not (path.parent / local).resolve().exists():
                errors.append(f"{path.relative_to(ROOT)}:{number}: missing link {target}")
    return errors


def inspect_repository() -> tuple[list[str], list[Path]]:
    errors: list[str] = []
    manifests: list[Path] = []
    for required in (ROOT / "LICENSE", MANIFEST, SCENARIOS):
        if not required.is_file():
            errors.append(f"{required.relative_to(ROOT)} is missing")
    if errors:
        return errors, manifests
    plugin = json.loads(MANIFEST.read_text(encoding="utf-8"))
    declared = [Path(item.removeprefix("./")).name for item in plugin.get("skills", [])]
    actual = sorted(path.name for path in SKILLS_DIR.iterdir() if path.is_dir())
    if len(declared) != len(set(declared)) or sorted(declared) != actual:
        errors.append(f"plugin skills differ from directories: declared={declared}, actual={actual}")
    for name in actual:
        skill_dir = SKILLS_DIR / name
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"skills/{name}/SKILL.md is missing")
            continue
        metadata, lines = parse_frontmatter(skill_md)
        if set(metadata) != {"name", "description"}:
            errors.append(f"skills/{name}: frontmatter must contain only name and description")
        if metadata.get("name") != name or not NAME_PATTERN.fullmatch(name):
            errors.append(f"skills/{name}: invalid or mismatched skill name")
        if not metadata.get("description"):
            errors.append(f"skills/{name}: description is missing")
        if len(lines) > 500:
            errors.append(f"skills/{name}/SKILL.md exceeds 500 lines")
        if "TODO" in skill_md.read_text(encoding="utf-8"):
            errors.append(f"skills/{name}/SKILL.md contains TODO")
        agent = skill_dir / "agents" / "openai.yaml"
        if not agent.is_file() or f"${name}" not in agent.read_text(encoding="utf-8"):
            errors.append(f"skills/{name}: agents/openai.yaml must mention ${name}")
        found = sorted((skill_dir / "examples").glob("golden-*/Package.swift"))
        if not found:
            errors.append(f"skills/{name}: missing examples/golden-*/Package.swift")
        manifests.extend(found)
    scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8")).get("cases", [])
    covered = {skill for case in scenarios for skill in case.get("expected_skills", [])}
    unknown = sorted(covered - set(actual))
    missing = sorted(set(actual) - covered)
    if unknown:
        errors.append(f"evaluation references unknown skills: {unknown}")
    if missing:
        errors.append(f"evaluation does not cover skills: {missing}")
    ids = [case.get("id") for case in scenarios]
    if any(not case.get("prompt") or not case.get("assertions") for case in scenarios):
        errors.append("every evaluation case requires prompt and assertions")
    if len(ids) != len(set(ids)) or None in ids:
        errors.append("evaluation case ids must be present and unique")
    for markdown in ROOT.rglob("*.md"):
        errors.extend(markdown_errors(markdown))
    for readme in (ROOT / "README.md", ROOT / "README.zh-CN.md"):
        text = readme.read_text(encoding="utf-8")
        if str(len(actual)) not in text or "swift-stable" not in text:
            errors.append(f"{readme.name}: skill count or swift-stable entry is stale")
    return errors, manifests


def check_examples(manifests: list[Path]) -> list[str]:
    swift = shutil.which("swift")
    if swift is None:
        return ["Swift is required for --check-examples"]
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="swift-skills-") as temporary:
        for index, manifest in enumerate(manifests):
            source = manifest.parent
            target = Path(temporary) / f"golden-{index:02d}"
            shutil.copytree(
                source,
                target,
                ignore=shutil.ignore_patterns(".build", ".swiftpm", "Package.resolved"),
            )
            completed = subprocess.run(
                [swift, "run", "--disable-sandbox", "GoldenVerifier"],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            if completed.returncode:
                errors.append(f"golden verifier failed in {source.relative_to(ROOT)}:\n{completed.stdout}")
            else:
                print(f"[OK] {source.relative_to(ROOT)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-examples", action="store_true")
    args = parser.parse_args()
    errors, manifests = inspect_repository()
    if not errors and args.check_examples:
        errors.extend(check_examples(manifests))
    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Validated 7 skills and {len(manifests)} golden examples.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
