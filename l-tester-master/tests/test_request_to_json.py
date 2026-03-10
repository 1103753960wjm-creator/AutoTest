import sys
from pathlib import Path

import pytest
from starlette.requests import Request


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from common.request_to_json import body_to_json  # noqa: E402


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _build_request(body: bytes = b"", headers=None) -> Request:
    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/test",
        "headers": headers or [],
        "query_string": b"",
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "scheme": "http",
        "http_version": "1.1",
    }
    return Request(scope, receive)


@pytest.mark.anyio
async def test_body_to_json_supports_header_auth_when_body_empty():
    request = _build_request(
        headers=[
            (b"authorization", b"Bearer token-123"),
            (b"x-user-id", b"7"),
        ]
    )

    result = await body_to_json(request)

    assert result["token"] == "token-123"
    assert result["user_id"] == "7"


@pytest.mark.anyio
async def test_body_to_json_keeps_body_and_backfills_missing_auth_fields():
    request = _build_request(
        body=b'{"name":"demo","user_id":"9"}',
        headers=[(b"x-token", b"token-456")],
    )

    result = await body_to_json(request)

    assert result["name"] == "demo"
    assert result["user_id"] == "9"
    assert result["token"] == "token-456"
