from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ChangePasswordView,
    ProfileView,
    BecomeSellerView,
    AvatarView,
    UserViewSet,
    UserProfileView,
)


class OptionalSlashRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = r'/?'


router = OptionalSlashRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    re_path(r'^auth/register/?$', RegisterView.as_view(), name='auth-register'),
    re_path(r'^auth/login/?$', LoginView.as_view(), name='auth-login'),
    re_path(r'^auth/logout/?$', LogoutView.as_view(), name='auth-logout'),
    re_path(r'^auth/change-password/?$', ChangePasswordView.as_view(), name='auth-change-password'),
    re_path(r'^auth/profile/?$', ProfileView.as_view(), name='auth-profile'),
    re_path(r'^auth/me/?$', ProfileView.as_view(), name='auth-me'),
    re_path(r'^auth/me/avatar/?$', AvatarView.as_view(), name='auth-avatar'),
    re_path(r'^auth/become-seller/?$', BecomeSellerView.as_view(), name='auth-become-seller'),
    re_path(r'^profile/?$', UserProfileView.as_view(), name='user-profile'),
    path('', include(router.urls)),
]
