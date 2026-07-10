import json
import re
from typing import Any


REDACTED = '***REDACTED***'

SENSITIVE_KEYWORDS = {
    'api_key',
    'apikey',
    'access',
    'refresh',
    'token',
    'authorization',
    'cookie',
    'password',
    'passwd',
    'secret',
    'secret_key',
    'key',
}


def _is_sensitive_key(key: Any) -> bool:
    key_text = str(key).lower().replace('-', '_')
    return any(keyword in key_text for keyword in SENSITIVE_KEYWORDS)


def mask_secret(value: Any) -> str:
    """把敏感值压缩成首尾少量字符，日志里不能出现完整原文。"""
    if value is None:
        return REDACTED

    text = str(value)
    if len(text) <= 8:
        return REDACTED

    return f'{text[:4]}...{text[-4:]}'


def redact_sensitive_data(data: Any, max_depth: int = 6) -> Any:
    """递归脱敏 dict/list 结构，避免配置、请求头或响应体被完整写入日志。"""
    if max_depth <= 0:
        return REDACTED

    if isinstance(data, dict):
        redacted = {}
        for key, value in data.items():
            if _is_sensitive_key(key):
                redacted[key] = mask_secret(value)
            else:
                redacted[key] = redact_sensitive_data(value, max_depth=max_depth - 1)
        return redacted

    if isinstance(data, list):
        return [redact_sensitive_data(item, max_depth=max_depth - 1) for item in data]

    if isinstance(data, tuple):
        return tuple(redact_sensitive_data(item, max_depth=max_depth - 1) for item in data)

    if isinstance(data, str):
        return redact_text(data)

    return data


def redact_text(text: Any, max_length: int = 1000) -> str:
    """脱敏日志文本，并限制长度，避免外部服务错误体泄露密钥或大段响应。"""
    if text is None:
        return ''

    value = str(text)

    replacements = [
        (r'(?i)(authorization\s*[:=]\s*bearer\s+)([A-Za-z0-9._\-]+)', rf'\1{REDACTED}'),
        (r'(?i)(authorization\s*[:=]\s*)([^\s,;]+)', rf'\1{REDACTED}'),
        (r'(?i)(cookie\s*[:=]\s*)([^,\n\r]+)', rf'\1{REDACTED}'),
        (
            r'(?i)(["\']?(?:api[_-]?key|access|refresh|token|password|secret|secret[_-]?key)["\']?\s*[:=]\s*["\']?)([^"\'\s,}\]]+)',
            rf'\1{REDACTED}',
        ),
        (r'(?i)(bearer\s+)([A-Za-z0-9._\-]+)', rf'\1{REDACTED}'),
        (r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b', REDACTED),
        (r'\bsk-[A-Za-z0-9_-]{12,}\b', REDACTED),
    ]

    for pattern, replacement in replacements:
        value = re.sub(pattern, replacement, value)

    if len(value) > max_length:
        return f'{value[:max_length]}...<truncated>'

    return value


def redact_json_for_log(data: Any, max_length: int = 1000) -> str:
    """把结构化数据脱敏后转成适合日志使用的短文本。"""
    redacted = redact_sensitive_data(data)
    try:
        text = json.dumps(redacted, ensure_ascii=False, default=str)
    except TypeError:
        text = str(redacted)
    return redact_text(text, max_length=max_length)
