"""Feedback submission service."""

from __future__ import annotations

from ims_mcp.analytics.tracker import get_posthog_client, get_session_id
from ims_mcp.constants import ANALYTICS_MCP_SERVER
from ims_mcp.context import CallContext
from ims_mcp import __version__
from ims_mcp.typing_utils import JsonObject


class FeedbackService:
    def submit(self, request_mode: str, feedback: JsonObject, call_ctx: CallContext) -> str:
        posthog = get_posthog_client(call_ctx.config)
        if not posthog:
            return "Feedback accepted (analytics disabled)."

        properties = {
            "request_mode": request_mode,
            "username": call_ctx.username,
            "repository": call_ctx.repository,
            "mcp_server": ANALYTICS_MCP_SERVER,
            "mcp_server_version": __version__,
            "$session_id": get_session_id(),
            **feedback,
        }
        distinct_id = f"{call_ctx.username}@{call_ctx.repository}"
        try:
            posthog.capture(distinct_id=distinct_id, event="feedback_submitted", properties=properties)
        except Exception:
            return "Feedback accepted (analytics unavailable)."
        return "Feedback submitted successfully."
