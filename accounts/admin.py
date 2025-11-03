from django.contrib import admin
from .models import User


# ============================================================
# 👤 CUSTOM USER ADMIN CONFIGURATION
# ============================================================

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for the User model.
    Displays username and email in the admin list view.
    """
    model = User
    list_display = ("username", "email")
    search_fields = ("username", "email")
    list_filter = ("role",)
    ordering = ("username",)
