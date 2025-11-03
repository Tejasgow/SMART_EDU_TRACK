from django.urls import path
from .views import MarkEntryView, ExamListCreateView


# ============================================================
# 🧮 PERFORMANCE MODULE ROUTES (EXAMS & MARKS)
# ============================================================

urlpatterns = [

    # ------------------------------------------------------------
    # 📝 MARKS ENTRY ROUTES
    # ------------------------------------------------------------
    path(
        "marks/entry/",
        MarkEntryView.as_view(),
        name="marks-entry"
    ),

    # ------------------------------------------------------------
    # 🧾 EXAM ROUTES
    # ------------------------------------------------------------
    path(
        "exams/",
        ExamListCreateView.as_view(),
        name="exam-list-create"
    ),
]
