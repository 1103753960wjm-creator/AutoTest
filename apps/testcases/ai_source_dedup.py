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


def _build_identity_content_key(identity):
    return (
        normalize_text_for_identity(identity.get('title')),
        normalize_text_for_identity(identity.get('preconditions')),
        normalize_text_for_identity(identity.get('steps')),
        normalize_text_for_identity(identity.get('expected_result')),
    )


def _build_testcase_identity(testcase):
    return build_ai_result_identity(
        {
            'title': testcase.title,
            'preconditions': testcase.preconditions,
            'steps': testcase.steps,
            'expected_result': testcase.expected_result,
            'test_type': testcase.test_type,
            'tags': getattr(testcase, 'tags', []),
        }
    )


def register_ai_testcase_lookup(testcase_lookup, testcase, identity=None):
    if not isinstance(testcase_lookup, dict):
        return testcase_lookup

    normalized_identity = identity or _build_testcase_identity(testcase)
    lookup_task_id = str(testcase_lookup.get('task_id') or '').strip()
    identity_task_id = str(normalized_identity.get('task_id') or '').strip()
    if lookup_task_id and identity_task_id and lookup_task_id != identity_task_id:
        return testcase_lookup

    by_case_id = testcase_lookup.setdefault('by_case_id', {})
    by_case_index = testcase_lookup.setdefault('by_case_index', {})
    by_content = testcase_lookup.setdefault('by_content', {})

    case_id = str(normalized_identity.get('case_id') or '').strip()
    case_index = _to_int(normalized_identity.get('case_index'))
    content_key = _build_identity_content_key(normalized_identity)

    if case_id:
        by_case_id.setdefault(case_id, testcase)
    if case_index is not None:
        by_case_index.setdefault(case_index, testcase)
    if any(content_key):
        by_content.setdefault(content_key, testcase)

    return testcase_lookup


def build_ai_testcase_lookup(project, task_id):
    normalized_task_id = str(task_id or '').strip()
    testcase_lookup = {
        'task_id': normalized_task_id,
        'by_case_id': {},
        'by_case_index': {},
        'by_content': {},
    }

    if not project or not normalized_task_id:
        return testcase_lookup

    queryset = TestCase.objects.filter(project=project).order_by('created_at', 'id')
    for testcase in queryset:
        ai_source = extract_ai_generation_source(getattr(testcase, 'tags', []))
        if not ai_source:
            continue
        if str(ai_source.get('task_id') or '').strip() != normalized_task_id:
            continue
        register_ai_testcase_lookup(testcase_lookup, testcase)

    return testcase_lookup


def find_existing_ai_testcase(project, identity, testcase_lookup=None):
    task_id = identity.get('task_id')
    if not project or not task_id:
        return None

    normalized_task_id = str(task_id or '').strip()
    if isinstance(testcase_lookup, dict) and str(testcase_lookup.get('task_id') or '').strip() == normalized_task_id:
        case_id = str(identity.get('case_id') or '').strip()
        case_index = _to_int(identity.get('case_index'))
        content_key = _build_identity_content_key(identity)

        if case_id:
            testcase = testcase_lookup.get('by_case_id', {}).get(case_id)
            if testcase:
                return testcase

        if case_index is not None:
            testcase = testcase_lookup.get('by_case_index', {}).get(case_index)
            if testcase:
                return testcase

        if any(content_key):
            testcase = testcase_lookup.get('by_content', {}).get(content_key)
            if testcase:
                return testcase

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


def get_or_create_ai_testcase(*, project, testcase_payload, create_callback, apply_default_versions=None, testcase_lookup=None):
    payload = copy.deepcopy(testcase_payload or {})
    identity = build_ai_result_identity(payload)

    payload['tags'] = merge_ai_generation_source_tags(
        payload.get('tags'),
        identity,
        project=project,
        source_label=(extract_ai_generation_source(payload.get('tags')) or {}).get('source_label') or '',
    )
    identity = build_ai_result_identity(payload)

    testcase = find_existing_ai_testcase(project, identity, testcase_lookup=testcase_lookup)
    if testcase:
        if apply_default_versions and not testcase.versions.exists():
            apply_default_versions(testcase, project)
        register_ai_testcase_lookup(testcase_lookup, testcase, identity=identity)
        return testcase, False, payload, identity

    testcase = create_callback(payload)
    if apply_default_versions:
        apply_default_versions(testcase, project)
    register_ai_testcase_lookup(testcase_lookup, testcase, identity=identity)
    return testcase, True, payload, identity
