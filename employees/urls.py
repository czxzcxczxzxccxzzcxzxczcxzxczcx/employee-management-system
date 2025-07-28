from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    # Department URLs
    path('departments/', views.DepartmentListCreateView.as_view(), name='department-list-create'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department-detail'),
    
    # Employee URLs
    path('employees/', views.EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/search/', views.employee_search, name='employee-search'),
    
    # Performance URLs
    path('performances/', views.PerformanceListCreateView.as_view(), name='performance-list-create'),
    path('performances/<int:pk>/', views.PerformanceDetailView.as_view(), name='performance-detail'),
    
    # Analytics URLs
    path('analytics/', views.employee_analytics, name='employee-analytics'),
    path('stats/', views.public_stats, name='public-stats'),  # No auth required
]