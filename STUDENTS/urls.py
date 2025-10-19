from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path('studentreg/',views.StudentRegistrationView.as_view()),
    path('isteacher/',views.IsTeacher),
    path('link/',views.LinkparentToStudentView.as_view()),
    path('standards/',views.StandardListCreatView.as_view(),name="views.StandardListCreatView"),
    path("sections/",views.SectionListCreateView.as_view(),name="views.SectionListCreateView"),
    path("attendance/mark/", csrf_exempt(views.AttendanceMarkView.as_view()), name="attendance-mark"),
    path("attendance-student/<int:student_id>/",views.AttendanceMarkView.as_view(),name="views.AttendanceMarkView"),
    path("attendance-class/<int:section_id>/",views.AttendanceMarkView.as_view(),name="views.AttendanceMarkView"),
    path("attendance-report/principal/",views.AttendanceReportPrincipalView.as_view(),name="views.AttendanceReportView"),
    path("attendance-report/parent/",views.AttendanceReportParentView.as_view(),name="views.ParentAttendanceReportView"),
    path("students/<int:student_id>/marks/",views.StudentMarkListView.as_view(),name="student_marks"),
    path("students/me/marks/",views.MyMarkListView.as_view(),name="my_marks"),


]