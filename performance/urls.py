from django.urls import path
from .views import MarkEntryView, ExamListCreateView

urlpatterns = [
    # Marks Entry
    path("marks/entry/", MarkEntryView.as_view(), name="marks-entry"),

    # Exam List and Create
    path("exams/", ExamListCreateView.as_view(), name="exam-list-create"),
]
