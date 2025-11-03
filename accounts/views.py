from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    CreateUserSerializer,
    SessionLoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)


# ============================================================
# 👩‍🏫 USER CREATION (TEACHER / PARENT)
# ============================================================

class CreateTeacherParentView(CreateAPIView):
    """
    POST /api/accounts/create-user/
    --------------------------------
    Allows admin or system to create teacher or parent accounts.
    """
    serializer_class = CreateUserSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        """Handle POST request for creating a new teacher or parent."""
        return super().post(request, *args, **kwargs)


# ============================================================
# 🔐 SESSION LOGIN / LOGOUT
# ============================================================

class SessionLoginView(APIView):
    """
    POST /api/accounts/session-login/
    --------------------------------
    Logs in a user using Django's session authentication.
    Also returns JWT tokens for API access.
    """
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = SessionLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        login(request, user)
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        }, status=status.HTTP_200_OK)


class SessionLogoutView(APIView):
    """
    GET /api/accounts/logout/
    --------------------------------
    Logs out the currently authenticated user (session-based).
    """
    permission_classes = []

    def get(self, request, *args, **kwargs):
        logout(request)
        return Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK
        )


# ============================================================
# 🪪 JWT LOGIN (TOKEN-BASED AUTHENTICATION)
# ============================================================

class JWTLoginView(APIView):
    """
    POST /api/accounts/jwt-login/
    --------------------------------
    Authenticates the user and returns a JWT token pair.
    """
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = SessionLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        }, status=status.HTTP_200_OK)


# ============================================================
# 🔁 PASSWORD RESET FUNCTIONALITY
# ============================================================

class PasswordResetRequestView(GenericAPIView):
    """
    POST /api/accounts/password-reset-request/
    --------------------------------
    Generates a password reset link for a given email.
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_link = f"http://127.0.0.1:8000/api/accounts/password-reset-confirm/?uid={uid}&token={token}"

        return Response(
            {
                "message": "Password reset link generated successfully.",
                "reset_link": reset_link,
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(GenericAPIView):
    """
    POST /api/accounts/password-reset-confirm/
    --------------------------------
    Confirms password reset using UID and token, sets new password.
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Password reset successful"},
            status=status.HTTP_200_OK
        )


# ============================================================
# 🧩 UTILITY VIEW PLACEHOLDER
# ============================================================

def render_placeholder(request):
    """Optional placeholder view for testing or extensions."""
    return render(request, "placeholder.html")
