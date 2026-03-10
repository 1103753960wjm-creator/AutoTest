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
    batch_update_testcases,
    compare_testcase_revisions,
    edit_testcase_content,
    export_testcases_excel,
    get_testcase_history,
    list_testcase_tags,
    list_page_testcases,
    update_testcase_review_status,
)
from views.testcase.testcase_model import (  # noqa: E402
    Testcase as CaseModel,
    Testcase_revision,
    Testcase_review_log,
)
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
async def test_update_testcase_review_status_reject_requires_comment():
    await _init_test_db()
    try:
        user = await _create_user()
        await _seed_testcases(user.id)
        testcase = await CaseModel.first()

        with pytest.raises(ValueError, match="驳回原因"):
            await update_testcase_review_status(
                {
                    "user_id": user.id,
                    "testcase_id": testcase.id,
                    "review_status": "rejected",
                }
            )
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_update_testcase_review_status_updates_record_and_creates_log():
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
                "review_comment": "预期结果描述不完整",
                "review_reason_type": "expected_result_issue",
            }
        )
        updated = await CaseModel.get(id=testcase.id)
        review_logs = await Testcase_review_log.filter(testcase_id=testcase.id)

        assert result["id"] == testcase.id
        assert result["review_status"] == "rejected"
        assert result["latest_review_comment"] == "预期结果描述不完整"
        assert updated.review_status == "rejected"
        assert updated.latest_review_comment == "预期结果描述不完整"
        assert len(review_logs) == 1
        assert review_logs[0].to_status == "rejected"
        assert review_logs[0].review_reason_type == "expected_result_issue"
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_edit_testcase_content_updates_fields_creates_revision_and_sets_risk():
    await _init_test_db()
    try:
        user = await _create_user()
        await _seed_testcases(user.id)
        testcase = await CaseModel.get(title="登录主流程")
        await Automation_draft.create(
            testcase_id=testcase.id,
            requirement_id=testcase.requirement_id,
            target_type="web",
            requested_mode="none",
            effective_mode="none",
            provider_name="template_rules",
            draft_payload={"menu_name": "登录主流程 Web 草稿", "script": [{"name": "step-1"}]},
            warnings=[],
            save_status="saved",
            target_asset_id=21,
            target_menu_id=31,
            user_id=user.id,
        )

        result = await edit_testcase_content(
            {
                "user_id": user.id,
                "testcase_id": testcase.id,
                "module": "登录设计区",
                "title": "登录主流程-改",
                "preconditions": "账号已准备\n账号状态正常",
                "steps": "输入账号\n输入密码\n点击登录",
                "expected_results": "登录成功\n跳转首页",
                "priority": "P0",
                "target_type": "api",
                "automatable": True,
            }
        )

        updated = await CaseModel.get(id=testcase.id)
        revisions = await Testcase_revision.filter(testcase_id=testcase.id)
        page_result = await list_page_testcases(
            {
                "user_id": user.id,
                "currentPage": 1,
                "pageSize": 10,
                "search": {"keyword": "登录主流程-改"},
            }
        )

        assert result["version"] == 2
        assert updated.version == 2
        assert updated.module == "登录设计区"
        assert updated.title == "登录主流程-改"
        assert updated.preconditions == ["账号已准备", "账号状态正常"]
        assert updated.steps == ["输入账号", "输入密码", "点击登录"]
        assert updated.expected_results == ["登录成功", "跳转首页"]
        assert updated.priority == "P0"
        assert updated.target_type == "api"
        assert len(revisions) == 1
        assert revisions[0].version == 1
        assert revisions[0].snapshot["title"] == "登录主流程"
        assert page_result["content"][0]["revision_count"] == 1
        assert page_result["content"][0]["automation_risk"]["has_risk"] is True
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_batch_update_testcases_returns_success_and_failed_items():
    await _init_test_db()
    try:
        user = await _create_user()
        await _seed_testcases(user.id)
        testcases = await CaseModel.all().order_by("id")

        result = await batch_update_testcases(
            {
                "user_id": user.id,
                "testcase_ids": [testcases[0].id, testcases[1].id, 9999],
                "action_type": "update_priority",
                "action_payload": {"priority": "P0"},
            }
        )

        refreshed = await CaseModel.all().order_by("id")

        assert result["success_count"] == 2
        assert result["failed_count"] == 1
        assert result["failed_items"][0]["id"] == 9999
        assert refreshed[0].priority == "P0"
        assert refreshed[1].priority == "P0"
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_get_testcase_history_returns_revisions_and_review_logs():
    await _init_test_db()
    try:
        user = await _create_user()
        await _seed_testcases(user.id)
        testcase = await CaseModel.first()

        await edit_testcase_content(
            {
                "user_id": user.id,
                "testcase_id": testcase.id,
                "module": testcase.module,
                "title": testcase.title + "-v2",
                "preconditions": testcase.preconditions,
                "steps": testcase.steps,
                "expected_results": testcase.expected_results,
                "priority": testcase.priority,
                "target_type": testcase.target_type,
                "automatable": testcase.automatable,
            }
        )
        await update_testcase_review_status(
            {
                "user_id": user.id,
                "testcase_id": testcase.id,
                "review_status": "approved",
                "review_comment": "设计已确认",
            }
        )

        history = await get_testcase_history(
            {
                "user_id": user.id,
                "testcase_id": testcase.id,
            }
        )

        assert history["testcase"]["id"] == testcase.id
        assert len(history["revisions"]) == 1
        assert history["revisions"][0]["version"] == 1
        assert len(history["review_logs"]) == 1
        assert history["review_logs"][0]["review_comment"] == "设计已确认"
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_export_testcases_excel_returns_chinese_headers_and_rows():
    await _init_test_db()
    try:
        user = await _create_user()
        await _seed_testcases(user.id)

        filename, content = await export_testcases_excel(
            {
                "user_id": user.id,
                "search": {"keyword": "登录"},
            }
        )

        text = content.decode("utf-8")
        assert filename.endswith(".xls")
        assert "所属模块" in text
        assert "用例标题" in text
        assert "前置条件" in text
        assert "测试步骤" in text
        assert "预期结果" in text
        assert "优先级" in text
        assert "主流程" in text
        assert "认证模块" in text
        assert "登录主流程" in text
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_update_testcase_review_status_records_reason_type_and_list_page_shows_label():
    await _init_test_db()
    try:
        user = await _create_user()
        await _seed_testcases(user.id)
        testcase = await CaseModel.first()

        result = await update_testcase_review_status(
            {
                "user_id": user.id,
                "testcase_id": testcase.id,
                "review_status": "approved",
                "review_comment": "设计完整，可进入下一步",
                "review_reason_type": "design_complete",
            }
        )
        review_logs = await Testcase_review_log.filter(testcase_id=testcase.id)
        page_result = await list_page_testcases(
            {
                "user_id": user.id,
                "currentPage": 1,
                "pageSize": 10,
                "search": {"review_reason_type": "design_complete"},
            }
        )

        assert result["latest_review_reason_type"] == "design_complete"
        assert result["latest_review_reason_type_label"] == "设计完整"
        assert review_logs[0].review_reason_type == "design_complete"
        assert page_result["total"] == 1
        assert page_result["content"][0]["latest_review_reason_type_label"] == "设计完整"
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_update_testcase_review_status_reject_requires_reason_type():
    await _init_test_db()
    try:
        user = await _create_user()
        await _seed_testcases(user.id)
        testcase = await CaseModel.first()

        with pytest.raises(ValueError, match="驳回原因类型"):
            await update_testcase_review_status(
                {
                    "user_id": user.id,
                    "testcase_id": testcase.id,
                    "review_status": "rejected",
                    "review_comment": "步骤不完整",
                }
            )
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_edit_testcase_content_updates_tags_and_tag_filter_works():
    await _init_test_db()
    try:
        user = await _create_user()
        await _seed_testcases(user.id)
        testcase = await CaseModel.get(title="登录主流程")

        result = await edit_testcase_content(
            {
                "user_id": user.id,
                "testcase_id": testcase.id,
                "module": testcase.module,
                "title": testcase.title,
                "preconditions": testcase.preconditions,
                "steps": testcase.steps,
                "expected_results": testcase.expected_results,
                "priority": testcase.priority,
                "target_type": testcase.target_type,
                "automatable": testcase.automatable,
                "tag_names": ["冒烟", "登录", "冒烟"],
            }
        )
        filtered = await list_page_testcases(
            {
                "user_id": user.id,
                "currentPage": 1,
                "pageSize": 10,
                "search": {"tag_names": ["冒烟"]},
            }
        )
        tags = await list_testcase_tags({"user_id": user.id})

        assert result["tag_names"] == ["冒烟", "登录"]
        assert filtered["total"] == 1
        assert filtered["content"][0]["tag_names"] == ["冒烟", "登录"]
        assert {item["name"] for item in tags} == {"冒烟", "登录"}
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_batch_update_testcases_supports_add_and_remove_tags():
    await _init_test_db()
    try:
        user = await _create_user()
        await _seed_testcases(user.id)
        testcases = await CaseModel.all().order_by("id")

        add_result = await batch_update_testcases(
            {
                "user_id": user.id,
                "testcase_ids": [item.id for item in testcases],
                "action_type": "add_tags",
                "action_payload": {"tag_names": ["回归", "核心链路"]},
            }
        )
        remove_result = await batch_update_testcases(
            {
                "user_id": user.id,
                "testcase_ids": [testcases[0].id],
                "action_type": "remove_tags",
                "action_payload": {"tag_names": ["回归"]},
            }
        )
        first_row = (
            await list_page_testcases(
                {
                    "user_id": user.id,
                    "currentPage": 1,
                    "pageSize": 10,
                    "search": {"keyword": "主流程"},
                }
            )
        )["content"][0]
        second_row = (
            await list_page_testcases(
                {
                    "user_id": user.id,
                    "currentPage": 1,
                    "pageSize": 10,
                    "search": {"keyword": "异常流程"},
                }
            )
        )["content"][0]

        assert add_result["success_count"] == 2
        assert remove_result["success_count"] == 1
        assert first_row["tag_names"] == ["核心链路"]
        assert second_row["tag_names"] == ["回归", "核心链路"]
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_batch_update_review_status_supports_reason_type():
    await _init_test_db()
    try:
        user = await _create_user()
        await _seed_testcases(user.id)
        testcases = await CaseModel.all().order_by("id")

        result = await batch_update_testcases(
            {
                "user_id": user.id,
                "testcase_ids": [item.id for item in testcases],
                "action_type": "update_review_status",
                "action_payload": {
                    "review_status": "approved",
                    "review_comment": "设计已统一确认",
                    "review_reason_type": "scope_clear",
                },
            }
        )
        review_logs = await Testcase_review_log.all()

        assert result["success_count"] == 2
        assert len(review_logs) == 2
        assert all(item.review_reason_type == "scope_clear" for item in review_logs)
    finally:
        await _close_test_db()


