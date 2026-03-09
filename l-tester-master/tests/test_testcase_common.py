import sys
from pathlib import Path

import pytest
from tortoise import Tortoise


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from views.requirement.requirement_common import save_reviewed_cases  # noqa: E402
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
