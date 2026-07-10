from uuid import uuid4

from rest_framework.response import Response


def get_request_id(request=None) -> str:
    if request is None:
        return str(uuid4())

    meta = getattr(request, 'META', {}) or {}
    return (
        meta.get('HTTP_X_REQUEST_ID')
        or meta.get('HTTP_X_CORRELATION_ID')
        or str(uuid4())
    )


def build_error_payload(code: str, message: str, details=None, request=None) -> dict:
    """构造兼容旧 error 字段的新错误结构。"""
    return {
        'code': code,
        'message': message,
        'error': message,
        'details': details or {},
        'request_id': get_request_id(request),
    }


def error_response(code: str, message: str, status_code: int, details=None, request=None) -> Response:
    return Response(
        build_error_payload(code, message, details=details, request=request),
        status=status_code,
    )
