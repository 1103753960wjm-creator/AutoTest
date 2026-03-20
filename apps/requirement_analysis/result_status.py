import copy

from django.utils import timezone

from apps.testcases.ai_source_dedup import build_ai_result_identity, find_existing_ai_testcase

from .result_parser import parse_generated_results


RESULT_STATUS_PENDING = "pending"
RESULT_STATUS_ADOPTED = "adopted"
RESULT_STATUS_DISCARDED = "discarded"
VALID_RESULT_STATUSES = {
    RESULT_STATUS_PENDING,
    RESULT_STATUS_ADOPTED,
    RESULT_STATUS_DISCARDED,
}


def _to_int(value):
    if value in (None, ""):
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _now_iso():
    return timezone.now().isoformat()


def build_result_key(case_id="", case_index=None):
    case_id = str(case_id or "").strip()
    if case_id:
        return f"case:{case_id}"

    normalized_index = _to_int(case_index)
    if normalized_index is None:
        return "index:unknown"
    return f"index:{normalized_index}"


def build_default_result_status_snapshot(task, parsed_results=None):
    parsed_results = parsed_results if parsed_results is not None else parse_generated_results(
        task.final_test_cases or task.generated_test_cases
    )
    items = []
    now_iso = _now_iso()

    for fallback_index, result in enumerate(parsed_results, start=1):
        case_index = _to_int(result.get("index")) or fallback_index
        case_id = str(result.get("case_id") or result.get("caseId") or "").strip()
        items.append(
            {
                "result_key": build_result_key(case_id, case_index),
                "case_id": case_id,
                "case_index": case_index,
                "status": RESULT_STATUS_PENDING,
                "adopted_testcase_id": None,
                "updated_at": now_iso,
            }
        )

    return {
        "version": 1,
        "total_count": len(items),
        "items": items,
    }


def _normalize_snapshot_item(existing_item, result, fallback_index):
    case_index = _to_int(result.get("index")) or fallback_index
    case_id = str(result.get("case_id") or result.get("caseId") or "").strip()
    result_key = build_result_key(case_id, case_index)
    updated_at = _now_iso()

    status = RESULT_STATUS_PENDING
    adopted_testcase_id = None
    if isinstance(existing_item, dict):
        existing_status = existing_item.get("status")
        if existing_status in VALID_RESULT_STATUSES:
            status = existing_status
        if status == RESULT_STATUS_ADOPTED:
            adopted_testcase_id = _to_int(existing_item.get("adopted_testcase_id"))
        updated_at = existing_item.get("updated_at") or updated_at

    if status != RESULT_STATUS_ADOPTED:
        adopted_testcase_id = None

    return {
        "result_key": result_key,
        "case_id": case_id,
        "case_index": case_index,
        "status": status,
        "adopted_testcase_id": adopted_testcase_id,
        "updated_at": updated_at,
    }


def _snapshot_changed(previous_snapshot, snapshot):
    return (previous_snapshot or {}) != snapshot


def _build_snapshot_lookup(snapshot):
    lookup = {}
    for item in snapshot.get("items", []):
        if not isinstance(item, dict):
            continue
        result_key = item.get("result_key")
        if result_key:
            lookup[result_key] = item

        case_id = str(item.get("case_id") or "").strip()
        case_index = _to_int(item.get("case_index"))
        if case_id:
            lookup[f"case:{case_id}"] = item
        if case_index is not None:
            lookup[f"index:{case_index}"] = item
    return lookup


def _apply_task_saved_state(task, summary):
    should_save = summary["total_count"] > 0 and summary["adopted_count"] == summary["total_count"]
    changed_fields = []

    if task.is_saved_to_records != should_save:
        task.is_saved_to_records = should_save
        changed_fields.append("is_saved_to_records")

    if should_save:
        if not task.saved_at:
            task.saved_at = timezone.now()
            changed_fields.append("saved_at")
    elif task.saved_at is not None:
        task.saved_at = None
        changed_fields.append("saved_at")

    return changed_fields