@pytest.mark.anyio
async def test_compare_testcase_revisions_returns_field_diffs():
    await _init_test_db()
    try:
        user = await _create_user()
        await _seed_testcases(user.id)
        testcase = await CaseModel.get(title="登录主流程")

        await edit_testcase_content(
            {
                "user_id": user.id,
                "testcase_id": testcase.id,
                "module": "认证模块",
                "title": "登录主流程-v2",
                "preconditions": "已准备账号",
                "steps": "输入账号密码\n点击登录",
                "expected_results": "登录成功",
                "priority": "P1",
                "target_type": "api",
                "automatable": True,
            }
        )
        testcase = await CaseModel.get(id=testcase.id)
        await edit_testcase_content(
            {
                "user_id": user.id,
                "testcase_id": testcase.id,
                "module": "登录设计区",
                "title": "登录主流程-v3",
                "preconditions": "已准备账号\n账号状态正常",
                "steps": "输入账号密码\n点击登录\n验证跳转",
                "expected_results": "登录成功\n进入首页",
                "priority": "P0",
                "target_type": "web",
                "automatable": False,
            }
        )
        revisions = await Testcase_revision.filter(testcase_id=testcase.id).order_by("id")

        compare_result = await compare_testcase_revisions(
            {
                "user_id": user.id,
                "testcase_id": testcase.id,
                "base_revision_id": revisions[0].id,
                "target_revision_id": revisions[1].id,
            }
        )

        diff_map = {item["field"]: item for item in compare_result["field_diffs"]}
        assert diff_map["title"]["before"] == "登录主流程"
        assert diff_map["title"]["after"] == "登录主流程-v2"
        assert diff_map["title"]["changed"] is True
        assert diff_map["module"]["changed"] is False
        assert diff_map["target_type"]["after"] == "接口"
        assert diff_map["automatable"]["after"] == "是"
    finally:
        await _close_test_db()
