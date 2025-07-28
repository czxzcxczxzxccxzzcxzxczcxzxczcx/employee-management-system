from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Attendance URLs
    path('attendances/', views.AttendanceListCreateView.as_view(), name='attendance-list-create'),
    path('attendances/<int:pk>/', views.AttendanceDetailView.as_view(), name='attendance-detail'),
    
    # Analytics URLs
    path('analytics/', views.attendance_analytics, name='attendance-analytics'),
    path('employees/<int:employee_id>/stats/', views.employee_attendance_stats, name='employee-attendance-stats'),
    path('bulk-stats/', views.bulk_attendance_stats, name='bulk-attendance-stats'),
]