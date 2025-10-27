from rest_framework import permissions
from .models import ParentStudent, Student


class IsTeacher(permissions.BasePermission):
    """
    Allows access only to users with role 'TEACHER'.
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', '') == 'TEACHER'
        )


class IsParentOrStudent(permissions.BasePermission):
    """
    Grants permission if the user is:
    - The student themselves
    - A parent linked to the student
    - An admin/staff user
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Get student object from the object itself or its 'student' attribute
        student = getattr(obj, 'student', None)
        if student is None and isinstance(obj, Student):
            student = obj

        if student is None:
            return False

        # Student checking themselves
        if hasattr(student, 'user') and student.user == user:
            return True

        # Parent linked to this student
        if ParentStudent.objects.filter(parent=user, student=student).exists():
            return True

        # Admin/staff override
        return user.is_staff or user.role == "ADMIN"



