from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, LogoutView, ProfileView, UserViewSet, UserProfileView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/profile/', ProfileView.as_view(), name='auth-profile'),
    path('auth/me/', ProfileView.as_view(), name='auth-me'),
    re_path(r'^profile/?$', UserProfileView.as_view(), name='user-profile'),
    path('', include(router.urls)),
]
