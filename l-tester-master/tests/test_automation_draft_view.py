import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from views.automation_draft import automation_draft_view  # noqa: E402


def test_generate_automation_draft_route_returns_standard_response(monkeypatch):
    async def fake_generate(payload):
        return {"id": 1, "target_type": payload["target_type"]}

    monkeypatch.setattr(automation_draft_view, "generate_automation_draft", fake_generate)

    app = FastAPI()
    app.include_router(automation_draft_view.router)
    client = TestClient(app)

    response = client.post(
        "/api/automation_draft/generate",
        json={"user_id": 1, "testcase_id": 2, "target_type": "api"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 200
    assert result["data"]["id"] == 1
    assert result["data"]["target_type"] == "api"


def test_save_automation_draft_route_returns_standard_response(monkeypatch):
    async def fake_save(payload):
        return {
            "draft_id": payload["draft_id"],
            "target_route": "/web",
            "target_asset_id": 8,
            "target_route_query": {
                "menu_id": 18,
                "draft_id": payload["draft_id"],
                "source": "testcase_automation",
            },
        }

    monkeypatch.setattr(automation_draft_view, "save_automation_draft", fake_save)

    app = FastAPI()
    app.include_router(automation_draft_view.router)
    client = TestClient(app)

    response = client.post(
        "/api/automation_draft/save_to_asset",
        json={"user_id": 1, "draft_id": 3, "edited_payload": {"menu_name": "test"}},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 200
    assert result["data"]["draft_id"] == 3
    assert result["data"]["target_route"] == "/web"
    assert result["data"]["target_route_query"]["menu_id"] == 18
