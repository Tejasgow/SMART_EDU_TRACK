from django.urls import path
from .views import ReportCardView, ClassPerformanceView, TopPerformersView

urlpatterns = [
    # Generate PDF report card for a student
    path('report-card/<int:student_id>/', ReportCardView.as_view(), name='report-card'),

    # Get class-wise average performance
    path('class-performance/', ClassPerformanceView.as_view(), name='class-performance'),
    
    # Get top 3 performers
    path('top-performers/', TopPerformersView.as_view(), name='top-performers'),
]
