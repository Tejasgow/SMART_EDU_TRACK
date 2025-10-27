from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import (
    StudentRegistrationSerializer, LinkParentSerializer,
    SectionSerializer, StandardSerializer,
    AttendanceMarkSerializer, AttendanceSerializer,
    SubjectSerializer, MarkSerializer
    
)
from .models import Student, ParentStudent, Standard, Section, Attendance, Subject
from accounts.models import User
from performance.models import Exam, Mark
from .permissions import IsTeacher, IsParentOrStudent


# ------------------------------
# Student Registration & Linking
# ------------------------------
class StudentRegistrationView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentRegistrationSerializer
    permission_classes = [IsAuthenticated]


class LinkParentToStudentView(generics.CreateAPIView):
    queryset = ParentStudent.objects.all()
    serializer_class = LinkParentSerializer
    permission_classes = [IsAuthenticated]


# ------------------------------
# Standard, Section, Subject CRUD
# ------------------------------
class StandardListCreateView(generics.ListCreateAPIView):
    queryset = Standard.objects.all()
    serializer_class = StandardSerializer
    permission_classes = [IsAuthenticated]


class SectionListCreateView(generics.ListCreateAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated]


class SubjectListCreateView(generics.ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]


# ------------------------------
# Attendance Views
# ------------------------------
class AttendanceMarkView(generics.CreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceMarkSerializer
    permission_classes = []  # You can add permissions like IsAuthenticated, IsTeacher

    def post(self, request, *args, **kwargs):
        # Detect if the request data is a list (multiple students)
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)

        records = []

        # Handle multiple student attendance
        for item in serializer.validated_data if many else [serializer.validated_data]:
            student_id = int(item["student_id"])
            date = item["date"]
            status_ = item["status"]

            # Either update existing attendance or create new
            attendance, created = Attendance.objects.update_or_create(
                student_id=student_id,
                date=date,
                defaults={"status": status_, "marked_by": request.user}
            )
            records.append(attendance)

        return Response(AttendanceSerializer(records, many=True).data, status=status.HTTP_200_OK)

class StudentAttendanceView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student_id = self.kwargs["student_id"]
        # Student can view only their own attendance
        if self.request.user.role == "STUDENT" and self.request.user.id != int(student_id):
            return Attendance.objects.none()
        return Attendance.objects.filter(student_id=student_id).order_by("-date")


class ClassAttendanceView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        section_id = self.kwargs["section_id"]
        section = get_object_or_404(Section, id=section_id)
        date = self.request.query_params.get("date")
        user_ids = [student.user.id for student in Student.objects.filter(section=section)]
        students = User.objects.filter(id__in=user_ids, role="STUDENT")

        if date:
            return Attendance.objects.filter(student__in=students, date=date)
        return Attendance.objects.filter(student__in=students).order_by("-date")


# ------------------------------
# Utility
# ------------------------------
def calculate_attendance_percentage(present_days, total_days):
    if total_days == 0:
        return "0%"
    percentage = (present_days / total_days) * 100
    return f"{percentage:.2f}%"


# ------------------------------
# Attendance Reports
# ------------------------------

