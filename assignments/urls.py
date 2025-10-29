from django.urls import path
from .views import AssignmentCreateView, AssignmentListView


# ============================================================
# 📘 ASSIGNMENT MODULE ROUTES
# ============================================================

urlpatterns = [

    # ------------------------------------------------------------
    # 📄 ASSIGNMENT LIST & DETAILS
    # ------------------------------------------------------------
    path(
        "assignments/",
        AssignmentListView.as_view(),
        name="assignment-list"
    ),

    # ------------------------------------------------------------
    # 📤 ASSIGNMENT UPLOAD (CREATE)
    # ------------------------------------------------------------
    path(
        "assignments/upload/",
        AssignmentCreateView.as_view(),
        name="assignment-create"
    ),
]
