import sys
from pathlib import Path

import pytest
from tortoise import Tortoise


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from views.requirement.requirement_common import save_reviewed_cases  # noqa: E402
from views.automation_draft.automation_draft_model import Automation_draft  # noqa: E402
from views.testcase.testcase_common import (  # noqa: E402
    list_page_testcases,
    update_testcase_review_status,
)
from views.testcase.testcase_model import Testcase as CaseModel  # noqa: E402
from views.user.user_model import User_info  # noqa: E402


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def _init_test_db():
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={
            "models": [
                "views.user.user_model",
                "views.requirement.requirement_model",
                "views.testcase.testcase_model",
                "views.automation_draft.automation_draft_model",
            ]
        },
    )
    await Tortoise.generate_schemas()


async def _close_test_db():
    await Tortoise.close_connections()


async def _create_user():
    return await User_info.create(
        username="ADMIN",
        password="pwd",
        account="admin",
        token="token",
        avatar="",
        phone="",
        email="",
    )


async def _seed_testcases(user_id: int):
    await save_reviewed_cases(
        {
            "user_id": user_id,
            "title": "登录功能",
            "source_type": "feature_design",
            "content": "支持账号密码登录",
            "summary": ["支持账号密码登录"],
            "configured_mode": "none",
            "effective_mode": "none",
            "provider_name": "template_rules",
            "cases": [
                {
                    "case_id": "CASE-001",
                    "title": "登录主流程",
                    "module": "认证模块",
                    "priority": "P1",
                    "category": "happy_path",
                    "target_type": "web",
                    "reviewed": True,
                    "preconditions": ["已准备账号"],
                    "steps": ["输入账号密码", "点击登录"],
                    "expected_results": ["登录成功"],
                },
                {
                    "case_id": "CASE-002",
                    "title": "登录异常流程",
                    "module": "认证模块",
                    "priority": "P2",
                    "category": "negative_path",
                    "target_type": "web",
                    "reviewed": True,
                    "preconditions": ["已准备账号"],
                    "steps": ["输入错误密码", "点击登录"],
                    "expected_results": ["登录失败"],
                },
            ],
        }
    )


@pytest.mark.anyio
async def test_list_page_testcases_supports_filters_and_returns_module_and_category():
    await _init_test_db()
    try:
        user = await _create_user()
        await _seed_testcases(user.id)

        result = await list_page_testcases(
            {
                "user_id": user.id,
                "currentPage": 1,
                "pageSize": 10,
                "search": {
                    "keyword": "主流程",
                    "review_status": "approved",
                    "target_type": "web",
                },
            }
        )

        assert result["total"] == 1
        assert result["content"][0]["title"] == "登录主流程"
        assert result["content"][0]["module"] == "认证模块"
        assert result["content"][0]["category"] == "happy_path"
        assert result["content"][0]["review_status"] == "approved"
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_list_page_testcases_returns_automation_summary():
    await _init_test_db()
    try:
        user = await _create_user()
        await _seed_testcases(user.id)
        testcase = await CaseModel.get(title="登录主流程")

        await Automation_draft.create(
            testcase_id=testcase.id,
            requirement_id=testcase.requirement_id,
            target_type="api",
            requested_mode="none",
            effective_mode="none",
            provider_name="template_rules",
            draft_payload={"name": "旧 API 草稿", "script": [{"name": "step-1"}]},
            warnings=[],
            save_status="draft",
            user_id=user.id,
        )
        latest_api = await Automation_draft.create(
            testcase_id=testcase.id,
            requirement_id=testcase.requirement_id,
            target_type="api",
            requested_mode="none",
            effective_mode="none",
            provider_name="template_rules",
            draft_payload={"name": "新 API 草稿", "script": [{"name": "step-2"}]},
            warnings=[],
            save_status="saved",
            target_asset_id=11,
            user_id=user.id,
        )
        latest_web = await Automation_draft.create(
            testcase_id=testcase.id,
            requirement_id=testcase.requirement_id,
            target_type="web",
            requested_mode="none",
            effective_mode="none",
            provider_name="template_rules",
            draft_payload={"menu_name": "Web 草稿", "script": [{"name": "step-1"}]},
            warnings=[],
            save_status="saved",
            target_asset_id=21,
            target_menu_id=31,
            user_id=user.id,
        )

        result = await list_page_testcases(
            {
                "user_id": user.id,
                "currentPage": 1,
                "pageSize": 10,
                "search": {"keyword": "主流程"},
            }
        )

        summary = result["content"][0]["automation_summary"]
        api_item = next(item for item in summary["latest_items"] if item["target_type"] == "api")
        web_item = next(item for item in summary["latest_items"] if item["target_type"] == "web")

        assert summary["latest_draft_count"] == 2
        assert api_item["draft_id"] == latest_api.id
        assert api_item["target_asset_id"] == 11
        assert api_item["target_route"] == "/_api_script"
        assert api_item["target_route_query"]["asset_id"] == 11
        assert web_item["draft_id"] == latest_web.id
        assert web_item["target_menu_id"] == 31
        assert web_item["target_route"] == "/web"
        assert web_item["target_route_query"]["menu_id"] == 31
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_update_testcase_review_status_rejects_invalid_status():
    await _init_test_db()
    try:
        user = await _create_user()
        await _seed_testcases(user.id)
        testcase = await CaseModel.first()

        with pytest.raises(ValueError, match="审核状态"):
            await update_testcase_review_status(
                {
                    "user_id": user.id,
                    "testcase_id": testcase.id,
                    "review_status": "done",
                }
            )
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_update_testcase_review_status_updates_record():
    await _init_test_db()
    try:
        user = await _create_user()
        await _seed_testcases(user.id)
        testcase = await CaseModel.first()

        result = await update_testcase_review_status(
            {
                "user_id": user.id,
                "testcase_id": testcase.id,
                "review_status": "rejected",
            }
        )
        updated = await CaseModel.get(id=testcase.id)

        assert result["id"] == testcase.id
        assert result["review_status"] == "rejected"
        assert updated.review_status == "rejected"
    finally:
        await _close_test_db()
