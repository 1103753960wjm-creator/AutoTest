from typing import Any, Dict, List, Tuple

from tortoise.expressions import Q

from views.testcase.testcase_model import Testcase


VALID_REVIEW_STATUS = {"draft", "approved", "rejected"}


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


async def list_page_testcases(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = int(payload.get("user_id") or 0)
    if user_id <= 0:
        raise ValueError("缺少用户信息，无法查询测试用例")

    search, current_page, page_size = _normalize_page_payload(payload)
    keyword = _normalize_string(search.get("keyword"))
    review_status = _normalize_string(search.get("review_status"))
    target_type = _normalize_string(search.get("target_type"))
    requirement_id = int(search.get("requirement_id") or 0)

    query = Testcase.filter(user_id=user_id).prefetch_related("requirement")
    if keyword:
        query = query.filter(
            Q(title__icontains=keyword)
            | Q(module__icontains=keyword)
            | Q(category__icontains=keyword)
            | Q(requirement__title__icontains=keyword)
        )
    if requirement_id > 0:
        query = query.filter(requirement_id=requirement_id)
    if review_status:
        query = query.filter(review_status=review_status)
    if target_type:
        query = query.filter(target_type=target_type)

    total = await query.count()
    testcases = (
        await query.order_by("-id")
        .offset((current_page - 1) * page_size)
        .limit(page_size)
    )

    content = []
    for item in testcases:
        requirement = await item.requirement
        content.append(
            {
                "id": item.id,
                "requirement_id": item.requirement_id,
                "requirement_title": requirement.title if requirement else "",
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
                "update_time": item.update_time,
            }
        )

    return _build_page_response(content, current_page, page_size, total)


async def update_testcase_review_status(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = int(payload.get("user_id") or 0)
    if user_id <= 0:
        raise ValueError("缺少用户信息，无法更新测试用例审核状态")

    testcase_id = int(payload.get("testcase_id") or 0)
    if testcase_id <= 0:
        raise ValueError("测试用例编号不能为空")

    review_status = _normalize_review_status(payload.get("review_status"))
    testcase = await Testcase.filter(id=testcase_id, user_id=user_id).first()
    if not testcase:
        raise ValueError("测试用例不存在")

    testcase.review_status = review_status
    await testcase.save(update_fields=["review_status"])

    return {
        "id": testcase.id,
        "review_status": testcase.review_status,
        "title": testcase.title,
        "module": testcase.module,
        "category": testcase.category,
    }