def ensure_result_status_snapshot(task, parsed_results=None, save=False):
    parsed_results = parsed_results if parsed_results is not None else parse_generated_results(
        task.final_test_cases or task.generated_test_cases
    )
    previous_snapshot = copy.deepcopy(task.result_status_snapshot or {})
    snapshot_items = previous_snapshot.get("items") if isinstance(previous_snapshot, dict) else None

    if not isinstance(snapshot_items, list):
        snapshot = build_default_result_status_snapshot(task, parsed_results)
    else:
        snapshot_lookup = _build_snapshot_lookup(previous_snapshot)
        items = []
        for fallback_index, result in enumerate(parsed_results, start=1):
            case_index = _to_int(result.get("index")) or fallback_index
            case_id = str(result.get("case_id") or result.get("caseId") or "").strip()
            existing_item = snapshot_lookup.get(build_result_key(case_id, case_index))
            if existing_item is None and case_id:
                existing_item = snapshot_lookup.get(f"case:{case_id}")
            if existing_item is None:
                existing_item = snapshot_lookup.get(f"index:{case_index}")
            items.append(_normalize_snapshot_item(existing_item, result, fallback_index))
        snapshot = {
            "version": 1,
            "total_count": len(items),
            "items": items,
        }

    task.result_status_snapshot = snapshot
    summary = get_result_status_summary(task, parsed_results=parsed_results, snapshot=snapshot)
    changed_fields = []
    if _snapshot_changed(previous_snapshot, snapshot):
        changed_fields.append("result_status_snapshot")
    changed_fields.extend(_apply_task_saved_state(task, summary))

    if save and changed_fields:
        task.save(update_fields=list(dict.fromkeys(changed_fields + ["updated_at"])))

    return snapshot


def get_result_status_summary(task, parsed_results=None, snapshot=None):
    parsed_results = parsed_results if parsed_results is not None else parse_generated_results(
        task.final_test_cases or task.generated_test_cases
    )
    snapshot = snapshot if snapshot is not None else ensure_result_status_snapshot(
        task,
        parsed_results=parsed_results,
        save=False,
    )
    items = snapshot.get("items", []) if isinstance(snapshot, dict) else []

    total_count = len(parsed_results)
    adopted_count = 0
    discarded_count = 0

    for item in items:
        status = item.get("status")
        if status == RESULT_STATUS_ADOPTED:
            adopted_count += 1
        elif status == RESULT_STATUS_DISCARDED:
            discarded_count += 1

    pending_count = max(total_count - adopted_count - discarded_count, 0)
    handled_count = adopted_count + discarded_count

    if total_count == 0 or pending_count == total_count:
        status = "pending"
        label = "尚未处理"
    elif adopted_count == total_count:
        status = "saved"
        label = "已保存为正式测试用例"
    elif pending_count == 0 and discarded_count > 0:
        status = "handled"
        label = "已处理完成"
    else:
        status = "partial"
        label = f"处理中（已处理 {handled_count}/{total_count}）"

    return {
        "status": status,
        "label": label,
        "detail": f"采纳 {adopted_count}，弃用 {discarded_count}，未标记 {pending_count}",
        "total_count": total_count,
        "handled_count": handled_count,
        "adopted_count": adopted_count,
        "discarded_count": discarded_count,
        "pending_count": pending_count,
    }


def _build_ai_identity(task, result, fallback_index):
    case_index = _to_int(result.get("index")) or fallback_index
    case_id = str(result.get("case_id") or result.get("caseId") or "").strip()
    return build_ai_result_identity(
        {
            "task_id": task.task_id,
            "case_id": case_id,
            "case_index": case_index,
            "title": result.get("scenario") or "",
            "preconditions": result.get("precondition") or "",
            "steps": result.get("steps") or "",
            "expected_result": result.get("expected") or "",
            "test_type": "functional",
            "tags": [
                {
                    "source": "ai_generation_task",
                    "task_id": task.task_id,
                    "case_id": case_id,
                    "case_index": case_index,
                }
            ],
        }
    )


