from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    # User management
    path("create-teacher-parent/", views.CreateTeacherParentView.as_view(), name="create-teacher-parent"),

    # Session-based login/logout
    path("login/", views.SessionLoginView.as_view(), name="session-login"),
    path("logout/", views.SessionLogoutView.as_view(), name="session-logout"),

    # Password reset
    path("password-reset-request/", views.PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset-confirm/", views.PasswordResetConfirmView.as_view(), name="password-reset-confirm"),

    # JWT authentication
    path("token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
]
