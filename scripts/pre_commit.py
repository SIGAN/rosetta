#!/usr/bin/env python3
"""Native Git pre-commit entrypoint for repository validation."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CORE_SOURCE = REPO_ROOT / "instructions" / "r2" / "core"
CORE_CLAUDE_DEST = REPO_ROOT / "plugins" / "core-claude"
CORE_CURSOR_DEST = REPO_ROOT / "plugins" / "core-cursor"
CORE_COPILOT_DEST = REPO_ROOT / "plugins" / "core-copilot"
TYPECHECK_SCRIPT = REPO_ROOT / "validate-types.sh"
MYPY_CONFIG = REPO_ROOT / "mypy.ini"
ALLOWED_CLAUDE_MODELS = {"opus", "sonnet", "haiku", "inherit"}

COPILOT_MODEL_MAP: dict[str, str] = {
    "opus": "claude-opus-4.6",
    "sonnet": "claude-sonnet-4.6",
    "haiku": "claude-haiku-4.5",
}


@dataclass(frozen=True)
class Check:
    name: str
    runner: Callable[[], int]


@dataclass(frozen=True)
class PluginSyncSpec:
    name: str
    destination: Path
    preserved_folder: str
    preserved_files: tuple[str, ...] = ()
    normalize_models: bool = False
    copilot_models: bool = False
    rename_agents: bool = False


def run_command(command: list[str]) -> int:
    result = subprocess.run(command, cwd=REPO_ROOT, check=False)
    return result.returncode


def normalize_claude_model(value: str) -> str:
    lowered = value.strip().lower()
    if lowered in ALLOWED_CLAUDE_MODELS:
        return lowered
    if "opus" in lowered:
        return "opus"
    if "sonnet" in lowered:
        return "sonnet"
    if "haiku" in lowered:
        return "haiku"
    return "inherit"


def normalize_copilot_model(value: str) -> str:
    lowered = value.strip().lower()
    for key, mapped in COPILOT_MODEL_MAP.items():
        if key in lowered:
            return mapped
    return lowered


def rewrite_frontmatter_models(content: str, normalizer: Callable[[str], str] = normalize_claude_model) -> str:
    if not content.startswith("---\n"):
        return content

    end = content.find("\n---\n", 4)
    if end == -1:
        return content

    frontmatter = content[4:end]

    def replace_model(match: re.Match[str]) -> str:
        prefix = match.group("prefix")
        value = match.group("value")
        suffix = match.group("suffix")
        return f"{prefix}{normalizer(value)}{suffix}"

    updated = re.sub(
        r"(?m)^(?P<prefix>model:\s*)(?P<value>.*?)(?P<suffix>\s*)$",
        replace_model,
        frontmatter,
    )
    return f"---\n{updated}{content[end:]}"


def reset_generated_tree(
    destination: Path,
    preserved_folder: str,
    preserved_files: tuple[str, ...] = (),
) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    preserved = {preserved_folder, *preserved_files}
    deleted_count = 0
    for child in destination.iterdir():
        if child.name in preserved:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
        deleted_count += 1

    print(
        f"      deleted {deleted_count} item(s) from {destination} preserving {', '.join(sorted(preserved))}",
        flush=True,
    )


def copy_core_tree(spec: PluginSyncSpec) -> None:
    destination = spec.destination
    copied_count = 0
    renamed_count = 0

    if spec.copilot_models:
        normalizer = normalize_copilot_model
    else:
        normalizer = normalize_claude_model

    should_normalize = spec.normalize_models or spec.copilot_models

    for source_file in sorted(CORE_SOURCE.rglob("*")):
        relative_path = source_file.relative_to(CORE_SOURCE)
        target = destination / relative_path

        if source_file.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        # Rename agents/*.md → agents/*.agent.md for Copilot
        if spec.rename_agents and _is_agent_file(relative_path):
            target = target.with_suffix(".agent.md")
            renamed_count += 1

        target.parent.mkdir(parents=True, exist_ok=True)

        if should_normalize and source_file.suffix == ".md":
            rewritten = rewrite_frontmatter_models(
                source_file.read_text(encoding="utf-8"),
                normalizer=normalizer,
            )
            target.write_text(rewritten, encoding="utf-8")
            shutil.copystat(source_file, target, follow_symlinks=True)
            copied_count += 1
            continue

        shutil.copy2(source_file, target)
        copied_count += 1

    msg = f"      copied {copied_count} item(s) to {destination}"
    if renamed_count:
        msg += f" (renamed {renamed_count} agent(s) to .agent.md)"
    print(msg, flush=True)


def _extract_frontmatter_field(content: str, field: str) -> str:
    """Extract a field value from YAML frontmatter."""
    if not content.startswith("---\n"):
        return ""
    end = content.find("\n---\n", 4)
    if end == -1:
        return ""
    frontmatter = content[4:end]
    match = re.search(rf"(?m)^{field}:\s*(.+)$", frontmatter)
    return match.group(1).strip() if match else ""


def generate_rules_index(destination: Path) -> None:
    """Generate rules/INDEX.md listing all rule files with descriptions."""
    rules_dir = destination / "rules"
    if not rules_dir.is_dir():
        return

    entries: list[tuple[str, str]] = []
    for rule_file in sorted(rules_dir.iterdir()):
        if rule_file.name == "INDEX.md" or rule_file.suffix != ".md":
            continue
        content = rule_file.read_text(encoding="utf-8")
        description = _extract_frontmatter_field(content, "description")
        if not description:
            description = rule_file.stem.replace("-", " ").title()
        entries.append((rule_file.name, description))

    if not entries:
        return

    lines = [
        "# Rosetta Rules Index",
        "",
        "All paths are relative to Rosetta Core Plugin Path.",
        "",
    ]
    for filename, description in entries:
        lines.append(f"- `rules/{filename}`: {description}")
    lines.append("")

    index_path = rules_dir / "INDEX.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"      generated rules/INDEX.md with {len(entries)} entries", flush=True)


def _is_agent_file(relative_path: Path) -> bool:
    """Check if a relative path is an agent markdown file (agents/<name>.md)."""
    parts = relative_path.parts
    return (
        len(parts) == 2
        and parts[0] == "agents"
        and relative_path.suffix == ".md"
    )


def sync_generated_plugins() -> int:
    if not CORE_SOURCE.is_dir():
        print(f"ERROR: Core source folder not found: {CORE_SOURCE}", file=sys.stderr)
        return 1

    plugin_specs = [
        PluginSyncSpec(
            name="core-claude",
            destination=CORE_CLAUDE_DEST,
            preserved_folder=".claude-plugin",
            normalize_models=True,
        ),
        PluginSyncSpec(
            name="core-cursor",
            destination=CORE_CURSOR_DEST,
            preserved_folder=".cursor-plugin",
        ),
        PluginSyncSpec(
            name="core-copilot",
            destination=CORE_COPILOT_DEST,
            preserved_folder=".github",
            preserved_files=(".mcp.json",),
            copilot_models=True,
            rename_agents=True,
        ),
    ]

    for spec in plugin_specs:
        print(f"   syncing {spec.name}", flush=True)
        reset_generated_tree(spec.destination, spec.preserved_folder, spec.preserved_files)
        copy_core_tree(spec)
        generate_rules_index(spec.destination)
    return 0


def run_type_validation() -> int:
    if os.name != "nt" and TYPECHECK_SCRIPT.is_file():
        bash_path = shutil.which("bash")
        if bash_path:
            return run_command([bash_path, str(TYPECHECK_SCRIPT)])

    if not MYPY_CONFIG.is_file():
        print(f"ERROR: mypy config not found: {MYPY_CONFIG}", file=sys.stderr)
        return 1

    uvx_path = shutil.which("uvx")
    if uvx_path:
        return run_command([uvx_path, "mypy", "--config-file", str(MYPY_CONFIG)])

    if subprocess.run(
        [sys.executable, "-m", "mypy", "--version"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0:
        return run_command([sys.executable, "-m", "mypy", "--config-file", str(MYPY_CONFIG)])

    mypy_path = shutil.which("mypy")
    if mypy_path:
        return run_command([mypy_path, "--config-file", str(MYPY_CONFIG)])

    print(
        "ERROR: No mypy runner found. Install dependencies in the root venv or install uv.",
        file=sys.stderr,
    )
    return 1


def main() -> int:
    checks = [
        Check(name="plugin sync", runner=sync_generated_plugins),
        Check(name="type validation", runner=run_type_validation),
    ]

    for check in checks:
        print(f"==> Running {check.name}", flush=True)
        exit_code = check.runner()
        if exit_code != 0:
            print(f"Pre-commit failed during {check.name}.", file=sys.stderr)
            return exit_code

    print("Pre-commit checks passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
