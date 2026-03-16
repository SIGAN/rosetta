"""Shared path utilities for Rosetta CLI."""

from pathlib import Path


def resolve_workspace_root(path: Path) -> Path:
    """Resolve the workspace root for a publish target.

    Preference order:
    1. Parent of the topmost `instructions/` directory in the target path.
    2. Nearest ancestor containing `.git`.
    3. The target directory itself, or the parent for a file target.
    """
    resolved = path.resolve()
    container = resolved if resolved.is_dir() else resolved.parent

    parts = container.parts
    for index, part in enumerate(parts):
        if part == "instructions" and index > 0:
            return Path(*parts[:index])

    current = container
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent

    return container
