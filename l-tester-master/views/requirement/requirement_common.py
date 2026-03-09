from typing import Any, Dict, List, Tuple

from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from views.requirement.requirement_model import Requirement, Testcase_generation_job
from views.testcase.testcase_model import Testcase


VALID_PRIORITY_VALUES = {"P0", "P1", "P2", "P3"}


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


def _normalize_text_list(value: Any, field_name: str) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.splitlines() if item.strip()]
    raise ValueError(f"{field_name} 格式不正确")


def _normalize_priority(value: Any) -> str:
    priority = _normalize_string(value, "P2").upper()
    if priority not in VALID_PRIORITY_VALUES:
        raise ValueError("优先级仅支持 P0、P1、P2、P3")
    return priority


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


def _case_is_reviewed(item: Dict[str, Any]) -> bool:
    if item.get("reviewed") is True:
        return True
    review_status = str(item.get("review_status") or "").strip().lower()
    return review_status in {"approved", "reviewed"}


async def _build_requirement_latest_job_map(
    requirement_ids: List[int], user_id: int
) -> Dict[int, Testcase_generation_job]:
    if not requirement_ids:
        return {}
    jobs = (
        await Testcase_generation_job.filter(
            requirement_id__in=requirement_ids, user_id=user_id
        )
        .order_by("-id")
        .all()
    )
    job_map: Dict[int, Testcase_generation_job] = {}
    for item in jobs:
        if item.requirement_id not in job_map:
            job_map[item.requirement_id] = item
    return job_map


async def _build_requirement_testcase_count_map(
    requirement_ids: List[int], user_id: int
) -> Dict[int, int]:
    if not requirement_ids:
        return {}
    rows = await Testcase.filter(
        requirement_id__in=requirement_ids, user_id=user_id
    ).values("requirement_id")
    count_map: Dict[int, int] = {}
    for item in rows:
        requirement_id = item["requirement_id"]
        count_map[requirement_id] = count_map.get(requirement_id, 0) + 1
    return count_map


def normalize_reviewed_cases_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = int(payload.get("user_id") or 0)
    if user_id <= 0:
        raise ValueError("缺少用户信息，无法保存")

    title = _normalize_string(payload.get("title"))
    if not title:
        raise ValueError("需求标题不能为空")

    source_content = _normalize_string(
        payload.get("content") or payload.get("source_content")
    )
    if not source_content:
        raise ValueError("需求内容不能为空")

    source_type = _normalize_string(payload.get("source_type"), "feature_design")
    default_module = _normalize_string(payload.get("module"), title)
    summary = payload.get("summary") or []
    if not isinstance(summary, list):
        summary = []
    summary = [str(item).strip() for item in summary if str(item).strip()]

    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("待保存的测试用例不能为空")

    reviewed_cases = []
    for item in raw_cases:
        if not isinstance(item, dict) or not _case_is_reviewed(item):
            continue
        case_title = _normalize_string(item.get("title"))
        if not case_title:
            raise ValueError("已审核测试用例缺少标题")
        case_module = _normalize_string(item.get("module"), default_module)
        if not case_module:
            raise ValueError("已审核测试用例缺少所属模块")
        reviewed_cases.append(
            {
                "source_case_id": _normalize_string(item.get("case_id")) or None,
                "title": case_title,
                "priority": _normalize_priority(item.get("priority")),
                "module": case_module,
                "category": _normalize_string(item.get("category"), "general"),
                "preconditions": _normalize_text_list(
                    item.get("preconditions") or [], "前置条件"
                ),
                "steps": _normalize_text_list(item.get("steps") or [], "测试步骤"),
                "expected_results": _normalize_text_list(
                    item.get("expected_results") or [], "预期结果"
                ),
                "target_type": _normalize_string(item.get("target_type"), "general"),
                "automatable": bool(item.get("automatable")),
                "review_status": "approved",
            }
        )

    if not reviewed_cases:
        raise ValueError("至少需要一个已审核的测试用例")

    requested_mode = _normalize_string(
        payload.get("configured_mode") or payload.get("requested_mode"), "none"
    )
    effective_mode = _normalize_string(payload.get("effective_mode"), requested_mode)
    provider_name = _normalize_string(
        payload.get("provider_name")
        or (payload.get("provider") or {}).get("provider_name"),
        "template_rules",
    )

    return {
        "user_id": user_id,
        "title": title,
        "source_type": source_type,
        "source_content": source_content,
        "summary": summary,
        "requested_mode": requested_mode,
        "effective_mode": effective_mode,
        "provider_name": provider_name,
        "prompt_version": _normalize_string(
            payload.get("prompt_version"), "m2-phase1"
        ),
        "cases": reviewed_cases,
    }


