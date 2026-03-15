"""Rosetta MCP server package."""

from __future__ import annotations

from typing import Any

try:
    from importlib.metadata import version

    __version__ = version("ims-mcp")
except Exception:
    __version__ = "unknown"

__author__ = "Igor Solomatov"

# Default PostHog Project API Key (injected during CI/CD build from GitHub secret)
DEFAULT_POSTHOG_API_KEY = "__POSTHOG_API_KEY_PLACEHOLDER__"

__all__ = ["mcp", "__version__", "DEFAULT_POSTHOG_API_KEY"]


def __getattr__(name: str) -> Any:
    if name == "mcp":
        from .server import mcp

        return mcp
    raise AttributeError(name)
