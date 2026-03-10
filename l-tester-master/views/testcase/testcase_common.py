from datetime import datetime, timezone
from html import escape
from typing import Any, Dict, List, Tuple

from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from views.automation_draft.automation_draft_model import Automation_draft
from views.testcase.testcase_model import (
    Testcase,
    Testcase_review_log,
    Testcase_revision,
    Testcase_tag,
    Testcase_tag_rel,
)


VALID_REVIEW_STATUS = {"draft", "approved", "rejected"}
VALID_PRIORITY = {"P0", "P1", "P2", "P3"}
VALID_TARGET_TYPES = {"general", "api", "web", "app"}
VALID_BATCH_ACTIONS = {
    "update_priority",
    "update_target_type",
    "update_module",
    "update_review_status",
    "add_tags",
    "remove_tags",
}
CATEGORY_LABEL_MAP = {
    "happy_path": "主流程",
    "negative_path": "异常流程",
    "required_field_validation": "必填项校验",
    "permission_or_visibility": "权限/可见性校验",
    "general": "通用",
}
TARGET_TYPE_LABEL_MAP = {
    "general": "通用",
    "api": "接口",
    "web": "Web",
    "app": "App",
}
REVIEW_STATUS_LABEL_MAP = {
    "draft": "草稿",
    "approved": "已审核",
    "rejected": "已拒绝",
}
REVIEW_REASON_TYPE_LABEL_MAP = {
    "design_complete": "设计完整",
    "scope_clear": "范围清晰",
    "ready_for_automation": "适合自动化",
    "missing_information": "信息缺失",
    "step_issue": "步骤不清",
    "expected_result_issue": "预期不准确",
    "duplicate_case": "重复用例",
    "other": "其他",
}
APPROVED_REVIEW_REASON_TYPES = {
    "design_complete",
    "scope_clear",
    "ready_for_automation",
    "other",
}
REJECTED_REVIEW_REASON_TYPES = {
    "missing_information",
    "step_issue",
    "expected_result_issue",
    "duplicate_case",
    "other",
}
DIFF_FIELD_LABEL_MAP = {
    "module": "所属模块",
    "title": "用例标题",
    "preconditions": "前置条件",
    "steps": "测试步骤",
    "expected_results": "预期结果",
    "priority": "优先级",
    "target_type": "目标类型",
    "automatable": "是否可自动化",
}


def _normalize_string(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text or default


def _normalize_positive_int(
    value: Any, default: int, *, minimum: int = 1, maximum: int = 50
) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError):
        return default
    result = max(minimum, result)
    result = min(maximum, result)
    return result


def _normalize_page_payload(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], int, int]:
    search = payload.get("search")
    if not isinstance(search, dict):
        search = {}
    current_page = _normalize_positive_int(
        payload.get("currentPage", payload.get("page_num")),
        1,
        maximum=100000,
    )
    page_size = _normalize_positive_int(
        payload.get("pageSize", payload.get("page_size")),
        10,
    )
    return search, current_page, page_size


def _build_page_response(
    content: List[Dict[str, Any]], current_page: int, page_size: int, total: int
) -> Dict[str, Any]:
    return {
        "content": content,
        "currentPage": current_page,
        "pageSize": page_size,
        "total": total,
        "page_num": current_page,
        "page_size": page_size,
    }


def _normalize_review_status(value: Any) -> str:
    review_status = _normalize_string(value).lower()
    if review_status not in VALID_REVIEW_STATUS:
        raise ValueError("审核状态仅支持 draft、approved、rejected")
    return review_status


def _normalize_priority(value: Any) -> str:
    priority = _normalize_string(value, "P2").upper()
    if priority not in VALID_PRIORITY:
        raise ValueError("优先级仅支持 P0、P1、P2、P3")
    return priority


def _normalize_target_type(value: Any) -> str:
    target_type = _normalize_string(value, "general").lower()
    if target_type not in VALID_TARGET_TYPES:
        raise ValueError("目标类型仅支持 general、api、web、app")
    return target_type


def _normalize_text_list(value: Any, field_name: str) -> List[str]:
    if isinstance(value, list):
        result = [str(item).strip() for item in value if str(item).strip()]
        if result:
            return result
    elif isinstance(value, str):
        result = [item.strip() for item in value.splitlines() if item.strip()]
        if result:
            return result
    raise ValueError(f"{field_name} 不能为空")


