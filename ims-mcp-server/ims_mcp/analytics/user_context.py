"""User and repository extraction for analytics."""

from __future__ import annotations

import os
import subprocess
import time
from typing import Any

from ims_mcp.constants import REPOSITORY_CACHE_TTL_SECONDS

_cached_username: str | None = None
_cached_repository: str | None = None
_repository_cache_time: float | None = None
_cached_agent_name: str | None = None
_cached_agent_version: str | None = None


def get_username() -> str:
    global _cached_username
    if _cached_username is not None:
        return _cached_username

    username = os.getenv("USER") or os.getenv("USERNAME") or os.getenv("LOGNAME")
    if not username:
        try:
            result = subprocess.run(["whoami"], capture_output=True, text=True, timeout=1, check=False)
            if result.returncode == 0:
                username = result.stdout.strip()
        except Exception:
            username = None

    _cached_username = username or "unknown"
    return _cached_username


async def get_repository_from_context(ctx: Any) -> str:
    global _cached_repository, _repository_cache_time

    now = time.time()
    if _cached_repository and _repository_cache_time and now - _repository_cache_time < REPOSITORY_CACHE_TTL_SECONDS:
        return _cached_repository

    result = "unknown"
    try:
        session = ctx.request_context.session
        roots_result = await session.list_roots()
        if roots_result and roots_result.roots:
            repo_names = [os.path.basename(str(root.uri)).rstrip("/") for root in roots_result.roots]
            result = ", ".join(repo_names)
    except Exception:
        pass

    if result == "unknown":
        try:
            client_id = getattr(ctx, "client_id", "")
            if client_id and "/" in str(client_id):
                path = str(client_id).split(":", 1)[-1]
                repo = os.path.basename(path.rstrip("/"))
                if repo:
                    result = repo
        except Exception:
            pass

    _cached_repository = result
    _repository_cache_time = now
    return result


def get_agent_info_from_context(ctx: Any) -> tuple[str, str]:
    global _cached_agent_name, _cached_agent_version
    if _cached_agent_name is not None and _cached_agent_version is not None:
        return _cached_agent_name, _cached_agent_version

    try:
        client_info = (
            getattr(getattr(getattr(ctx, "session", None), "client_params", None), "clientInfo", None)
            or getattr(getattr(getattr(ctx, "session", None), "client_params", None), "client_info", None)
        )
        name = getattr(client_info, "name", None) if client_info else None
        version = getattr(client_info, "version", None) if client_info else None
        _cached_agent_name = name or "unknown"
        _cached_agent_version = version or "unknown"
    except Exception:
        _cached_agent_name = "unknown"
        _cached_agent_version = "unknown"

    return _cached_agent_name, _cached_agent_version
