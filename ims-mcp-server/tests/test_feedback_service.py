from types import SimpleNamespace

import ims_mcp.services.feedback as feedback_module
from ims_mcp.config import RosettaConfig
from ims_mcp.context import CallContext
from ims_mcp.services.authorizer import Authorizer
from ims_mcp.services.feedback import FeedbackService


def _call_ctx() -> CallContext:
    return CallContext(
        config=RosettaConfig.from_env(),
        ragflow=SimpleNamespace(),
        dataset_lookup=SimpleNamespace(),
        ctx=None,
        username="tester",
        repository="RulesOfPower",
        tool_name="submit_feedback",
        params={},
        user_email="tester@example.com",
        authorizer=Authorizer("all", "all"),
    )


def test_feedback_service_returns_disabled_when_analytics_missing(monkeypatch):
    monkeypatch.setattr(feedback_module, "get_posthog_client", lambda config: None)

    result = FeedbackService().submit(
        request_mode="coding.md",
        feedback={"summary": "s"},
        call_ctx=_call_ctx(),
    )

    assert result == "Feedback accepted (analytics disabled)."


def test_feedback_service_degrades_gracefully_on_capture_failure(monkeypatch):
    class _FailingPosthog:
        def capture(self, **kwargs):
            raise RuntimeError("network down")

    monkeypatch.setattr(feedback_module, "get_posthog_client", lambda config: _FailingPosthog())

    result = FeedbackService().submit(
        request_mode="coding.md",
        feedback={"summary": "s"},
        call_ctx=_call_ctx(),
    )

    assert result == "Feedback accepted (analytics unavailable)."
