import copy
import re

from .models import TestCase


def extract_ai_generation_source(tags):
    if not isinstance(tags, list):
        return None

    for item in tags:
        if isinstance(item, dict) and item.get('source') == 'ai_generation_task':
            return item

    return None


def normalize_text_for_identity(value):
    if value is None:
        return ''
    return re.sub(r'\s+', ' ', str(value).replace('\r\n', '\n').replace('\r', '\n')).strip()


def _to_int(value):
    if value in (None, ''):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def build_ai_result_identity(payload_or_result):
    payload = payload_or_result or {}
    ai_source = extract_ai_generation_source(payload.get('tags')) or {}

    title = payload.get('title') or payload.get('scenario') or payload.get('description') or ''
    preconditions = payload.get('preconditions') or payload.get('precondition') or ''
    steps = payload.get('steps') or payload.get('test_steps') or ''
    expected_result = payload.get('expected_result') or payload.get('expected') or ''

    return {
        'task_id': str(ai_source.get('task_id') or payload.get('task_id') or '').strip(),
        'case_id': str(ai_source.get('case_id') or payload.get('case_id') or payload.get('caseId') or '').strip(),
        'case_index': _to_int(ai_source.get('case_index') or payload.get('case_index') or payload.get('index')),
        'title': normalize_text_for_identity(title),
        'preconditions': normalize_text_for_identity(preconditions),
        'steps': normalize_text_for_identity(steps),
        'expected_result': normalize_text_for_identity(expected_result),
        'test_type': str(payload.get('test_type') or 'functional').strip() or 'functional',
    }


def merge_ai_generation_source_tags(tags, identity, project=None, source_label=''):
    normalized_tags = []
    if isinstance(tags, list):
        normalized_tags = [copy.deepcopy(tag) for tag in tags if not (isinstance(tag, dict) and tag.get('source') == 'ai_generation_task')]

    normalized_tags.append({
        'source': 'ai_generation_task',
        'task_id': identity.get('task_id') or '',
        'project_id': getattr(project, 'id', None),
        'project_name': getattr(project, 'name', '') or '',
        'case_id': identity.get('case_id') or '',
        'case_index': identity.get('case_index'),
        'source_label': source_label or '由 AI 生成链导入',
    })
    return normalized_tags


def _is_same_content(identity, testcase):
    return (
        identity.get('title') == normalize_text_for_identity(testcase.title)
        and identity.get('preconditions') == normalize_text_for_identity(testcase.preconditions)
        and identity.get('steps') == normalize_text_for_identity(testcase.steps)
        and identity.get('expected_result') == normalize_text_for_identity(testcase.expected_result)
    )


def find_existing_ai_testcase(project, identity):
    task_id = identity.get('task_id')
    if not project or not task_id:
        return None

    queryset = TestCase.objects.filter(project=project).order_by('created_at', 'id')

    fallback_only = not identity.get('case_id') and identity.get('case_index') is None and identity.get('title')
    if fallback_only:
        queryset = queryset.filter(title=identity.get('title'))

    matched_by_case_id = []
    matched_by_case_index = []
    matched_by_content = []

    for testcase in queryset:
        ai_source = extract_ai_generation_source(getattr(testcase, 'tags', []))
        if not ai_source:
            continue
        if str(ai_source.get('task_id') or '').strip() != task_id:
            continue

        if identity.get('case_id') and str(ai_source.get('case_id') or '').strip() == identity.get('case_id'):
            matched_by_case_id.append(testcase)
            continue

        if identity.get('case_index') is not None and _to_int(ai_source.get('case_index')) == identity.get('case_index'):
            matched_by_case_index.append(testcase)
            continue

        if _is_same_content(identity, testcase):
            matched_by_content.append(testcase)

    if matched_by_case_id:
        return matched_by_case_id[0]
    if matched_by_case_index:
        return matched_by_case_index[0]
    if matched_by_content:
        return matched_by_content[0]
    return None


def get_or_create_ai_testcase(*, project, testcase_payload, create_callback, apply_default_versions=None):
    payload = copy.deepcopy(testcase_payload or {})
    identity = build_ai_result_identity(payload)

    payload['tags'] = merge_ai_generation_source_tags(
        payload.get('tags'),
        identity,
        project=project,
        source_label=(extract_ai_generation_source(payload.get('tags')) or {}).get('source_label') or '',
    )
    identity = build_ai_result_identity(payload)

    testcase = find_existing_ai_testcase(project, identity)
    if testcase:
        if apply_default_versions and not testcase.versions.exists():
            apply_default_versions(testcase, project)
        return testcase, False, payload, identity

    testcase = create_callback(payload)
    if apply_default_versions:
        apply_default_versions(testcase, project)
    return testcase, True, payload, identity