def _normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = _normalize_string(value).lower()
    if text in {"true", "1", "yes", "y", "是"}:
        return True
    if text in {"false", "0", "no", "n", "否"}:
        return False
    return bool(value)


def _normalize_user_id(payload: Dict[str, Any], message: str) -> int:
    user_id = int(payload.get("user_id") or 0)
    if user_id <= 0:
        raise ValueError(message)
    return user_id


def _normalize_testcase_id(payload: Dict[str, Any]) -> int:
    testcase_id = int(payload.get("testcase_id") or 0)
    if testcase_id <= 0:
        raise ValueError("测试用例编号不能为空")
    return testcase_id


def _normalize_batch_ids(value: Any) -> List[int]:
    if not isinstance(value, list) or not value:
        raise ValueError("批量操作至少需要一个测试用例编号")

    result: List[int] = []
    for item in value:
        testcase_id = int(item or 0)
        if testcase_id > 0 and testcase_id not in result:
            result.append(testcase_id)
    if not result:
        raise ValueError("批量操作至少需要一个有效测试用例编号")
    return result


def _build_category_label(category: str) -> str:
    return CATEGORY_LABEL_MAP.get(category, category or "通用")


def _build_target_type_label(target_type: str) -> str:
    return TARGET_TYPE_LABEL_MAP.get(target_type, target_type or "通用")


def _build_review_status_label(review_status: str) -> str:
    return REVIEW_STATUS_LABEL_MAP.get(review_status, review_status or "草稿")


def _build_review_reason_type_label(review_reason_type: str) -> str:
    return REVIEW_REASON_TYPE_LABEL_MAP.get(review_reason_type, review_reason_type or "")


def _normalize_review_reason_type(
    value: Any, *, review_status: str, required: bool = False
) -> str:
    review_reason_type = _normalize_string(value).lower()
    if not review_reason_type:
        if required and review_status == "rejected":
            raise ValueError("驳回测试用例时必须选择驳回原因类型")
        return ""
    if review_reason_type not in REVIEW_REASON_TYPE_LABEL_MAP:
        raise ValueError("审核原因类型不支持")
    if review_status == "approved" and review_reason_type not in APPROVED_REVIEW_REASON_TYPES:
        raise ValueError("审核通过仅支持通过类审核原因类型")
    if review_status == "rejected" and review_reason_type not in REJECTED_REVIEW_REASON_TYPES:
        raise ValueError("驳回仅支持驳回类审核原因类型")
    if review_status == "draft":
        raise ValueError("草稿状态不支持审核原因类型")
    return review_reason_type


def _normalize_datetime_for_compare(value: Any) -> Any:
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _empty_automation_summary() -> Dict[str, Any]:
    return {
        "latest_draft_count": 0,
        "latest_items": [],
    }


def _build_target_route(target_type: str) -> str:
    if target_type == "api":
        return "/_api_script"
    if target_type == "web":
        return "/web"
    if target_type == "app":
        return "/app_auto"
    return ""


