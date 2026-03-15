import pytest

import ims_mcp.analytics.tracker as tracker_module
from ims_mcp.analytics.tracker import track_tool_call


@pytest.mark.asyncio
async def test_track_tool_call_wraps_unexpected_exception_as_error(monkeypatch):
    monkeypatch.setattr(tracker_module, "get_posthog_client", lambda config=None: None)
    monkeypatch.setattr(tracker_module, "capture_error_to_posthog", lambda *args, **kwargs: None)

    @track_tool_call
    async def boom(ctx=None):
        raise RuntimeError("boom")

    result = await boom(ctx=None)

    assert result == "Error: boom call failed: boom"
