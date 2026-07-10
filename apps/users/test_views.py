from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@csrf_exempt
@require_http_methods(["POST"])
def test_register(request):
    try:
        data = json.loads(request.body)
        
        # 检查用户名是否已存在
        if User.objects.filter(username=data.get('username')).exists():
            return JsonResponse({
                'success': False,
                'error': '用户名已存在'
            }, status=400)
        
        # 简单的用户创建
        user = User.objects.create_user(
            username=data.get('username'),
            email=data.get('email', ''),
            password=data.get('password'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            department=data.get('department', ''),
            position=data.get('position', '')
        )
        
        refresh = RefreshToken.for_user(user)
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
