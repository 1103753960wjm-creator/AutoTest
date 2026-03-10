from typing import Any, Dict, List

from tortoise.transactions import in_transaction

from views.ai.ai_service import AIGatewayService
from views.api.api_model import Api_script
from views.app.app_model import App_menu, App_script
from views.automation_draft.automation_draft_model import Automation_draft
from views.testcase.testcase_model import Testcase
from views.web.web_model import Web_menu, Web_script


VALID_AUTOMATION_TARGET_TYPES = {"api", "web", "app"}
VALID_AUTOMATION_SAVE_STATUS = {"draft", "saved"}


def _normalize_string(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text or default


def _normalize_user_id(payload: Dict[str, Any]) -> int:
    user_id = int(payload.get("user_id") or 0)
    if user_id <= 0:
        raise ValueError("缺少用户信息，无法处理自动化草稿")
    return user_id


def _normalize_target_type(value: Any) -> str:
    target_type = _normalize_string(value).lower()
    if target_type not in VALID_AUTOMATION_TARGET_TYPES:
        raise ValueError("目标类型仅支持 api、web、app")
    return target_type


def _normalize_dict(value: Any, field_name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} 格式不正确")
    return value


def _build_api_route() -> str:
    return "/_api_script"


def _build_web_route() -> str:
    return "/web"


def _build_app_route() -> str:
    return "/app_auto"


def _build_target_route(target_type: str) -> str:
    if target_type == "api":
        return _build_api_route()
    if target_type == "web":
        return _build_web_route()
    if target_type == "app":
        return _build_app_route()
    return ""


def _build_target_route_query(
    target_type: str,
    *,
    draft_id: int,
    target_asset_id: Any = None,
    target_menu_id: Any = None,
) -> Dict[str, Any]:
    query: Dict[str, Any] = {
        "draft_id": draft_id,
        "source": "testcase_automation",
    }
    if target_type == "api" and target_asset_id:
        query["asset_id"] = target_asset_id
    elif target_type in {"web", "app"} and target_menu_id:
        query["menu_id"] = target_menu_id
    return query


def _serialize_testcase(testcase: Testcase) -> Dict[str, Any]:
    return {
        "id": testcase.id,
        "requirement_id": testcase.requirement_id,
        "title": testcase.title,
        "module": testcase.module,
        "priority": testcase.priority,
        "category": testcase.category,
        "preconditions": testcase.preconditions,
        "steps": testcase.steps,
        "expected_results": testcase.expected_results,
        "target_type": testcase.target_type,
        "automatable": testcase.automatable,
        "review_status": testcase.review_status,
    }


def _serialize_draft(draft: Automation_draft, testcase: Testcase) -> Dict[str, Any]:
    target_route = _build_target_route(draft.target_type)

    return {
        "id": draft.id,
        "testcase_id": draft.testcase_id,
        "requirement_id": draft.requirement_id,
        "target_type": draft.target_type,
        "requested_mode": draft.requested_mode,
        "effective_mode": draft.effective_mode,
        "provider_name": draft.provider_name,
        "draft_payload": draft.draft_payload,
        "warnings": draft.warnings,
        "save_status": draft.save_status,
        "target_asset_id": draft.target_asset_id,
        "target_menu_id": draft.target_menu_id,
        "target_route": target_route,
        "target_route_query": _build_target_route_query(
            draft.target_type,
            draft_id=draft.id,
            target_asset_id=draft.target_asset_id,
            target_menu_id=draft.target_menu_id,
        ),
        "source_testcase_id": draft.testcase_id,
        "testcase": _serialize_testcase(testcase),
        "create_time": draft.create_time,
        "update_time": draft.update_time,
    }


async def _get_testcase_or_raise(testcase_id: int, user_id: int) -> Testcase:
    testcase = await Testcase.filter(id=testcase_id, user_id=user_id).first()
    if not testcase:
        raise ValueError("测试用例不存在")
    return testcase


async def _get_draft_or_raise(draft_id: int, user_id: int) -> Automation_draft:
    draft = await Automation_draft.filter(id=draft_id, user_id=user_id).first()
    if not draft:
        raise ValueError("自动化草稿不存在")
    return draft


def _build_gateway_payload(testcase: Testcase, target_type: str, mode: str) -> Dict[str, Any]:
    return {
        "title": testcase.title,
        "module": testcase.module,
        "priority": testcase.priority,
        "category": testcase.category,
        "target_type": target_type,
        "mode": mode,
        "preconditions": testcase.preconditions,
        "steps": testcase.steps,
        "expected_results": testcase.expected_results,
    }


async def generate_automation_draft(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = _normalize_user_id(payload)
    testcase_id = int(payload.get("testcase_id") or 0)
    if testcase_id <= 0:
        raise ValueError("测试用例编号不能为空")

    target_type = _normalize_target_type(payload.get("target_type"))
    requested_mode = _normalize_string(payload.get("mode"))
    testcase = await _get_testcase_or_raise(testcase_id, user_id)
    if testcase.review_status != "approved":
        raise ValueError("只有已审核的测试用例才允许生成自动化草稿")

    gateway_payload = _build_gateway_payload(testcase, target_type, requested_mode)
    result = AIGatewayService().generate_automation_draft(gateway_payload)

    draft = await Automation_draft.create(
        testcase_id=testcase.id,
        requirement_id=testcase.requirement_id,
        target_type=target_type,
        requested_mode=result["configured_mode"],
        effective_mode=result["effective_mode"],
        provider_name=result["provider"]["provider_name"],
        draft_payload=result["draft_payload"],
        warnings=result.get("warnings") or [],
        save_status="draft",
        user_id=user_id,
    )
    data = _serialize_draft(draft, testcase)
    data["generation_source"] = result.get("generation_source", "rules")
    data["provider"] = result["provider"]
    data["configured_mode"] = result["configured_mode"]
    data["effective_mode"] = result["effective_mode"]
    return data


async def get_automation_draft_info(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = _normalize_user_id(payload)
    draft_id = int(payload.get("draft_id") or 0)
    if draft_id <= 0:
        raise ValueError("自动化草稿编号不能为空")

    draft = await _get_draft_or_raise(draft_id, user_id)
    testcase = await _get_testcase_or_raise(draft.testcase_id, user_id)
    return _serialize_draft(draft, testcase)


async def list_testcase_automation_drafts(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    user_id = _normalize_user_id(payload)
    testcase_id = int(payload.get("testcase_id") or 0)
    if testcase_id <= 0:
        raise ValueError("测试用例编号不能为空")

    testcase = await _get_testcase_or_raise(testcase_id, user_id)
    drafts = await Automation_draft.filter(
        testcase_id=testcase_id, user_id=user_id
    ).order_by("-id")
    return [_serialize_draft(item, testcase) for item in drafts]


def _validate_api_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    script = payload.get("script")
    if not isinstance(script, list) or not script:
        raise ValueError("API 草稿内容不能为空")
    return {
        "name": _normalize_string(payload.get("name")) or "未命名 API 草稿",
        "description": _normalize_string(payload.get("description")),
        "type": int(payload.get("type") or 1),
        "config": payload.get("config") if isinstance(payload.get("config"), dict) else {},
        "script": script,
    }


def _validate_web_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    script = payload.get("script")
    if not isinstance(script, list) or not script:
        raise ValueError("Web 草稿内容不能为空")
    return {
        "menu_name": _normalize_string(payload.get("menu_name")) or "未命名 Web 草稿",
        "script": script,
    }


def _validate_app_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    script = payload.get("script")
    if not isinstance(script, list) or not script:
        raise ValueError("App 草稿内容不能为空")
    return {
        "menu_name": _normalize_string(payload.get("menu_name")) or "未命名 App 草稿",
        "script": script,
    }


async def _build_unique_menu_name(model, base_name: str) -> str:
    if not await model.filter(name=base_name).exists():
        return base_name
    index = 2
    while await model.filter(name=f"{base_name}-{index}").exists():
        index += 1
    return f"{base_name}-{index}"


async def _ensure_root_menu(model, user_id: int, conn):
    root = await model.filter(name="AI生成草稿", type=1).first()
    if root:
        return root
    return await model.create(
        name="AI生成草稿", pid=0, type=1, user_id=user_id, using_db=conn
    )


async def _save_api_asset(
    payload: Dict[str, Any], user_id: int, testcase: Testcase, conn
) -> Dict[str, Any]:
    validated = _validate_api_payload(payload)
    asset = await Api_script.create(
        script=validated["script"],
        name=validated["name"],
        config=validated["config"],
        description=validated["description"] or f"来源测试用例：{testcase.title}",
        type=validated["type"],
        user_id=user_id,
        using_db=conn,
    )
    return {
        "target_asset_id": asset.id,
        "target_menu_id": None,
        "target_asset_name": asset.name,
        "target_route": _build_api_route(),
    }


async def _save_web_asset(
    payload: Dict[str, Any], user_id: int, testcase: Testcase, conn
) -> Dict[str, Any]:
    validated = _validate_web_payload(payload)
    root = await _ensure_root_menu(Web_menu, user_id, conn)
    menu_name = await _build_unique_menu_name(Web_menu, validated["menu_name"])
    menu = await Web_menu.create(
        name=menu_name,
        pid=root.id,
        type=2,
        user_id=user_id,
        using_db=conn,
    )
    asset = await Web_script.create(
        script=validated["script"],
        menu_id=menu.id,
        user_id=user_id,
        using_db=conn,
    )
    return {
        "target_asset_id": asset.id,
        "target_menu_id": menu.id,
        "target_asset_name": menu.name,
        "target_route": _build_web_route(),
    }


async def _save_app_asset(
    payload: Dict[str, Any], user_id: int, testcase: Testcase, conn
) -> Dict[str, Any]:
    validated = _validate_app_payload(payload)
    root = await _ensure_root_menu(App_menu, user_id, conn)
    menu_name = await _build_unique_menu_name(App_menu, validated["menu_name"])
    menu = await App_menu.create(
        name=menu_name,
        pid=root.id,
        type=2,
        user_id=user_id,
        using_db=conn,
    )
    asset = await App_script.create(
        script=validated["script"],
        menu_id=menu.id,
        user_id=user_id,
        using_db=conn,
    )
    return {
        "target_asset_id": asset.id,
        "target_menu_id": menu.id,
        "target_asset_name": menu.name,
        "target_route": _build_app_route(),
    }


async def save_automation_draft(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = _normalize_user_id(payload)
    draft_id = int(payload.get("draft_id") or 0)
    if draft_id <= 0:
        raise ValueError("自动化草稿编号不能为空")

    draft = await _get_draft_or_raise(draft_id, user_id)
    if draft.save_status not in VALID_AUTOMATION_SAVE_STATUS:
        raise ValueError("自动化草稿状态不正确")
    if draft.save_status == "saved" and draft.target_asset_id:
        raise ValueError("自动化草稿已保存到目标资产，请勿重复保存")

    edited_payload = _normalize_dict(payload.get("edited_payload"), "自动化草稿内容")
    testcase = await _get_testcase_or_raise(draft.testcase_id, user_id)
    async with in_transaction() as conn:
        if draft.target_type == "api":
            result = await _save_api_asset(edited_payload, user_id, testcase, conn)
        elif draft.target_type == "web":
            result = await _save_web_asset(edited_payload, user_id, testcase, conn)
        else:
            result = await _save_app_asset(edited_payload, user_id, testcase, conn)

        draft.draft_payload = edited_payload
        draft.save_status = "saved"
        draft.target_asset_id = result["target_asset_id"]
        draft.target_menu_id = result["target_menu_id"]
        await draft.save(
            using_db=conn,
            update_fields=[
                "draft_payload",
                "save_status",
                "target_asset_id",
                "target_menu_id",
            ],
        )

    result["draft_id"] = draft.id
    result["target_type"] = draft.target_type
    result["source_testcase_id"] = draft.testcase_id
    result["target_route_query"] = _build_target_route_query(
        draft.target_type,
        draft_id=draft.id,
        target_asset_id=result.get("target_asset_id"),
        target_menu_id=result.get("target_menu_id"),
    )
    return result