class AttendanceReportPrincipalView(generics.GenericAPIView):
    """
    Allows principals (ADMIN role) to view attendance reports for all students,
    optionally filtered by standard, section, and date range.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = Attendance.objects.all()
        standard_name = request.query_params.get("standard")
        section_name = request.query_params.get("section")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        # Filter by standard
        if standard_name:
            standards = Standard.objects.filter(name=standard_name)
            students = Student.objects.filter(standard__in=standards)
            queryset = queryset.filter(student__in=[s.user for s in students])

        # Filter by section
        if section_name:
            sections = Section.objects.filter(name=section_name)
            students = Student.objects.filter(section__in=sections)
            queryset = queryset.filter(student__in=[s.user for s in students])

        # Filter by date range
        if from_date and to_date:
            queryset = queryset.filter(date__range=[from_date, to_date])

        # Build summary per student
        summary_data = []
        student_ids = queryset.values_list("student_id", flat=True).distinct()
        for sid in student_ids:
            student_attendance = queryset.filter(student_id=sid)
            if not student_attendance.exists():
                continue
            student_obj = student_attendance.first().student
            total_days = student_attendance.count()
            total_present = student_attendance.filter(status="PRESENT").count()
            total_absent = student_attendance.filter(status="ABSENT").count()

            student_record = Student.objects.filter(user=student_obj).first()
            summary_data.append({
                "student_name": f"{student_obj.first_name} {student_obj.last_name}",
                "standard": student_record.standard.name if student_record else "",
                "section": student_record.section.name if student_record else "",
                "total_present": total_present,
                "total_absent": total_absent,
                "attendance_percentage": calculate_attendance_percentage(total_present, total_days)
            })

        # Overall summary
        total_students = len(student_ids)
        total_days = queryset.values("date").distinct().count()
        overall_present = queryset.filter(status="PRESENT").count()
        overall_percentage = calculate_attendance_percentage(overall_present, queryset.count())

        return Response({
            "summary": {
                "total_students": total_students,
                "total_days": total_days,
                "average_attendance": overall_percentage
            },
            "records": summary_data
        }, status=status.HTTP_200_OK)

class AttendanceReportParentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated,IsParentOrStudent]

    def get(self, request, *args, **kwargs):
        parent = request.user
        linked_students = [link.student for link in ParentStudent.objects.filter(parent=parent)]
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        data = []
        for student_ in linked_students:
            user = student_.user
            user_records = Attendance.objects.filter(student=user)
            if from_date and to_date:
                user_records = user_records.filter(date__range=[from_date, to_date])

            if not user_records.exists():
                continue

            total_days = user_records.count()
            total_present = user_records.filter(status="PRESENT").count()
            total_absent = user_records.filter(status="ABSENT").count()

            child_data = {
                "student_name": f"{student_.user.first_name} {student_.user.last_name}",
                "standard": student_.standard.name,
                "section": student_.section.name,
                "summary": {
                    "total_days": total_days,
                    "present": total_present,
                    "absent": total_absent,
                    "percentage": calculate_attendance_percentage(total_present, total_days)
                },
                "records": AttendanceSerializer(user_records, many=True).data
            }
            data.append(child_data)

        return Response({"children": data})


# ------------------------------
# Marks Views
# ------------------------------
class StudentMarkListView(generics.ListAPIView):
    serializer_class = MarkSerializer
    # permission_classes = [IsAuthenticated, IsParentOrStudent]
    permission_classes = []
    queryset = Mark.objects.select_related('subject', 'exam', 'entered_by', 'student')

    def get_queryset(self):
        student_id = self.kwargs.get('student_id')
        student = get_object_or_404(Student, pk=student_id)
        self.check_object_permissions(self.request, student)
        qs = self.queryset.filter(student=student)

        exam_id = self.request.query_params.get('exam')
        subject_id = self.request.query_params.get('subject')
        if exam_id:
            qs = qs.filter(exam_id=exam_id)
        if subject_id:
            qs = qs.filter(subject_id=subject_id)

        return qs.order_by('-exam__date', 'subject__name')


class MyMarkListView(generics.ListAPIView):
    serializer_class = MarkSerializer
    permission_classes = [IsAuthenticated]
    queryset = Mark.objects.select_related('subject', 'exam', 'entered_by', 'student')

    def get_queryset(self):
        user = self.request.user
        student = getattr(user, 'student', None)
        if student:
            return self.queryset.filter(student=student).order_by('-exam__date', 'subject__name')

        # If parent, allow children
        children_ids = ParentStudent.objects.filter(parent=user).values_list('student_id', flat=True)
        student_id = self.request.query_params.get('student_id')
        if student_id and int(student_id) in set(children_ids):
            return self.queryset.filter(student_id=student_id).order_by('-exam__date','subject__name')

        return Mark.objects.none()
from django.shortcuts import render

# Create your views here.
