from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet


class OptionalSlashRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = r'/?'


router = OptionalSlashRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
