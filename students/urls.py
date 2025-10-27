from django.urls import path
from . import views

urlpatterns = [
    # ------------------------------
    # Student & Parent
    # ------------------------------
    path('register/', views.StudentRegistrationView.as_view(), name='student-register'),
    path('link-parent/', views.LinkParentToStudentView.as_view(), name='link-parent'),

    # ------------------------------
    # Standard, Section, Subject
    # ------------------------------
    path('standards/', views.StandardListCreateView.as_view(), name='standard-list-create'),
    path('sections/', views.SectionListCreateView.as_view(), name='section-list-create'),
    path('subjects/', views.SubjectListCreateView.as_view(), name='subject-list-create'),

    # ------------------------------
    # Attendance
    # ------------------------------
    path('attendance/mark/', views.AttendanceMarkView.as_view(), name='attendance-mark'),
    path('attendance/student/<int:student_id>/', views.StudentAttendanceView.as_view(), name='student-attendance'),
    path('attendance/class/<int:section_id>/', views.ClassAttendanceView.as_view(), name='class-attendance'),
    path('attendance/report/principal/', views.AttendanceReportPrincipalView.as_view(), name='attendance-report-principal'),
    path('attendance/report/parent/', views.AttendanceReportParentView.as_view(), name='attendance-report-parent'),

    # ------------------------------
    # Marks
    # ------------------------------
    path('marks/student/<int:student_id>/', views.StudentMarkListView.as_view(), name='student-marks'),
    path('marks/my/', views.MyMarkListView.as_view(), name='my-marks'),

]
