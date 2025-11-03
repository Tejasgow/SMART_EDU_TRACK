from django.db import models
from django.contrib.auth.models import AbstractUser

# ============================================================
# 📌 Custom User Model
# ============================================================
class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    Roles:
        - ADMIN
        - TEACHER
        - STUDENT
        - PARENT
    """
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
        ('PARENT', 'Parent'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='STUDENT',
        help_text="Designates the role of the user."
    )

    def __str__(self):
        """
        String representation of the user, including role.
        """
        return f"{self.username} ({self.get_role_display()})"