async def save_reviewed_cases(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = normalize_reviewed_cases_payload(payload)
    async with in_transaction() as conn:
        requirement = await Requirement.create(
            title=data["title"],
            source_type=data["source_type"],
            source_content=data["source_content"],
            parsed_content=data["summary"],
            status="reviewed",
            version=1,
            user_id=data["user_id"],
            using_db=conn,
        )
        generation_job = await Testcase_generation_job.create(
            requirement_id=requirement.id,
            source_type=data["source_type"],
            source_id=requirement.id,
            requested_mode=data["requested_mode"],
            effective_mode=data["effective_mode"],
            provider_name=data["provider_name"],
            prompt_version=data["prompt_version"],
            job_status="saved",
            summary=data["summary"],
            error_message="",
            user_id=data["user_id"],
            using_db=conn,
        )

        saved_cases = []
        for item in data["cases"]:
            testcase = await Testcase.create(
                requirement_id=requirement.id,
                generation_job_id=generation_job.id,
                source_case_id=item["source_case_id"],
                title=item["title"],
                priority=item["priority"],
                module=item["module"],
                category=item["category"],
                preconditions=item["preconditions"],
                steps=item["steps"],
                expected_results=item["expected_results"],
                target_type=item["target_type"],
                automatable=item["automatable"],
                review_status=item["review_status"],
                version=1,
                user_id=data["user_id"],
                using_db=conn,
            )
            saved_cases.append(
                {
                    "id": testcase.id,
                    "title": testcase.title,
                    "module": testcase.module,
                    "review_status": testcase.review_status,
                }
            )

    return {
        "requirement": {
            "id": requirement.id,
            "title": requirement.title,
            "source_type": requirement.source_type,
            "status": requirement.status,
            "version": requirement.version,
            "create_time": requirement.create_time,
        },
        "generation_job": {
            "id": generation_job.id,
            "requested_mode": generation_job.requested_mode,
            "effective_mode": generation_job.effective_mode,
            "provider_name": generation_job.provider_name,
            "job_status": generation_job.job_status,
        },
        "testcase_count": len(saved_cases),
        "testcases": saved_cases,
    }


async def list_recent_requirements(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    if user_id <= 0:
        raise ValueError("缺少用户信息，无法查询需求资产")

    limit = max(1, min(int(limit or 10), 50))
    requirements = await Requirement.filter(user_id=user_id).order_by("-id").limit(limit)

    result = []
    for item in requirements:
        testcase_count = await Testcase.filter(
            requirement_id=item.id, user_id=user_id
        ).count()
        latest_job = (
            await Testcase_generation_job.filter(requirement_id=item.id, user_id=user_id)
            .order_by("-id")
            .first()
        )
        result.append(
            {
                "id": item.id,
                "title": item.title,
                "source_type": item.source_type,
                "status": item.status,
                "version": item.version,
                "parsed_content": item.parsed_content,
                "create_time": item.create_time,
                "testcase_count": testcase_count,
                "effective_mode": latest_job.effective_mode if latest_job else "none",
                "provider_name": latest_job.provider_name if latest_job else "",
            }
        )
    return result


async def list_page_requirements(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = int(payload.get("user_id") or 0)
    if user_id <= 0:
        raise ValueError("缺少用户信息，无法查询需求资产")

    search, current_page, page_size = _normalize_page_payload(payload)
    keyword = _normalize_string(search.get("keyword"))
    source_type = _normalize_string(search.get("source_type"))
    status = _normalize_string(search.get("status"))

    query = Requirement.filter(user_id=user_id)
    if keyword:
        query = query.filter(
            Q(title__icontains=keyword) | Q(source_content__icontains=keyword)
        )
    if source_type:
        query = query.filter(source_type=source_type)
    if status:
        query = query.filter(status=status)

    total = await query.count()
    requirements = (
        await query.order_by("-id")
        .offset((current_page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    requirement_ids = [item.id for item in requirements]
    count_map = await _build_requirement_testcase_count_map(requirement_ids, user_id)
    latest_job_map = await _build_requirement_latest_job_map(requirement_ids, user_id)

    content = []
    for item in requirements:
        latest_job = latest_job_map.get(item.id)
        content.append(
            {
                "id": item.id,
                "title": item.title,
                "source_type": item.source_type,
                "status": item.status,
                "version": item.version,
                "parsed_content": item.parsed_content,
                "create_time": item.create_time,
                "testcase_count": count_map.get(item.id, 0),
                "effective_mode": latest_job.effective_mode if latest_job else "none",
                "provider_name": latest_job.provider_name if latest_job else "",
            }
        )
    return _build_page_response(content, current_page, page_size, total)


async def list_requirement_testcases(
    requirement_id: int, user_id: int
) -> Dict[str, Any]:
    if user_id <= 0:
        raise ValueError("缺少用户信息，无法查询测试用例")

    requirement = await Requirement.filter(id=requirement_id, user_id=user_id).first()
    if not requirement:
        raise ValueError("需求资产不存在")

    testcases = await Testcase.filter(
        requirement_id=requirement_id, user_id=user_id
    ).order_by("id")

    return {
        "requirement": {
            "id": requirement.id,
            "title": requirement.title,
            "source_type": requirement.source_type,
            "status": requirement.status,
            "version": requirement.version,
            "create_time": requirement.create_time,
        },
        "testcases": [
            {
                "id": item.id,
                "source_case_id": item.source_case_id,
                "title": item.title,
                "priority": item.priority,
                "module": item.module,
                "category": item.category,
                "preconditions": item.preconditions,
                "steps": item.steps,
                "expected_results": item.expected_results,
                "target_type": item.target_type,
                "automatable": item.automatable,
                "review_status": item.review_status,
                "version": item.version,
                "create_time": item.create_time,
            }
            for item in testcases
        ],
    }
