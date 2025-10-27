from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.db.models import Avg
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from io import BytesIO
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

        # Create a byte buffer for PDF
        buffer = BytesIO()

        # Create a canvas
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, height - 80, f"Report Card")

        p.setFont("Helvetica", 12)
        p.drawString(100, height - 110, f"Student: {student.user.get_full_name()}")
        p.drawString(100, height - 130, f"Student ID: {student.id}")

        # Prepare table data
        y_position = height - 200
        data = [["Subject", "Marks Obtained", "Max Marks", "Grade"]]  # table header

        if marks.exists():
            for mark in marks:
                data.append([
                    mark.subject.name,
                    str(mark.marks_obtained),
                    str(mark.max_marks),
                    mark.grade
                ])
        else:
            data.append(["No marks available", "", "", ""])

        # Create the table
        table = Table(data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 1.0 * inch])

        # Add some styling
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ])
        table.setStyle(style)

        # Render the table
        table.wrapOn(p, width, height)
        table.drawOn(p, 70, y_position - 20 * len(data))

        p.showPage()
        p.save()

        # Get PDF data
        pdf = buffer.getvalue()
        buffer.close()

        # Create HTTP response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_card_{student_id}.pdf"'
        response.write(pdf)
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
