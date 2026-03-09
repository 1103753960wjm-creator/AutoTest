import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from views.requirement import requirement_view  # noqa: E402


def test_requirement_list_page_route_returns_standard_response(monkeypatch):
    async def fake_list_page_requirements(payload):
        return {
            "content": [{"id": 1, "title": "登录功能"}],
            "currentPage": payload["currentPage"],
            "pageSize": payload["pageSize"],
            "total": 1,
        }

    monkeypatch.setattr(
        requirement_view, "list_page_requirements", fake_list_page_requirements
    )

    app = FastAPI()
    app.include_router(requirement_view.router)
    client = TestClient(app)

    response = client.post(
        "/api/requirement/list_page",
        json={"user_id": 1, "currentPage": 1, "pageSize": 10, "search": {}},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 200
    assert result["data"]["total"] == 1
    assert result["data"]["content"][0]["title"] == "登录功能"
