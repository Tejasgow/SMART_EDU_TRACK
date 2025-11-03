from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .models import User


# ============================================================
# 👤 USER CREATION SERIALIZER
# ============================================================
class CreateUserSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Teacher or Parent accounts.
    Enforces role validation and secure password handling.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username", "email", "password",
            "role", "first_name", "last_name"
        ]

    def validate_role(self, value):
        """
        Ensure only allowed roles ('TEACHER', 'PARENT') are accepted.
        """
        allowed_roles = ["TEACHER", "PARENT"]
        if value.upper() not in allowed_roles:
            raise serializers.ValidationError(f"Role must be one of {allowed_roles}.")
        return value.upper()

    def create(self, validated_data):
        """
        Create a new user instance with a hashed password.
        """
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ============================================================
# 🔐 SESSION / JWT LOGIN SERIALIZER
# ============================================================
class SessionLoginSerializer(serializers.Serializer):
    """
    Handles user authentication for both session and JWT logins.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("Account disabled, contact administrator.")

        return {"user": user}


# ============================================================
# 🔁 PASSWORD RESET REQUEST SERIALIZER
# ============================================================
class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Validates email for initiating a password reset process.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


# ============================================================
# 🔄 PASSWORD RESET CONFIRMATION SERIALIZER
# ============================================================
class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Handles validation and updating of the new password using
    UID and token verification.
    """
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data["uid"]))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError("Invalid UID.")

        if not default_token_generator.check_token(user, data["token"]):
            raise serializers.ValidationError("Invalid or expired token.")

        data["user"] = user
        return data

    def save(self):
        """
        Sets and saves the new password for the user.
        """
        user = self.validated_data["user"]
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return user
