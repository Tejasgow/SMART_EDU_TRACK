from django.urls import path
from . import views
# ============================================================
# 📘 ASSIGNMENT MODULE ROUTES
# ============================================================

urlpatterns = [
    # ------------------------------------------------------------
    # 📄 ASSIGNMENT LIST & DETAILS
    # ------------------------------------------------------------
    path(
        "assignments/",
        views.AssignmentListView.as_view(),
        name="assignment-list"
    ),
    # ------------------------------------------------------------
    # 📤 ASSIGNMENT UPLOAD (CREATE)
    # ------------------------------------------------------------
    path(
        "assignments/upload/",
        views.AssignmentCreateView.as_view(),
        name="assignment-create"
    ),
    # ------------------------------------------------------------
    # 📄 ASSIGNMENT DETAILS
    # ------------------------------------------------------------
    path(
        "assignments/<int:pk>/",
        views.AssignmentDetailView.as_view(),
        name="assignment-detail"
    ),

    # ------------------------------------------------------------
    # 📤 ASSIGNMENT SUBMISSION (CREATE)
    # ------------------------------------------------------------
    path(
        "assignments/submit/",
        views.AssignmentSubmissionCreateView.as_view(),
        name="assignment-submit"
    ),
    # ------------------------------------------------------------
    # 📄 ASSIGNMENT SUBMISSION LIST
    # ------------------------------------------------------------
    path(
        "assignments/submissions/",
        views.AssignmentSubmissionListView.as_view(),
        name="assignment-submission-list"
    ),
]


