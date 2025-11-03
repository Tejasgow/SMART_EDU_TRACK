from django.urls import path
from . import views


# ============================================================
# 🎓 STUDENT & ACADEMIC MODULE ROUTES
# ============================================================

urlpatterns = [

    # ------------------------------------------------------------
    # 👩‍🎓 STUDENT & PARENT ROUTES
    # ------------------------------------------------------------
    path(
        "register/",
        views.StudentRegistrationView.as_view(),
        name="student-register"
    ),
    path(
        "list/",
        views.StudentListView.as_view(),
        name="student-list"
    ),
    path(
        "<int:pk>/",
        views.StudentDetailView.as_view(),
        name="student-detail"
    ),
    path(
        "link-parent/",
        views.LinkParentToStudentView.as_view(),
        name="link-parent"
    ),

    # ------------------------------------------------------------
    # 🏫 STANDARD, SECTION & SUBJECT ROUTES
    # ------------------------------------------------------------
    path(
        "standards/",
        views.StandardListCreateView.as_view(),
        name="standard-list-create"
    ),
    path(
        "sections/",
        views.SectionListCreateView.as_view(),
        name="section-list-create"
    ),
    path(
        "subjects/",
        views.SubjectListCreateView.as_view(),
        name="subject-list-create"
    ),

    # ------------------------------------------------------------
    # 📅 ATTENDANCE ROUTES
    # ------------------------------------------------------------
    path(
        "attendance/mark/",
        views.AttendanceMarkView.as_view(),
        name="attendance-mark"
    ),
    path(
        "attendance/student/<int:student_id>/",
        views.StudentAttendanceView.as_view(),
        name="student-attendance"
    ),
    path(
        "attendance/class/<int:section_id>/",
        views.ClassAttendanceView.as_view(),
        name="class-attendance"
    ),
    path(
        "attendance/report/principal/",
        views.AttendanceReportPrincipalView.as_view(),
        name="attendance-report-principal"
    ),
    path(
        "attendance/report/parent/",
        views.AttendanceReportParentView.as_view(),
        name="attendance-report-parent"
    ),

    # ------------------------------------------------------------
    # 🧾 MARKS ROUTES
    # ------------------------------------------------------------
    path(
        "marks/student/<int:student_id>/",
        views.StudentMarkListView.as_view(),
        name="student-marks"
    ),
    path(
        "marks/my/",
        views.MyMarkListView.as_view(),
        name="my-marks"
    ),
]
