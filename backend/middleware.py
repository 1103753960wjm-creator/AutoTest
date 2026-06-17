from django.utils.deprecation import MiddlewareMixin

class DisableCSRFMiddleware(MiddlewareMixin):
    def process_request(self, request):
        from django.conf import settings

        # 仅在显式开关开启时禁用 API CSRF，避免生产环境静默放开。
        if settings.DISABLE_CSRF_FOR_API and request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