def _join_text_lines(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join([str(item).strip() for item in value if str(item).strip()])
    return _normalize_string(value)


def _normalize_tag_names(value: Any) -> List[str]:
    if value is None:
        return []
    raw_items: List[Any]
    if isinstance(value, list):
        raw_items = value
    elif isinstance(value, str):
        raw_items = value.replace("，", ",").replace("\n", ",").split(",")
    else:
        raw_items = [value]

    result: List[str] = []
    for item in raw_items:
        text = _normalize_string(item)
        if not text:
            continue
        if len(text) > 32:
            raise ValueError("标签名称长度不能超过 32 个字符")
        if text not in result:
            result.append(text)
    return result


def _normalize_required_tag_names(value: Any, message: str) -> List[str]:
    tag_names = _normalize_tag_names(value)
    if not tag_names:
        raise ValueError(message)
    return tag_names


def _build_target_route_query(draft: Automation_draft) -> Dict[str, Any]:
    query: Dict[str, Any] = {
        "draft_id": draft.id,
        "source": "testcase_automation",
    }
    if draft.target_type == "api" and draft.target_asset_id:
        query["asset_id"] = draft.target_asset_id
    elif draft.target_type in {"web", "app"} and draft.target_menu_id:
        query["menu_id"] = draft.target_menu_id
    return query


def _serialize_automation_summary_item(draft: Automation_draft) -> Dict[str, Any]:
    return {
        "target_type": draft.target_type,
        "target_type_label": _build_target_type_label(draft.target_type),
        "draft_id": draft.id,
        "save_status": draft.save_status,
        "target_asset_id": draft.target_asset_id,
        "target_menu_id": draft.target_menu_id,
        "target_route": _build_target_route(draft.target_type),
        "target_route_query": _build_target_route_query(draft),
        "update_time": draft.update_time,
    }


async def _build_automation_summary_map(
    testcase_ids: List[int], user_id: int
) -> Dict[int, Dict[str, Any]]:
    if not testcase_ids:
        return {}

    drafts = await Automation_draft.filter(
        user_id=user_id, testcase_id__in=testcase_ids
    ).order_by("-id")

    summary_map: Dict[int, Dict[str, Dict[str, Any]]] = {}
    for draft in drafts:
        testcase_summary = summary_map.setdefault(draft.testcase_id, {})
        if draft.target_type in testcase_summary:
            continue
        testcase_summary[draft.target_type] = _serialize_automation_summary_item(draft)

    result: Dict[int, Dict[str, Any]] = {}
    for testcase_id, summary in summary_map.items():
        latest_items = list(summary.values())
        result[testcase_id] = {
            "latest_draft_count": len(latest_items),
            "latest_items": latest_items,
        }
    return result


async def _build_revision_count_map(testcase_ids: List[int]) -> Dict[int, int]:
    if not testcase_ids:
        return {}
    revisions = await Testcase_revision.filter(testcase_id__in=testcase_ids).all()
    result: Dict[int, int] = {}
    for item in revisions:
        result[item.testcase_id] = result.get(item.testcase_id, 0) + 1
    return result


async def _build_testcase_tag_map(testcase_ids: List[int]) -> Dict[int, List[Dict[str, Any]]]:
    if not testcase_ids:
        return {}
    rels = (
        await Testcase_tag_rel.filter(testcase_id__in=testcase_ids)
        .select_related("tag")
        .order_by("id")
    )
    result: Dict[int, List[Dict[str, Any]]] = {}
    for item in rels:
        tag = item.tag
        testcase_tags = result.setdefault(item.testcase_id, [])
        testcase_tags.append({"id": tag.id, "name": tag.name})
    return result


async def _list_testcase_tag_names(testcase_id: int) -> List[str]:
    tag_map = await _build_testcase_tag_map([testcase_id])
    return [item["name"] for item in tag_map.get(testcase_id, [])]


async def _sync_testcase_tags(
    testcase_id: int, user_id: int, tag_names: List[str], conn
) -> List[str]:
    normalized_tag_names = _normalize_tag_names(tag_names)
    tag_map: Dict[str, Testcase_tag] = {}
    if normalized_tag_names:
        existing_tags = await Testcase_tag.filter(
            user_id=user_id, name__in=normalized_tag_names
        ).using_db(conn)
        tag_map = {item.name: item for item in existing_tags}
        for tag_name in normalized_tag_names:
            if tag_name in tag_map:
                continue
            tag = await Testcase_tag.create(name=tag_name, user_id=user_id, using_db=conn)
            tag_map[tag_name] = tag

    target_tag_ids = [tag_map[name].id for name in normalized_tag_names if name in tag_map]
    rels = await Testcase_tag_rel.filter(testcase_id=testcase_id).using_db(conn)
    current_map = {item.tag_id: item for item in rels}
    current_ids = set(current_map.keys())
    target_ids = set(target_tag_ids)

    delete_rel_ids = [current_map[tag_id].id for tag_id in current_ids - target_ids]
    if delete_rel_ids:
        await Testcase_tag_rel.filter(id__in=delete_rel_ids).using_db(conn).delete()

    for tag_id in target_ids - current_ids:
        await Testcase_tag_rel.create(
            testcase_id=testcase_id,
            tag_id=tag_id,
            using_db=conn,
        )
    return normalized_tag_names


async def _serialize_testcase_snapshot(testcase: Testcase) -> Dict[str, Any]:
    tag_names = await _list_testcase_tag_names(testcase.id)
    return {
        "requirement_id": testcase.requirement_id,
        "generation_job_id": testcase.generation_job_id,
        "source_case_id": testcase.source_case_id,
        "title": testcase.title,
        "priority": testcase.priority,
        "module": testcase.module,
        "category": testcase.category,
        "preconditions": testcase.preconditions,
        "steps": testcase.steps,
        "expected_results": testcase.expected_results,
        "target_type": testcase.target_type,
        "automatable": testcase.automatable,
        "review_status": testcase.review_status,
        "latest_review_comment": testcase.latest_review_comment,
        "latest_review_reason_type": testcase.latest_review_reason_type,
        "latest_review_time": testcase.latest_review_time,
        "tag_names": tag_names,
        "version": testcase.version,
    }


async def _create_revision(
    testcase: Testcase, *, edit_reason: str, user_id: int, conn
) -> None:
    await Testcase_revision.create(
        testcase_id=testcase.id,
        version=testcase.version,
        snapshot=await _serialize_testcase_snapshot(testcase),
        edit_reason=edit_reason,
        user_id=user_id,
        using_db=conn,
    )


async def _create_review_log(
    testcase: Testcase,
    *,
    from_status: str,
    to_status: str,
    review_comment: str,
    review_reason_type: str,
    user_id: int,
    conn,
) -> None:
    await Testcase_review_log.create(
        testcase_id=testcase.id,
        from_status=from_status,
        to_status=to_status,
        review_comment=review_comment,
        review_reason_type=review_reason_type,
        user_id=user_id,
        using_db=conn,
    )


def _build_automation_risk(
    testcase: Testcase, automation_summary: Dict[str, Any]
) -> Dict[str, Any]:
    latest_items = automation_summary.get("latest_items") or []
    if not latest_items:
        return {"has_risk": False, "message": ""}

    latest_draft_time = None
    for item in latest_items:
        update_time = _normalize_datetime_for_compare(item.get("update_time"))
        if update_time and (latest_draft_time is None or update_time > latest_draft_time):
            latest_draft_time = update_time

    testcase_update_time = _normalize_datetime_for_compare(testcase.update_time)
    if latest_draft_time and testcase_update_time and testcase_update_time > latest_draft_time:
        return {
            "has_risk": True,
            "message": "测试用例已变更，已有自动化草稿可能过期",
        }
    return {"has_risk": False, "message": ""}


async def _get_testcase_or_raise(testcase_id: int, user_id: int) -> Testcase:
    testcase = await Testcase.filter(id=testcase_id, user_id=user_id).first()
    if not testcase:
        raise ValueError("测试用例不存在")
    return testcase


def _serialize_testcase_row(
    testcase: Testcase,
    requirement_title: str,
    revision_count: int,
    automation_summary: Dict[str, Any],
    tag_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "id": testcase.id,
        "requirement_id": testcase.requirement_id,
        "requirement_title": requirement_title,
        "source_case_id": testcase.source_case_id,
        "title": testcase.title,
        "priority": testcase.priority,
        "module": testcase.module,
        "category": testcase.category,
        "category_label": _build_category_label(testcase.category),
        "preconditions": testcase.preconditions,
        "preconditions_text": _join_text_lines(testcase.preconditions),
        "steps": testcase.steps,
        "steps_text": _join_text_lines(testcase.steps),
        "expected_results": testcase.expected_results,
        "expected_results_text": _join_text_lines(testcase.expected_results),
        "target_type": testcase.target_type,
        "target_type_label": _build_target_type_label(testcase.target_type),
        "automatable": testcase.automatable,
        "review_status": testcase.review_status,
        "review_status_label": _build_review_status_label(testcase.review_status),
        "latest_review_comment": testcase.latest_review_comment,
        "latest_review_reason_type": testcase.latest_review_reason_type,
        "latest_review_reason_type_label": _build_review_reason_type_label(
            testcase.latest_review_reason_type
        ),
        "latest_review_time": testcase.latest_review_time,
        "tags": tag_items,
        "tag_names": [item["name"] for item in tag_items],
        "version": testcase.version,
        "revision_count": revision_count,
        "history_available": revision_count > 0
        or bool(testcase.latest_review_comment),
        "automation_summary": automation_summary,
        "automation_risk": _build_automation_risk(testcase, automation_summary),
        "create_time": testcase.create_time,
        "update_time": testcase.update_time,
    }


async def list_page_testcases(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = _normalize_user_id(payload, "缺少用户信息，无法查询测试用例")

    search, current_page, page_size = _normalize_page_payload(payload)
    keyword = _normalize_string(search.get("keyword"))
    review_status = _normalize_string(search.get("review_status"))
    target_type = _normalize_string(search.get("target_type"))
    review_reason_type = _normalize_string(search.get("review_reason_type"))
    tag_names = _normalize_tag_names(search.get("tag_names"))
    requirement_id = int(search.get("requirement_id") or 0)

    query = Testcase.filter(user_id=user_id).prefetch_related("requirement")
    if keyword:
        query = query.filter(
            Q(title__icontains=keyword)
            | Q(module__icontains=keyword)
            | Q(category__icontains=keyword)
            | Q(requirement__title__icontains=keyword)
            | Q(latest_review_comment__icontains=keyword)
        )
    if requirement_id > 0:
        query = query.filter(requirement_id=requirement_id)
    if review_status:
        query = query.filter(review_status=review_status)
    if target_type:
        query = query.filter(target_type=target_type)
    if review_reason_type:
        query = query.filter(latest_review_reason_type=review_reason_type)
    if tag_names:
        tag_ids = await Testcase_tag.filter(
            user_id=user_id, name__in=tag_names
        ).values_list("id", flat=True)
        if not tag_ids:
            return _build_page_response([], current_page, page_size, 0)
        testcase_ids = list(
            set(
                await Testcase_tag_rel.filter(tag_id__in=list(tag_ids)).values_list(
                    "testcase_id", flat=True
                )
            )
        )
        if not testcase_ids:
            return _build_page_response([], current_page, page_size, 0)
        query = query.filter(id__in=testcase_ids)

    total = await query.count()
    testcases = (
        await query.order_by("-id")
        .offset((current_page - 1) * page_size)
        .limit(page_size)
    )
    testcase_ids = [item.id for item in testcases]
    automation_summary_map = await _build_automation_summary_map(testcase_ids, user_id)
    revision_count_map = await _build_revision_count_map(testcase_ids)
    tag_map = await _build_testcase_tag_map(testcase_ids)

    content = []
    for item in testcases:
        requirement = await item.requirement
        content.append(
            _serialize_testcase_row(
                item,
                requirement.title if requirement else "",
                revision_count_map.get(item.id, 0),
                automation_summary_map.get(item.id, _empty_automation_summary()),
                tag_map.get(item.id, []),
            )
        )

    return _build_page_response(content, current_page, page_size, total)


def _build_excel_cell(value: str) -> str:
    text = escape(value or "").replace("\n", "<br/>")
    return f"<td style=\"vertical-align: top; white-space: normal;\">{text}</td>"


def _build_excel_content(rows: List[Dict[str, Any]]) -> bytes:
    header_html = """
<tr>
  <th>序号</th>
  <th>所属模块</th>
  <th>用例标题</th>
  <th>前置条件</th>
  <th>测试步骤</th>
  <th>预期结果</th>
  <th>优先级</th>
</tr>
"""
    body_rows = []
    for index, row in enumerate(rows, start=1):
        body_rows.append(
            "<tr>"
            + _build_excel_cell(str(index))
            + _build_excel_cell(_normalize_string(row.get("module")))
            + _build_excel_cell(_normalize_string(row.get("title")))
            + _build_excel_cell(_join_text_lines(row.get("preconditions_text")))
            + _build_excel_cell(_join_text_lines(row.get("steps_text")))
            + _build_excel_cell(_join_text_lines(row.get("expected_results_text")))
            + _build_excel_cell(_normalize_string(row.get("priority")))
            + "</tr>"
        )

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #dcdfe6; padding: 8px; font-size: 12px; }}
    th {{ background: #f5f7fa; }}
  </style>
</head>
<body>
  <table>
    <thead>{header_html}</thead>
    <tbody>{''.join(body_rows)}</tbody>
  </table>
</body>
</html>"""
    return html.encode("utf-8")


async def export_testcases_excel(payload: Dict[str, Any]) -> Tuple[str, bytes]:
    user_id = _normalize_user_id(payload, "缺少用户信息，无法导出测试用例")
    search = payload.get("search")
    if not isinstance(search, dict):
        search = {}

    export_payload = {
        "user_id": user_id,
        "currentPage": 1,
        "pageSize": 5000,
        "search": search,
    }
    page_result = await list_page_testcases(export_payload)
    filename = f"测试用例_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.xls"
    return filename, _build_excel_content(page_result.get("content") or [])


def _normalize_edit_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    title = _normalize_string(payload.get("title"))
    module = _normalize_string(payload.get("module"))
    if not title:
        raise ValueError("用例标题不能为空")
    if not module:
        raise ValueError("所属模块不能为空")
    return {
        "title": title,
        "module": module,
        "priority": _normalize_priority(payload.get("priority")),
        "preconditions": _normalize_text_list(payload.get("preconditions"), "前置条件"),
        "steps": _normalize_text_list(payload.get("steps"), "测试步骤"),
        "expected_results": _normalize_text_list(
            payload.get("expected_results"), "预期结果"
        ),
        "target_type": _normalize_target_type(payload.get("target_type")),
        "automatable": _normalize_bool(payload.get("automatable")),
        "edit_reason": _normalize_string(payload.get("edit_reason"), "手工编辑"),
        "tag_names": (
            _normalize_tag_names(payload.get("tag_names"))
            if "tag_names" in payload
            else None
        ),
    }


async def edit_testcase_content(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = _normalize_user_id(payload, "缺少用户信息，无法编辑测试用例")
    testcase_id = _normalize_testcase_id(payload)
    testcase = await _get_testcase_or_raise(testcase_id, user_id)
    data = _normalize_edit_payload(payload)
    now = datetime.now(timezone.utc)

    async with in_transaction() as conn:
        await _create_revision(
            testcase,
            edit_reason=data["edit_reason"],
            user_id=user_id,
            conn=conn,
        )

        testcase.module = data["module"]
        testcase.title = data["title"]
        testcase.priority = data["priority"]
        testcase.preconditions = data["preconditions"]
        testcase.steps = data["steps"]
        testcase.expected_results = data["expected_results"]
        testcase.target_type = data["target_type"]
        testcase.automatable = data["automatable"]
        testcase.version = testcase.version + 1
        testcase.update_time = now
        await testcase.save(
            using_db=conn,
            update_fields=[
                "module",
                "title",
                "priority",
                "preconditions",
                "steps",
                "expected_results",
                "target_type",
                "automatable",
                "version",
                "update_time",
            ],
        )
        if data["tag_names"] is not None:
            await _sync_testcase_tags(testcase.id, user_id, data["tag_names"], conn)

    revision_count = await Testcase_revision.filter(testcase_id=testcase.id).count()
    automation_summary = (
        await _build_automation_summary_map([testcase.id], user_id)
    ).get(testcase.id, _empty_automation_summary())
    tag_items = (await _build_testcase_tag_map([testcase.id])).get(testcase.id, [])
    requirement = await testcase.requirement
    return _serialize_testcase_row(
        testcase,
        requirement.title if requirement else "",
        revision_count,
        automation_summary,
        tag_items,
    )


async def update_testcase_review_status(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = _normalize_user_id(payload, "缺少用户信息，无法更新测试用例审核状态")
    testcase_id = _normalize_testcase_id(payload)
    review_status = _normalize_review_status(payload.get("review_status"))
    review_comment = _normalize_string(payload.get("review_comment"))
    review_reason_type = _normalize_review_reason_type(
        payload.get("review_reason_type"),
        review_status=review_status,
        required=review_status == "rejected",
    )
    if review_status == "rejected" and not review_comment:
        raise ValueError("驳回测试用例时必须填写驳回原因")

    testcase = await _get_testcase_or_raise(testcase_id, user_id)
    from_status = testcase.review_status
    now = datetime.now(timezone.utc)

    async with in_transaction() as conn:
        testcase.review_status = review_status
        testcase.latest_review_comment = review_comment
        testcase.latest_review_reason_type = review_reason_type
        testcase.latest_review_time = now
        await testcase.save(
            using_db=conn,
            update_fields=[
                "review_status",
                "latest_review_comment",
                "latest_review_reason_type",
                "latest_review_time",
            ],
        )
        await _create_review_log(
            testcase,
            from_status=from_status,
            to_status=review_status,
            review_comment=review_comment,
            review_reason_type=review_reason_type,
            user_id=user_id,
            conn=conn,
        )

    return {
        "id": testcase.id,
        "review_status": testcase.review_status,
        "review_status_label": _build_review_status_label(testcase.review_status),
        "latest_review_comment": testcase.latest_review_comment,
        "latest_review_reason_type": testcase.latest_review_reason_type,
        "latest_review_reason_type_label": _build_review_reason_type_label(
            testcase.latest_review_reason_type
        ),
        "latest_review_time": testcase.latest_review_time,
        "title": testcase.title,
        "module": testcase.module,
        "category": testcase.category,
        "category_label": _build_category_label(testcase.category),
    }


async def _apply_batch_action(
    testcase: Testcase,
    *,
    action_type: str,
    action_payload: Dict[str, Any],
    user_id: int,
) -> None:
    now = datetime.now(timezone.utc)
    if action_type == "update_review_status":
        review_status = _normalize_review_status(action_payload.get("review_status"))
        review_comment = _normalize_string(action_payload.get("review_comment"))
        review_reason_type = _normalize_review_reason_type(
            action_payload.get("review_reason_type"),
            review_status=review_status,
            required=review_status == "rejected",
        )
        if review_status == "rejected" and not review_comment:
            raise ValueError("批量驳回时必须填写驳回原因")
        async with in_transaction() as conn:
            from_status = testcase.review_status
            testcase.review_status = review_status
            testcase.latest_review_comment = review_comment
            testcase.latest_review_reason_type = review_reason_type
            testcase.latest_review_time = now
            await testcase.save(
                using_db=conn,
                update_fields=[
                    "review_status",
                    "latest_review_comment",
                    "latest_review_reason_type",
                    "latest_review_time",
                ],
            )
            await _create_review_log(
                testcase,
                from_status=from_status,
                to_status=review_status,
                review_comment=review_comment,
                review_reason_type=review_reason_type,
                user_id=user_id,
                conn=conn,
            )
        return

    edit_reason = _normalize_string(action_payload.get("edit_reason"), "批量修改")
    async with in_transaction() as conn:
        await _create_revision(
            testcase,
            edit_reason=edit_reason,
            user_id=user_id,
            conn=conn,
        )
        if action_type == "update_priority":
            testcase.priority = _normalize_priority(action_payload.get("priority"))
            update_fields = ["priority"]
        elif action_type == "update_target_type":
            testcase.target_type = _normalize_target_type(action_payload.get("target_type"))
            update_fields = ["target_type"]
        elif action_type == "update_module":
            testcase.module = _normalize_string(action_payload.get("module"))
            if not testcase.module:
                raise ValueError("所属模块不能为空")
            update_fields = ["module"]
        elif action_type == "add_tags":
            current_tag_names = await _list_testcase_tag_names(testcase.id)
            incoming_tag_names = _normalize_required_tag_names(
                action_payload.get("tag_names"), "批量打标至少需要一个标签"
            )
            merged_tag_names = current_tag_names[:]
            for tag_name in incoming_tag_names:
                if tag_name not in merged_tag_names:
                    merged_tag_names.append(tag_name)
            await _sync_testcase_tags(testcase.id, user_id, merged_tag_names, conn)
            update_fields = []
        elif action_type == "remove_tags":
            current_tag_names = await _list_testcase_tag_names(testcase.id)
            removed_tag_names = set(
                _normalize_required_tag_names(
                    action_payload.get("tag_names"), "批量移除标签至少需要一个标签"
                )
            )
            remained_tag_names = [
                tag_name
                for tag_name in current_tag_names
                if tag_name not in removed_tag_names
            ]
            await _sync_testcase_tags(testcase.id, user_id, remained_tag_names, conn)
            update_fields = []
        else:
            raise ValueError("不支持的批量操作类型")

        testcase.version = testcase.version + 1
        testcase.update_time = now
        update_fields.extend(["version", "update_time"])
        await testcase.save(using_db=conn, update_fields=update_fields)


async def batch_update_testcases(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = _normalize_user_id(payload, "缺少用户信息，无法批量更新测试用例")
    testcase_ids = _normalize_batch_ids(payload.get("testcase_ids"))
    action_type = _normalize_string(payload.get("action_type"))
    if action_type not in VALID_BATCH_ACTIONS:
        raise ValueError("不支持的批量操作类型")
    action_payload = payload.get("action_payload")
    if not isinstance(action_payload, dict):
        action_payload = {}

    testcase_map = {
        item.id: item
        for item in await Testcase.filter(id__in=testcase_ids, user_id=user_id).all()
    }

    success_count = 0
    failed_items = []
    for testcase_id in testcase_ids:
        testcase = testcase_map.get(testcase_id)
        if not testcase:
            failed_items.append({"id": testcase_id, "message": "测试用例不存在"})
            continue
        try:
            await _apply_batch_action(
                testcase,
                action_type=action_type,
                action_payload=action_payload,
                user_id=user_id,
            )
            success_count += 1
        except ValueError as exc:
            failed_items.append({"id": testcase_id, "message": str(exc)})

    return {
        "success_count": success_count,
        "failed_count": len(failed_items),
        "failed_items": failed_items,
    }


def _serialize_revision(item: Testcase_revision) -> Dict[str, Any]:
    return {
        "id": item.id,
        "version": item.version,
        "snapshot": item.snapshot,
        "edit_reason": item.edit_reason,
        "create_time": item.create_time,
    }


def _serialize_review_log(item: Testcase_review_log) -> Dict[str, Any]:
    return {
        "id": item.id,
        "from_status": item.from_status,
        "from_status_label": _build_review_status_label(item.from_status),
        "to_status": item.to_status,
        "to_status_label": _build_review_status_label(item.to_status),
        "review_comment": item.review_comment,
        "review_reason_type": item.review_reason_type,
        "review_reason_type_label": _build_review_reason_type_label(
            item.review_reason_type
        ),
        "create_time": item.create_time,
    }


async def get_testcase_history(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = _normalize_user_id(payload, "缺少用户信息，无法查询测试用例历史")
    testcase_id = _normalize_testcase_id(payload)
    testcase = await _get_testcase_or_raise(testcase_id, user_id)
    revisions = await Testcase_revision.filter(testcase_id=testcase_id).order_by("-id")
    review_logs = await Testcase_review_log.filter(testcase_id=testcase_id).order_by("-id")

    requirement = await testcase.requirement
    automation_summary = (
        await _build_automation_summary_map([testcase.id], user_id)
    ).get(testcase.id, _empty_automation_summary())
    tag_items = (await _build_testcase_tag_map([testcase.id])).get(testcase.id, [])
    revision_count = len(revisions)

    return {
        "testcase": _serialize_testcase_row(
            testcase,
            requirement.title if requirement else "",
            revision_count,
            automation_summary,
            tag_items,
        ),
        "revisions": [_serialize_revision(item) for item in revisions],
        "review_logs": [_serialize_review_log(item) for item in review_logs],
    }


def _build_compare_value(field: str, value: Any) -> Any:
    if field in {"preconditions", "steps", "expected_results"}:
        return _join_text_lines(value)
    if field == "target_type":
        return _build_target_type_label(_normalize_string(value))
    if field == "automatable":
        return "是" if _normalize_bool(value) else "否"
    return value if value not in {None, ""} else ""


async def compare_testcase_revisions(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = _normalize_user_id(payload, "缺少用户信息，无法对比版本")
    testcase_id = _normalize_testcase_id(payload)
    base_revision_id = int(payload.get("base_revision_id") or 0)
    target_revision_id = int(payload.get("target_revision_id") or 0)
    if base_revision_id <= 0 or target_revision_id <= 0:
        raise ValueError("请选择两个有效版本进行对比")

    testcase = await _get_testcase_or_raise(testcase_id, user_id)
    revisions = await Testcase_revision.filter(
        testcase_id=testcase.id,
        id__in=[base_revision_id, target_revision_id],
    ).all()
    revision_map = {item.id: item for item in revisions}
    base_revision = revision_map.get(base_revision_id)
    target_revision = revision_map.get(target_revision_id)
    if not base_revision or not target_revision:
        raise ValueError("所选版本不存在")

    field_diffs = []
    for field, field_label in DIFF_FIELD_LABEL_MAP.items():
        before = _build_compare_value(field, base_revision.snapshot.get(field))
        after = _build_compare_value(field, target_revision.snapshot.get(field))
        field_diffs.append(
            {
                "field": field,
                "field_label": field_label,
                "before": before,
                "after": after,
                "changed": before != after,
            }
        )

    return {
        "testcase_id": testcase.id,
        "base_revision": _serialize_revision(base_revision),
        "target_revision": _serialize_revision(target_revision),
        "field_diffs": field_diffs,
    }


async def list_testcase_tags(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    user_id = _normalize_user_id(payload, "缺少用户信息，无法查询标签")
    keyword = _normalize_string(payload.get("keyword"))

    query = Testcase_tag.filter(user_id=user_id)
    if keyword:
        query = query.filter(name__icontains=keyword)
    tags = await query.order_by("name")
    tag_ids = [item.id for item in tags]
    rels = []
    if tag_ids:
        rels = await Testcase_tag_rel.filter(tag_id__in=tag_ids).all()
    count_map: Dict[int, int] = {}
    for item in rels:
        count_map[item.tag_id] = count_map.get(item.tag_id, 0) + 1
    return [
        {
            "id": item.id,
            "name": item.name,
            "use_count": count_map.get(item.id, 0),
        }
        for item in tags
    ]
