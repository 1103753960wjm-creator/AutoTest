import sys
from pathlib import Path

import pytest
from tortoise import Tortoise


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from views.requirement.requirement_common import (  # noqa: E402
    list_page_requirements,
    list_recent_requirements,
    list_requirement_testcases,
    normalize_reviewed_cases_payload,
    save_reviewed_cases,
)
from views.requirement.requirement_model import (  # noqa: E402
    Requirement as RequirementModel,
    Testcase_generation_job as GenerationJobModel,
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


@pytest.mark.anyio
async def test_normalize_reviewed_cases_payload_filters_unreviewed_cases():
    payload = normalize_reviewed_cases_payload(
        {
            "user_id": 1,
            "title": "登录功能",
            "content": "支持账号密码登录",
            "cases": [
                {
                    "case_id": "A-001",
                    "title": "主流程",
                    "module": "认证模块",
                    "reviewed": True,
                    "preconditions": "账号存在\n账号状态正常",
                    "steps": "输入账号密码\n点击登录",
                    "expected_results": "登录成功\n跳转首页",
                },
                {
                    "case_id": "A-002",
                    "title": "未审核草稿",
                    "reviewed": False,
                    "preconditions": ["账号存在"],
                    "steps": ["输入错误密码"],
                    "expected_results": ["登录失败"],
                },
            ],
        }
    )

    assert len(payload["cases"]) == 1
    assert payload["cases"][0]["source_case_id"] == "A-001"
    assert payload["cases"][0]["module"] == "认证模块"
    assert payload["cases"][0]["preconditions"] == ["账号存在", "账号状态正常"]
    assert payload["cases"][0]["expected_results"] == ["登录成功", "跳转首页"]


@pytest.mark.anyio
async def test_save_reviewed_cases_persists_requirement_job_and_testcases():
    await _init_test_db()
    try:
        user = await User_info.create(
            username="ADMIN",
            password="pwd",
            account="admin",
            token="token",
            avatar="",
            phone="",
            email="",
        )

        result = await save_reviewed_cases(
            {
                "user_id": user.id,
                "title": "登录功能",
                "source_type": "feature_design",
                "content": "支持账号密码登录，空密码需要提示",
                "summary": ["支持账号密码登录", "空密码需要提示"],
                "configured_mode": "none",
                "effective_mode": "none",
                "provider_name": "template_rules",
                "cases": [
                    {
                        "case_id": "NONE-001",
                        "title": "主流程登录",
                        "module": "认证模块",
                        "priority": "P1",
                        "category": "happy_path",
                        "target_type": "web",
                        "automatable": True,
                        "reviewed": True,
                        "preconditions": "已准备账号\n账号状态正常",
                        "steps": "输入账号密码\n点击登录",
                        "expected_results": "登录成功\n跳转首页",
                    },
                    {
                        "case_id": "NONE-002",
                        "title": "未审核不保存",
                        "priority": "P2",
                        "category": "negative_path",
                        "target_type": "web",
                        "automatable": False,
                        "reviewed": False,
                        "preconditions": ["已准备账号"],
                        "steps": ["输入错误密码"],
                        "expected_results": ["登录失败"],
                    },
                ],
            }
        )

        requirements = await RequirementModel.all()
        generation_jobs = await GenerationJobModel.all()
        testcases = await CaseModel.all()
        recent = await list_recent_requirements(user.id, 10)
        detail = await list_requirement_testcases(requirements[0].id, user.id)

        assert result["testcase_count"] == 1
        assert len(requirements) == 1
        assert len(generation_jobs) == 1
        assert len(testcases) == 1
        assert generation_jobs[0].requirement_id == requirements[0].id
        assert testcases[0].generation_job_id == generation_jobs[0].id
        assert testcases[0].requirement_id == requirements[0].id
        assert testcases[0].module == "认证模块"
        assert testcases[0].category == "happy_path"
        assert testcases[0].preconditions == ["已准备账号", "账号状态正常"]
        assert recent[0]["testcase_count"] == 1
        assert detail["requirement"]["id"] == requirements[0].id
        assert len(detail["testcases"]) == 1
        assert detail["testcases"][0]["module"] == "认证模块"
        assert detail["testcases"][0]["category"] == "happy_path"
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_list_page_requirements_supports_keyword_and_source_type_filter():
    await _init_test_db()
    try:
        user = await User_info.create(
            username="ADMIN",
            password="pwd",
            account="admin",
            token="token",
            avatar="",
            phone="",
            email="",
        )

        await save_reviewed_cases(
            {
                "user_id": user.id,
                "title": "登录功能",
                "source_type": "feature_design",
                "content": "支持账号密码登录",
                "summary": ["支持账号密码登录"],
                "configured_mode": "none",
                "effective_mode": "none",
                "provider_name": "template_rules",
                "cases": [
                    {
                        "case_id": "NONE-001",
                        "title": "登录主流程",
                        "module": "认证模块",
                        "priority": "P1",
                        "category": "happy_path",
                        "reviewed": True,
                        "preconditions": ["已准备账号"],
                        "steps": ["输入账号密码", "点击登录"],
                        "expected_results": ["登录成功"],
                    }
                ],
            }
        )
        await save_reviewed_cases(
            {
                "user_id": user.id,
                "title": "订单功能",
                "source_type": "requirement_doc",
                "content": "支持订单创建与查询",
                "summary": ["支持订单创建与查询"],
                "configured_mode": "none",
                "effective_mode": "none",
                "provider_name": "template_rules",
                "cases": [
                    {
                        "case_id": "NONE-002",
                        "title": "订单创建",
                        "module": "订单模块",
                        "priority": "P1",
                        "category": "happy_path",
                        "reviewed": True,
                        "preconditions": ["已准备商品"],
                        "steps": ["创建订单"],
                        "expected_results": ["创建成功"],
                    }
                ],
            }
        )

        result = await list_page_requirements(
            {
                "user_id": user.id,
                "currentPage": 1,
                "pageSize": 10,
                "search": {"keyword": "登录", "source_type": "feature_design"},
            }
        )

        assert result["total"] == 1
        assert result["content"][0]["title"] == "登录功能"
        assert result["content"][0]["testcase_count"] == 1
        assert result["content"][0]["effective_mode"] == "none"
        assert result["currentPage"] == 1
        assert result["pageSize"] == 10
    finally:
        await _close_test_db()
