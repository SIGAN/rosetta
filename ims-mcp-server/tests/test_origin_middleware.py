import pytest

from ims_mcp.server import OriginValidationMiddleware


async def _receive():
    return {"type": "http.request"}


def _capture_send(sent):
    async def _send(message):
        sent.append(message)

    return _send


@pytest.mark.asyncio
async def test_origin_middleware_blocks_http_origin_not_in_allowlist():
    calls = []

    async def app(scope, receive, send):
        calls.append("called")

    middleware = OriginValidationMiddleware(app, allowed_origins=["https://allowed.example.com"])
    sent = []

    await middleware(
        {
            "type": "http",
            "headers": [(b"origin", b"https://blocked.example.com")],
        },
        _receive,
        _capture_send(sent),
    )

    assert calls == []
    assert sent == [
        {"type": "http.response.start", "status": 403, "headers": []},
        {"type": "http.response.body", "body": b"Forbidden", "more_body": False},
    ]


@pytest.mark.asyncio
async def test_origin_middleware_blocks_websocket_origin_not_in_allowlist():
    calls = []

    async def app(scope, receive, send):
        calls.append("called")

    middleware = OriginValidationMiddleware(app, allowed_origins=["https://allowed.example.com"])
    sent = []

    await middleware(
        {
            "type": "websocket",
            "headers": [(b"origin", b"https://blocked.example.com")],
        },
        _receive,
        _capture_send(sent),
    )

    assert calls == []
    assert sent == [
        {"type": "websocket.close", "code": 1008, "reason": "Forbidden"},
    ]


@pytest.mark.asyncio
async def test_origin_middleware_allows_missing_origin_header():
    calls = []

    async def app(scope, receive, send):
        calls.append(scope["type"])

    middleware = OriginValidationMiddleware(app, allowed_origins=["https://allowed.example.com"])

    async def _send(_message):
        return None

    await middleware({"type": "http", "headers": []}, _receive, _send)

    assert calls == ["http"]