def sync_result_status_from_existing_adoptions(task, project=None, parsed_results=None, save=False):
    parsed_results = parsed_results if parsed_results is not None else parse_generated_results(
        task.final_test_cases or task.generated_test_cases
    )
    previous_snapshot = copy.deepcopy(task.result_status_snapshot or {})
    snapshot = copy.deepcopy(ensure_result_status_snapshot(task, parsed_results=parsed_results, save=False))
    lookup = _build_snapshot_lookup(snapshot)
    target_project = project or task.project
    changed = False
    now_iso = _now_iso()

    for fallback_index, result in enumerate(parsed_results, start=1):
        case_index = _to_int(result.get("index")) or fallback_index
        case_id = str(result.get("case_id") or result.get("caseId") or "").strip()
        item = lookup.get(build_result_key(case_id, case_index))
        if not item or item.get("status") == RESULT_STATUS_DISCARDED:
            continue
        if item.get("status") == RESULT_STATUS_ADOPTED and item.get("adopted_testcase_id"):
            continue

        testcase = None
        if target_project:
            testcase = find_existing_ai_testcase(target_project, _build_ai_identity(task, result, fallback_index))

        if testcase:
            item["status"] = RESULT_STATUS_ADOPTED
            item["adopted_testcase_id"] = testcase.id
            item["updated_at"] = now_iso
            changed = True
        elif task.is_saved_to_records and item.get("status") == RESULT_STATUS_PENDING:
            item["status"] = RESULT_STATUS_ADOPTED
            item["updated_at"] = now_iso
            changed = True

    task.result_status_snapshot = snapshot
    summary = get_result_status_summary(task, parsed_results=parsed_results, snapshot=snapshot)
    changed_fields = []
    if changed or _snapshot_changed(previous_snapshot, snapshot):
        changed_fields.append("result_status_snapshot")
    changed_fields.extend(_apply_task_saved_state(task, summary))

    if save and changed_fields:
        task.save(update_fields=list(dict.fromkeys(changed_fields + ["updated_at"])))

    return snapshot


def mark_result_status(task, case_id="", case_index=None, status=RESULT_STATUS_PENDING, adopted_testcase_id=None, parsed_results=None, save=True):
    if status not in VALID_RESULT_STATUSES:
        raise ValueError(f"不支持的结果状态: {status}")

    parsed_results = parsed_results if parsed_results is not None else parse_generated_results(
        task.final_test_cases or task.generated_test_cases
    )
    snapshot = copy.deepcopy(ensure_result_status_snapshot(task, parsed_results=parsed_results, save=False))
    lookup = _build_snapshot_lookup(snapshot)
    normalized_index = _to_int(case_index)
    item = lookup.get(build_result_key(case_id, normalized_index))

    if item is None and normalized_index is not None and normalized_index >= 0:
        item = lookup.get(build_result_key(case_id, normalized_index + 1))

    if item is None:
        return snapshot, get_result_status_summary(task, parsed_results=parsed_results, snapshot=snapshot)

    item["status"] = status
    item["adopted_testcase_id"] = _to_int(adopted_testcase_id) if status == RESULT_STATUS_ADOPTED else None
    item["updated_at"] = _now_iso()

    task.result_status_snapshot = snapshot
    summary = get_result_status_summary(task, parsed_results=parsed_results, snapshot=snapshot)
    changed_fields = ["result_status_snapshot"]
    changed_fields.extend(_apply_task_saved_state(task, summary))

    if save:
        task.save(update_fields=list(dict.fromkeys(changed_fields + ["updated_at"])))

    return snapshot, summary


def attach_result_status(task, results, project=None, save=False):
    parsed_results = results if results is not None else parse_generated_results(
        task.final_test_cases or task.generated_test_cases
    )
    snapshot = sync_result_status_from_existing_adoptions(
        task,
        project=project,
        parsed_results=parsed_results,
        save=save,
    )
    lookup = _build_snapshot_lookup(snapshot)
    enriched_results = []

    for fallback_index, result in enumerate(parsed_results, start=1):
        case_index = _to_int(result.get("index")) or fallback_index
        case_id = str(result.get("case_id") or result.get("caseId") or "").strip()
        item = lookup.get(build_result_key(case_id, case_index)) or {}
        result_status = item.get("status") or RESULT_STATUS_PENDING
        adopted_testcase_id = _to_int(item.get("adopted_testcase_id"))

        if result_status == RESULT_STATUS_ADOPTED:
            status_label = "已采纳"
        elif result_status == RESULT_STATUS_DISCARDED:
            status_label = "已弃用"
        else:
            status_label = "待处理"

        enriched_results.append(
            {
                **result,
                "index": case_index,
                "result_status": result_status,
                "result_status_label": status_label,
                "is_adopted": result_status == RESULT_STATUS_ADOPTED,
                "adopted_testcase_id": adopted_testcase_id,
                "display_status": result_status,
                "display_status_label": status_label,
            }
        )

    return enriched_results, get_result_status_summary(task, parsed_results=parsed_results, snapshot=snapshot)


__all__ = [
    "RESULT_STATUS_PENDING",
    "RESULT_STATUS_ADOPTED",
    "RESULT_STATUS_DISCARDED",
    "attach_result_status",
    "build_default_result_status_snapshot",
    "build_result_key",
    "ensure_result_status_snapshot",
    "get_result_status_summary",
    "mark_result_status",
    "sync_result_status_from_existing_adoptions",
]
