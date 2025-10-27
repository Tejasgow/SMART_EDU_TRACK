from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Mark, Exam
from .serializers import MarkEntrySerializer, ExamSerializer
from accounts.permissions import IsTeacherOrPrincipal


# ----------------------------
# Marks Entry View
# ----------------------------
class MarkEntryView(ListCreateAPIView):
    """
    Accepts a list of marks entries for students.
    Example payload:
    [
        {
            "exam": 1,
            "student": 3,
            "subject": 2,
            "marks_obtained": 45,
            "max_marks": 50,
            "remarks": "Good improvement"
        },
        ...
    ]
    """
    # permission_classes = [IsAuthenticated, IsTeacherOrPrincipal]
    permission_classes =[]

    serializer_class = MarkEntrySerializer
    queryset = Mark.objects.select_related('exam', 'student', 'subject', 'entered_by').all()

    def post(self, request):
        serializer = MarkEntrySerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save(entered_by=request.user)
            return Response({"message": "Marks saved successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------
# Exam List and Create View
# ----------------------------
class ExamListCreateView(ListCreateAPIView):
    """
    List all exams or create a new exam.
    """
    queryset = Exam.objects.all().order_by('-date')
    serializer_class = ExamSerializer
    # permission_classes = [IsAuthenticated, IsTeacherOrPrincipal]
    permission_classes =[]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
