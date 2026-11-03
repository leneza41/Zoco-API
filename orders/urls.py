from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet


class OptionalSlashRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = r'/?'


router = OptionalSlashRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
