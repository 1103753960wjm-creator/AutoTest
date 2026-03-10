import sys
from pathlib import Path

import pytest
from tortoise import Tortoise


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from views.api.api_model import Api_script  # noqa: E402
from views.app.app_model import App_menu, App_script  # noqa: E402
from views.automation_draft.automation_draft_common import (  # noqa: E402
    generate_automation_draft,
    get_automation_draft_info,
    list_testcase_automation_drafts,
    save_automation_draft,
)
from views.automation_draft.automation_draft_model import Automation_draft  # noqa: E402
from views.requirement.requirement_common import save_reviewed_cases  # noqa: E402
from views.testcase.testcase_model import Testcase as CaseModel  # noqa: E402
from views.user.user_model import User_info  # noqa: E402
from views.web.web_model import Web_menu, Web_script  # noqa: E402


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
                "views.api.api_model",
                "views.web.web_model",
                "views.app.app_model",
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


async def _seed_reviewed_testcase(user_id: int) -> CaseModel:
    await save_reviewed_cases(
        {
            "user_id": user_id,
            "title": "登录功能",
            "source_type": "feature_design",
            "content": "支持账号密码登录，输入正确凭证后进入首页",
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
                    "automatable": True,
                    "reviewed": True,
                    "preconditions": ["已准备账号"],
                    "steps": ["打开登录页", "输入账号密码", "点击登录"],
                    "expected_results": ["登录成功", "进入首页"],
                }
            ],
        }
    )
    return await CaseModel.first()


@pytest.mark.anyio
async def test_generate_automation_draft_requires_approved_testcase():
    await _init_test_db()
    try:
        user = await _create_user()
        testcase = await _seed_reviewed_testcase(user.id)
        testcase.review_status = "draft"
        await testcase.save(update_fields=["review_status"])

        with pytest.raises(ValueError, match="已审核"):
            await generate_automation_draft(
                {"user_id": user.id, "testcase_id": testcase.id, "target_type": "api"}
            )
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_generate_and_save_api_automation_draft_persists_trace():
    await _init_test_db()
    try:
        user = await _create_user()
        testcase = await _seed_reviewed_testcase(user.id)

        generated = await generate_automation_draft(
            {
                "user_id": user.id,
                "testcase_id": testcase.id,
                "target_type": "api",
                "mode": "none",
            }
        )
        saved = await save_automation_draft(
            {
                "user_id": user.id,
                "draft_id": generated["id"],
                "edited_payload": generated["draft_payload"],
            }
        )
        draft_info = await get_automation_draft_info(
            {"user_id": user.id, "draft_id": generated["id"]}
        )
        draft_list = await list_testcase_automation_drafts(
            {"user_id": user.id, "testcase_id": testcase.id}
        )

        assert generated["target_type"] == "api"
        assert saved["target_route"] == "/_api_script"
        assert saved["target_route_query"] == {
            "asset_id": saved["target_asset_id"],
            "draft_id": generated["id"],
            "source": "testcase_automation",
        }
        assert saved["source_testcase_id"] == testcase.id
        assert await Api_script.all().count() == 1
        assert draft_info["save_status"] == "saved"
        assert draft_info["target_asset_id"] == saved["target_asset_id"]
        assert draft_info["target_route_query"]["asset_id"] == saved["target_asset_id"]
        assert draft_list[0]["target_asset_id"] == saved["target_asset_id"]
        assert draft_list[0]["target_route_query"]["asset_id"] == saved["target_asset_id"]
        assert draft_list[0]["testcase"]["title"] == "登录主流程"
        assert await Automation_draft.all().count() == 1
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_save_web_and_app_automation_draft_creates_menu_and_script_assets():
    await _init_test_db()
    try:
        user = await _create_user()
        testcase = await _seed_reviewed_testcase(user.id)

        web_generated = await generate_automation_draft(
            {
                "user_id": user.id,
                "testcase_id": testcase.id,
                "target_type": "web",
                "mode": "none",
            }
        )
        web_saved = await save_automation_draft(
            {
                "user_id": user.id,
                "draft_id": web_generated["id"],
                "edited_payload": web_generated["draft_payload"],
            }
        )

        app_generated = await generate_automation_draft(
            {
                "user_id": user.id,
                "testcase_id": testcase.id,
                "target_type": "app",
                "mode": "none",
            }
        )
        app_saved = await save_automation_draft(
            {
                "user_id": user.id,
                "draft_id": app_generated["id"],
                "edited_payload": app_generated["draft_payload"],
            }
        )

        assert web_saved["target_route"] == "/web"
        assert app_saved["target_route"] == "/app_auto"
        assert web_saved["target_route_query"] == {
            "menu_id": web_saved["target_menu_id"],
            "draft_id": web_generated["id"],
            "source": "testcase_automation",
        }
        assert app_saved["target_route_query"] == {
            "menu_id": app_saved["target_menu_id"],
            "draft_id": app_generated["id"],
            "source": "testcase_automation",
        }
        assert await Web_script.all().count() == 1
        assert await App_script.all().count() == 1
        assert await Web_menu.filter(name="AI生成草稿", type=1).exists()
        assert await App_menu.filter(name="AI生成草稿", type=1).exists()
        assert web_saved["target_menu_id"] is not None
        assert app_saved["target_menu_id"] is not None
    finally:
        await _close_test_db()
