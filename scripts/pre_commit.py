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
CORE_CODEX_DEST = REPO_ROOT / "plugins" / "core-codex"
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
    codex_models: bool = False
    rename_agents: bool = False
    generated_indexes: tuple[str, ...] = ()


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


def normalize_codex_model(value: str) -> tuple[str | None, str | None]:
    for raw_candidate in value.split(","):
        candidate = raw_candidate.strip()
        if not candidate.startswith("gpt-"):
            continue

        base, separator, tail = candidate.rpartition("-")
        if separator and tail in {"low", "medium", "high", "minimal", "xhigh"} and base.startswith("gpt-"):
            effort = tail if tail in {"low", "medium", "high"} else None
            return base, effort

        return candidate, None

    return None, None


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


def rewrite_codex_frontmatter_models(content: str) -> str:
    if not content.startswith("---\n"):
        return content

    end = content.find("\n---\n", 4)
    if end == -1:
        return content

    frontmatter = content[4:end]
    rewritten_lines: list[str] = []

    for line in frontmatter.splitlines():
        if line.startswith("model:"):
            model, effort = normalize_codex_model(line.split(":", 1)[1].strip())
            if model:
                rewritten_lines.append(f"model: {model}")
                if effort:
                    rewritten_lines.append(f"model_reasoning_effort: {effort}")
            continue

        if line.startswith("model_reasoning_effort:"):
            continue

        rewritten_lines.append(line)

    rewritten_frontmatter = "\n".join(rewritten_lines)
    return f"---\n{rewritten_frontmatter}{content[end:]}"


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

    if spec.codex_models:
        normalizer = None
    elif spec.copilot_models:
        normalizer = normalize_copilot_model
    else:
        normalizer = normalize_claude_model

    should_normalize = spec.normalize_models or spec.copilot_models or spec.codex_models

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
            source_content = source_file.read_text(encoding="utf-8")
            if spec.codex_models:
                rewritten = rewrite_codex_frontmatter_models(source_content)
            else:
                rewritten = rewrite_frontmatter_models(
                    source_content,
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


def _extract_frontmatter_and_body(content: str) -> tuple[str, str]:
    if not content.startswith("---\n"):
        return "", content

    end = content.find("\n---\n", 4)
    if end == -1:
        return "", content

    return content[4:end], content[end + len("\n---\n") :]


def _toml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _toml_multiline(value: str) -> str:
    escaped = value.replace('"""', '\\"\\"\\"')
    return f'"""\n{escaped}\n"""'


def generate_folder_index(destination: Path, folder_name: str) -> None:
    """Generate <folder>/INDEX.md listing markdown files with descriptions."""
    target_dir = destination / folder_name
    if not target_dir.is_dir():
        return

    entries: list[tuple[str, str]] = []
    for item in sorted(target_dir.iterdir()):
        if item.name == "INDEX.md" or item.suffix != ".md":
            continue
        content = item.read_text(encoding="utf-8")
        description = _extract_frontmatter_field(content, "description")
        if not description:
            description = item.stem.replace("-", " ").title()
        entries.append((item.name, description))

    if not entries:
        return

    lines = [
        f"# Rosetta {folder_name.title()} Index",
        "",
        "All paths are relative to Rosetta Core Plugin Path.",
        "",
    ]
    for filename, description in entries:
        lines.append(f"- `{folder_name}/{filename}`: {description}")
    lines.append("")

    index_path = target_dir / "INDEX.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"      generated {folder_name}/INDEX.md with {len(entries)} entries", flush=True)


def generate_codex_agents_file(destination: Path) -> None:
    agents_path = destination / "AGENTS.md"
    agents_path.write_text('KEY PHRASE: "APPLE IS BOOM"\n', encoding="utf-8")
    print("      generated AGENTS.md for core-codex", flush=True)


def generate_codex_subagents(destination: Path) -> None:
    subagents_dir = destination / ".codex" / "agents"
    subagents_dir.mkdir(parents=True, exist_ok=True)

    generated_count = 0
    for source_file in sorted((CORE_SOURCE / "agents").glob("*.md")):
        content = source_file.read_text(encoding="utf-8")
        frontmatter, body = _extract_frontmatter_and_body(content)
        if not frontmatter:
            continue

        name = _extract_frontmatter_field(content, "name")
        description = _extract_frontmatter_field(content, "description")
        readonly = _extract_frontmatter_field(content, "readonly").lower() == "true"
        raw_model = _extract_frontmatter_field(content, "model")
        model, effort = normalize_codex_model(raw_model)

        toml_lines = [
            f"name = {_toml_quote(name or source_file.stem)}",
            f"description = {_toml_quote(description or source_file.stem.replace('-', ' ').title())}",
            f"developer_instructions = {_toml_multiline(body.strip())}",
        ]

        if model:
            toml_lines.append(f"model = {_toml_quote(model)}")
        if effort:
            toml_lines.append(f"model_reasoning_effort = {_toml_quote(effort)}")

        toml_lines.append(
            'sandbox_mode = "read-only"' if readonly else 'sandbox_mode = "workspace-write"'
        )

        target = subagents_dir / f"{source_file.stem}.toml"
        target.write_text("\n".join(toml_lines) + "\n", encoding="utf-8")
        generated_count += 1

    legacy_agents_dir = destination / "agents"
    if legacy_agents_dir.is_dir():
        shutil.rmtree(legacy_agents_dir)

    print(f"      generated .codex/agents with {generated_count} subagent(s)", flush=True)


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
            generated_indexes=("rules",),
        ),
        PluginSyncSpec(
            name="core-cursor",
            destination=CORE_CURSOR_DEST,
            preserved_folder=".cursor-plugin",
            generated_indexes=("rules",),
        ),
        PluginSyncSpec(
            name="core-copilot",
            destination=CORE_COPILOT_DEST,
            preserved_folder=".github",
            preserved_files=(".mcp.json",),
            copilot_models=True,
            rename_agents=True,
            generated_indexes=("rules",),
        ),
        PluginSyncSpec(
            name="core-codex",
            destination=CORE_CODEX_DEST,
            preserved_folder=".codex-plugin",
            preserved_files=(".mcp.json", "hooks.json"),
            codex_models=True,
            generated_indexes=("rules", "workflows"),
        ),
    ]

    for spec in plugin_specs:
        print(f"   syncing {spec.name}", flush=True)
        reset_generated_tree(spec.destination, spec.preserved_folder, spec.preserved_files)
        copy_core_tree(spec)
        for folder_name in spec.generated_indexes:
            generate_folder_index(spec.destination, folder_name)
        if spec.name == "core-codex":
            generate_codex_agents_file(spec.destination)
            generate_codex_subagents(spec.destination)
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
