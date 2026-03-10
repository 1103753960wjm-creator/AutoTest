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


def test_testcase_update_content_route_returns_standard_response(monkeypatch):
    async def fake_edit_testcase_content(payload):
        return {
            "id": payload["testcase_id"],
            "title": payload["title"],
            "version": 2,
        }

    monkeypatch.setattr(testcase_view, "edit_testcase_content", fake_edit_testcase_content)

    app = FastAPI()
    app.include_router(testcase_view.router)
    client = TestClient(app)

    response = client.post(
        "/api/testcase/update_content",
        json={"user_id": 1, "testcase_id": 3, "title": "登录主流程-v2"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 200
    assert result["data"]["id"] == 3
    assert result["data"]["version"] == 2


def test_testcase_batch_update_route_returns_standard_response(monkeypatch):
    async def fake_batch_update_testcases(payload):
        return {
            "success_count": len(payload["testcase_ids"]),
            "failed_count": 0,
            "failed_items": [],
        }

    monkeypatch.setattr(testcase_view, "batch_update_testcases", fake_batch_update_testcases)

    app = FastAPI()
    app.include_router(testcase_view.router)
    client = TestClient(app)

    response = client.post(
        "/api/testcase/batch_update",
        json={"user_id": 1, "testcase_ids": [1, 2], "action_type": "update_priority"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 200
    assert result["data"]["success_count"] == 2


def test_testcase_list_history_route_returns_standard_response(monkeypatch):
    async def fake_get_testcase_history(payload):
        return {
            "testcase": {"id": payload["testcase_id"]},
            "revisions": [],
            "review_logs": [],
        }

    monkeypatch.setattr(testcase_view, "get_testcase_history", fake_get_testcase_history)

    app = FastAPI()
    app.include_router(testcase_view.router)
    client = TestClient(app)

    response = client.post(
        "/api/testcase/list_history",
        json={"user_id": 1, "testcase_id": 3},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 200
    assert result["data"]["testcase"]["id"] == 3


def test_testcase_compare_revisions_route_returns_standard_response(monkeypatch):
    async def fake_compare_testcase_revisions(payload):
        return {
            "testcase_id": payload["testcase_id"],
            "base_revision": {"id": payload["base_revision_id"]},
            "target_revision": {"id": payload["target_revision_id"]},
            "field_diffs": [],
        }

    monkeypatch.setattr(
        testcase_view, "compare_testcase_revisions", fake_compare_testcase_revisions
    )

    app = FastAPI()
    app.include_router(testcase_view.router)
    client = TestClient(app)

    response = client.post(
        "/api/testcase/compare_revisions",
        json={
            "user_id": 1,
            "testcase_id": 3,
            "base_revision_id": 11,
            "target_revision_id": 12,
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 200
    assert result["data"]["testcase_id"] == 3
    assert result["data"]["base_revision"]["id"] == 11


def test_testcase_list_tags_route_returns_standard_response(monkeypatch):
    async def fake_list_testcase_tags(payload):
        return [{"id": 1, "name": "冒烟", "use_count": 3}]

    monkeypatch.setattr(testcase_view, "list_testcase_tags", fake_list_testcase_tags)

    app = FastAPI()
    app.include_router(testcase_view.router)
    client = TestClient(app)

    response = client.post("/api/testcase/list_tags", json={"user_id": 1})

    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 200
    assert result["data"][0]["name"] == "冒烟"


def test_testcase_export_excel_route_returns_file_response(monkeypatch):
    async def fake_export_testcases_excel(payload):
        return (
            "测试用例.xls",
            "<table><tr><td>所属模块</td></tr></table>".encode("utf-8"),
        )

    monkeypatch.setattr(
        testcase_view, "export_testcases_excel", fake_export_testcases_excel
    )

    app = FastAPI()
    app.include_router(testcase_view.router)
    client = TestClient(app)

    response = client.post("/api/testcase/export_excel", json={"user_id": 1})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/vnd.ms-excel")
    assert "attachment;" in response.headers["content-disposition"]
