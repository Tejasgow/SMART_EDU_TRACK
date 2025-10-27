from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.db.models import Avg

from accounts.permissions import IsTeacherOrPrincipal, IsPrincipal
from students.models import Student
from performance.models import Mark


# ------------------------------
# Report Card PDF
# ------------------------------
class ReportCardView(APIView):
    permission_classes = []

    def get(self, request, student_id):
        student = get_object_or_404(Student, id=student_id)
        marks = Mark.objects.filter(student=student)

        # Create PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_card_{student_id}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 800, f"Report Card - {student.user.get_full_name()}")

        p.setFont("Helvetica", 12)
        y = 760
        if not marks.exists():
            p.drawString(100, y, "No marks available.")
        else:
            for mark in marks:
                p.drawString(100, y, f"{mark.subject.name}: {mark.marks_obtained}/{mark.max_marks} - Grade: {mark.grade}")
                y -= 20

        p.showPage()
        p.save()
        return response


# ------------------------------
# Class Performance Summary
# ------------------------------
class ClassPerformanceView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated, IsPrincipal]
    permission_classes = []


    def get_queryset(self):
        """
        Returns average marks per standard.
        """
        return (
            Mark.objects
            .values('student__standard__name')
            .annotate(avg_marks=Avg('marks_obtained'))
            .order_by('student__standard__name')
        )

    def list(self, request, *args, **kwargs):
        data = list(self.get_queryset())
        return Response(data)


# ------------------------------
# Top Performers
# ------------------------------
class TopPerformersView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated, IsPrincipal]
    permission_classes = []

    def get_queryset(self):
        """
        Returns top 3 students by average marks.
        """
        return (
            Mark.objects
            .values(
                'student__id',
                'student__user__first_name',
                'student__user__last_name',
                'student__standard__name'
            )
            .annotate(avg_marks=Avg('marks_obtained'))
            .order_by('-avg_marks')[:3]
        )

    def list(self, request, *args, **kwargs):
        data = list(self.get_queryset())
        return Response(data)
