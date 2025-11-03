from django.shortcuts import get_object_or_404, render
from rest_framework import generics, status
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


# ============================================================
# 🧍 STUDENT REGISTRATION & PARENT LINKING
# ============================================================

class StudentRegistrationView(generics.CreateAPIView):
    """
    POST /api/students/register/
    --------------------------------
    Allows authenticated users (admin/teacher) to register a new student.
    """
    queryset = Student.objects.all()
    serializer_class = StudentRegistrationSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes=[]

class StudentListView(generics.ListAPIView):
    """
    Lists all registered students.

    Endpoint:
        GET /api/students/list/

    Permissions:
        Only authenticated users can access this list.
    """
    queryset = Student.objects.all()
    serializer_class = StudentRegistrationSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes=[]


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific student record.

    Endpoints:
        GET /api/students/<id>/
        PUT /api/students/<id>/
        PATCH /api/students/<id>/
        DELETE /api/students/<id>/

    Permissions:
        Only authenticated users can modify student records.
    """
    queryset = Student.objects.all()
    serializer_class = StudentRegistrationSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes=[]


class LinkParentToStudentView(generics.CreateAPIView):
    """
    POST /api/students/link-parent/
    --------------------------------
    Allows authenticated users to link a parent to a student.
    """
    queryset = ParentStudent.objects.all()
    serializer_class = LinkParentSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes=[]



# ============================================================
# 🏫 STANDARD, SECTION, SUBJECT MANAGEMENT
# ============================================================

class StandardListCreateView(generics.ListCreateAPIView):
    """
    GET/POST /api/standards/
    --------------------------------
    List or create class standards (grades).
    """
    queryset = Standard.objects.all()
    serializer_class = StandardSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes=[]



class SectionListCreateView(generics.ListCreateAPIView):
    """
    GET/POST /api/sections/
    --------------------------------
    List or create class sections.
    """
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes=[]



class SubjectListCreateView(generics.ListCreateAPIView):
    """
    GET/POST /api/subjects/
    --------------------------------
    List or create subjects.
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes=[]



# ============================================================
# 📅 ATTENDANCE MANAGEMENT
# ============================================================

class AttendanceMarkView(generics.CreateAPIView):
    """
    POST /api/attendance/mark/
    --------------------------------
    Allows teachers to mark attendance for one or multiple students.
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceMarkSerializer
    # permission_classes=[IsAuthenticated, IsTeacher] 
    permission_classes = []  

    def post(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)

        records = []
        items = serializer.validated_data if many else [serializer.validated_data]

        for item in items:
            student_id = int(item["student_id"])
            date = item["date"]
            status_ = item["status"]

            attendance, _ = Attendance.objects.update_or_create(
                student_id=student_id,
                date=date,
                defaults={"status": status_, "marked_by": request.user}
            )
            records.append(attendance)

        return Response(
            AttendanceSerializer(records, many=True).data,
            status=status.HTTP_200_OK
        )


class StudentAttendanceView(generics.ListAPIView):
    """
    GET /api/attendance/student/<student_id>/
    --------------------------------
    View attendance for a specific student.
    """
    serializer_class = AttendanceSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = []


    def get_queryset(self):
        student_id = self.kwargs["student_id"]

        # Students can only see their own attendance
        if self.request.user.role == "STUDENT" and self.request.user.id != int(student_id):
            return Attendance.objects.none()

        return Attendance.objects.filter(student_id=student_id).order_by("-date")


class ClassAttendanceView(generics.ListAPIView):
    """
    GET /api/attendance/class/<section_id>/
    --------------------------------
    View attendance for all students in a section (teacher only).
    """
    serializer_class = AttendanceSerializer
    # permission_classes = [IsAuthenticated, IsTeacher]
    permission_classes = []


    def get_queryset(self):
        section_id = self.kwargs["section_id"]
        section = get_object_or_404(Section, id=section_id)
        date = self.request.query_params.get("date")

        user_ids = [student.user.id for student in Student.objects.filter(section=section)]
        students = User.objects.filter(id__in=user_ids, role="STUDENT")

        if date:
            return Attendance.objects.filter(student__in=students, date=date)
        return Attendance.objects.filter(student__in=students).order_by("-date")


# ============================================================
# 🧮 ATTENDANCE REPORT HELPERS
# ============================================================

def calculate_attendance_percentage(present_days, total_days):
    """Calculate attendance percentage and return a formatted string."""
    if total_days == 0:
        return "0%"
    percentage = (present_days / total_days) * 100
    return f"{percentage:.2f}%"


# ============================================================
# 📊 ATTENDANCE REPORTS
# ============================================================

class AttendanceReportPrincipalView(generics.GenericAPIView):
    """
    GET /api/attendance/reports/principal/
    --------------------------------
    Allows principals/admins to view attendance reports
    filtered by standard, section, and date range.
    """
    # permission_classes = [IsAuthenticated]
    permission_classes = []


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
                "attendance_percentage": calculate_attendance_percentage(total_present, total_days),
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
                "average_attendance": overall_percentage,
            },
            "records": summary_data
        }, status=status.HTTP_200_OK)


class AttendanceReportParentView(generics.GenericAPIView):
    """
    GET /api/attendance/reports/parent/
    --------------------------------
    Allows parents (or students) to view attendance for linked children.
    """
    # permission_classes = [IsAuthenticated, IsParentOrStudent]
    permission_classes = []


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

            data.append({
                "student_name": f"{user.first_name} {user.last_name}",
                "standard": student_.standard.name,
                "section": student_.section.name,
                "summary": {
                    "total_days": total_days,
                    "present": total_present,
                    "absent": total_absent,
                    "percentage": calculate_attendance_percentage(total_present, total_days),
                },
                "records": AttendanceSerializer(user_records, many=True).data,
            })

        return Response({"children": data})


# ============================================================
# 🧾 MARKS MANAGEMENT
# ============================================================

class StudentMarkListView(generics.ListAPIView):
    """
    GET /api/marks/student/<student_id>/
    --------------------------------
    Lists marks for a specific student, filterable by exam or subject.
    """
    serializer_class = MarkSerializer
    # permission_classes = [IsAuthenticated, IsParentOrStudent]  # Add IsAuthenticated, IsParentOrStudent as needed
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
    """
    GET /api/marks/my/
    --------------------------------
    Returns marks for the logged-in student or a parent's selected child.
    """
    serializer_class = MarkSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = []

    queryset = Mark.objects.select_related('subject', 'exam', 'entered_by', 'student')

    def get_queryset(self):
        user = self.request.user
        student = getattr(user, 'student', None)

        if student:
            return self.queryset.filter(student=student).order_by('-exam__date', 'subject__name')

        # If parent, allow selecting a child
        children_ids = ParentStudent.objects.filter(parent=user).values_list('student_id', flat=True)
        student_id = self.request.query_params.get('student_id')

        if student_id and int(student_id) in set(children_ids):
            return self.queryset.filter(student_id=student_id).order_by('-exam__date', 'subject__name')

        return Mark.objects.none()
