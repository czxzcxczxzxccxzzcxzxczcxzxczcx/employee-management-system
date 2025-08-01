from django.shortcuts import render
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Department, Employee, Performance

from .serializers import (
    DepartmentSerializer,
    EmployeeListSerializer,
    EmployeeDetailSerializer,
    EmployeeCreateUpdateSerializer,
    PerformanceSerializer,
    PerformanceCreateUpdateSerializer
)

# This view allows you to retrieve a list of all departments or create a new department
class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

# This view allows you to retrieve, update or delete a specific department
class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a department"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


# This view allows you to retrieve a list of all employees or create a new employee
class EmployeeListCreateView(generics.ListCreateAPIView):
    """List all employees or create a new employee"""
    queryset = Employee.objects.select_related('department').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'is_active', 'position']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id']
    ordering_fields = ['first_name', 'last_name', 'date_joined', 'created_at']
    ordering = ['last_name', 'first_name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeeCreateUpdateSerializer
        return EmployeeListSerializer

# This view allows you to retrieve, update or delete a specific employee
class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an employee"""
    queryset = Employee.objects.select_related('department').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EmployeeCreateUpdateSerializer
        return EmployeeDetailSerializer

# This view allows you to index employees that meet certain criteria
class PerformanceListCreateView(generics.ListCreateAPIView):
    """List all performance records or create a new one"""
    queryset = Performance.objects.select_related('employee').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'rating', 'review_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['review_date', 'rating', 'created_at']
    ordering = ['-review_date']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PerformanceCreateUpdateSerializer
        return PerformanceSerializer

# This view allows you to retrieve, update or delete a specific performance record
class PerformanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a performance record"""
    queryset = Performance.objects.select_related('employee').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PerformanceCreateUpdateSerializer
        return PerformanceSerializer


# Analytics Views
# Set as GET only because who needs to update analytics?
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_analytics(request):
    """Get employee analytics data"""
    from attendance.models import Attendance
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    # Get date range from query params
    dept_data = Department.objects.annotate(
        employee_count=Count('employees')
    ).values('name', 'employee_count')

    # Get total and recent employee counts
    total_employees = Employee.objects.filter(is_active=True).count()
    recent_employees = Employee.objects.filter(
        date_joined__gte=datetime.now() - timedelta(days=30),
        is_active=True
    ).count()
    
    perf_data = Performance.objects.values('rating').annotate(
        count=Count('rating')
    ).order_by('rating')
    
    # Get daily attendance from the last 7 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    
    daily_attendance = Attendance.objects.filter(
        date__range=[start_date, end_date],
        status='present'
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Get status distribution from the last 7 days 
    status_distribution = Attendance.objects.filter(
        date__range=[start_date, end_date]
    ).values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    return Response({
        'total_employees': total_employees,
        'recent_joiners': recent_employees,
        'department_distribution': list(dept_data),
        'performance_distribution': list(perf_data),
        'daily_attendance': [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'count': item['count']
            } for item in daily_attendance
        ],
        'status_distribution': list(status_distribution),
    })


# Public API Test
@api_view(['GET'])
@permission_classes([AllowAny])
def public_stats(request):
    return Response({
        'message': 'Employee Management System Public API Active',
        'total_employees': Employee.objects.filter(is_active=True).count(),
        'total_departments': Department.objects.count(),
        'status': 'success',
        'authentication_required': 'Use /api/v1/auth/token/ to get JWT token'
    })

# Advanced employee indexing
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_search(request):
    query = request.GET.get('q', '')
    department_id = request.GET.get('department')
    is_active = request.GET.get('is_active')
    
    employees = Employee.objects.select_related('department').all()
    
    if query:
        employees = employees.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(employee_id__icontains=query)
        )
    
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    if is_active is not None:
        employees = employees.filter(is_active=is_active.lower() == 'true')
    
    serializer = EmployeeListSerializer(employees[:50], many=True)  # Limit results
    return Response(serializer.data)