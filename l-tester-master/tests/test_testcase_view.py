import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from views.testcase import testcase_view  # noqa: E402


def test_testcase_update_review_status_route_returns_standard_response(monkeypatch):
    async def fake_update_review_status(payload):
        return {
            "id": payload["testcase_id"],
            "review_status": payload["review_status"],
        }

    monkeypatch.setattr(
        testcase_view, "update_testcase_review_status", fake_update_review_status
    )

    app = FastAPI()
    app.include_router(testcase_view.router)
    client = TestClient(app)

    response = client.post(
        "/api/testcase/update_review_status",
        json={"user_id": 1, "testcase_id": 3, "review_status": "approved"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 200
    assert result["data"]["id"] == 3
    assert result["data"]["review_status"] == "approved"
