from django.shortcuts import render
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from .models import Assignment
from .serializers import AssignmentSerializer
from accounts.permissions import IsTeacherOrPrincipal


# ============================================================
# 📘 ASSIGNMENT MANAGEMENT VIEWS
# ============================================================

class AssignmentCreateView(generics.CreateAPIView):
    """
    POST /api/assignments/upload/
    --------------------------------
    Allows teachers or principals to create assignments,
    optionally including a file upload.
    """
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrPrincipal]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        """
        Automatically assign the current user as the person who created the assignment.
        """
        serializer.save(assigned_by=self.request.user)


class AssignmentListView(generics.ListAPIView):
    """
    GET /api/assignments/
    --------------------------------
    Accessible by students, parents, teachers, and principals.

    Optional query parameters:
        - ?subject=<subject_id> → Filter by subject
        - ?teacher=<user_id>   → Filter by teacher (assigned_by)
    """
    queryset = Assignment.objects.select_related('subject', 'assigned_by')
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filter assignments by subject or teacher.
        """
        queryset = super().get_queryset()
        params = self.request.query_params

        # Filter by subject
        subject_id = params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)

        # Filter by teacher/assigned_by
        teacher_id = params.get('teacher')
        if teacher_id:
            queryset = queryset.filter(assigned_by_id=teacher_id)

        return queryset
