"""
URL configuration for zoco_api project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root_view(request):
    """
    Directorio raíz de la API REST de Zoco.
    Muestra los endpoints disponibles para la aplicación móvil y servicios web.
    """
    base_uri = request.build_absolute_uri('/')[:-1]
    return Response({
        "name": "Zoco Hyperlocal E-Commerce REST API",
        "version": "1.0.0",
        "status": "online",
        "description": "API REST para conectar productores y consumidores locales.",
        "endpoints": {
            "products": f"{base_uri}/api/v1/products",
            "orders": f"{base_uri}/api/v1/orders",
            "media": f"{base_uri}/api/v1/media",
            "notifications": f"{base_uri}/api/v1/notifications",
            "users": f"{base_uri}/api/v1/users",
            "auth": {
                "register": f"{base_uri}/api/v1/auth/register/",
                "login": f"{base_uri}/api/v1/auth/login/",
                "logout": f"{base_uri}/api/v1/auth/logout/",
                "profile": f"{base_uri}/api/v1/auth/profile/"
            },
            "admin": f"{base_uri}/admin/"
        }
    })


# API v1 routes
v1_patterns = [
    path('', include('products.urls')),
    path('', include('orders.urls')),
    path('', include('multimedia.urls')),
    path('', include('notifications.urls')),
    path('', include('accounts.urls')),
]

urlpatterns = [
    path('', api_root_view, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/v1/', include((v1_patterns, 'v1'))),
    # Also support direct /api/ for backward compatibility or alternate configs
    path('api/', include(v1_patterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
