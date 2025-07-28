from django.shortcuts import render
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Attendance
from employees.models import Employee

from .serializers import (
    AttendanceSerializer,
    AttendanceCreateUpdateSerializer,
    AttendanceStatsSerializer
)

# Retrieves a list of all attendance records or create a new attendance record
class AttendanceListCreateView(generics.ListCreateAPIView):
    queryset = Attendance.objects.select_related('employee').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'status', 'date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date', 'employee__last_name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AttendanceCreateUpdateSerializer
        return AttendanceSerializer

# Retrieves, updates or deletes a specific attendance record
class AttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.select_related('employee').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AttendanceCreateUpdateSerializer
        return AttendanceSerializer

# Gets attendance analytics data
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_analytics(request):
    # Get date range from query params
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = timezone.now().date() - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Overall attendance stats
    total_records = Attendance.objects.filter(
        date__range=[start_date, end_date]
    ).count()
    
    status_distribution = Attendance.objects.filter(
        date__range=[start_date, end_date]
    ).values('status').annotate(count=Count('status'))
    
    # Daily attendance count
    daily_attendance = Attendance.objects.filter(
        date__range=[start_date, end_date],
        status='present'
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    return Response({
        'date_range': {
            'start_date': start_date,
            'end_date': end_date
        },
        'total_records': total_records,
        'status_distribution': list(status_distribution),
        'daily_attendance': list(daily_attendance),
    })

# Gets attendance statistics for a specific employee
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_attendance_stats(request, employee_id):    
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=404)
    
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = timezone.now().date() - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    attendances = Attendance.objects.filter(
        employee=employee,
        date__range=[start_date, end_date]
    )
    
    total_days = attendances.count()
    present_days = attendances.filter(status='present').count()
    absent_days = attendances.filter(status='absent').count()
    late_days = attendances.filter(status='late').count()
    half_days = attendances.filter(status='half_day').count()
    
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    stats = {
        'employee_id': employee.employee_id,
        'employee_name': employee.full_name,
        'date_range': {
            'start_date': start_date,
            'end_date': end_date
        },
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'late_days': late_days,
        'half_days': half_days,
        'attendance_percentage': round(attendance_percentage, 2)
    }
    
    return Response(stats)

# Gets attendance statistics for all employees
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bulk_attendance_stats(request):
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = timezone.now().date() - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    employees = Employee.objects.filter(is_active=True)
    stats_list = []
    
    for employee in employees:
        attendances = Attendance.objects.filter(
            employee=employee,
            date__range=[start_date, end_date]
        )
        
        total_days = attendances.count()
        present_days = attendances.filter(status='present').count()
        absent_days = attendances.filter(status='absent').count()
        late_days = attendances.filter(status='late').count()
        half_days = attendances.filter(status='half_day').count()
        
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
        
        stats_list.append({
            'employee_id': employee.employee_id,
            'employee_name': employee.full_name,
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'half_days': half_days,
            'attendance_percentage': round(attendance_percentage, 2)
        })
    
    return Response({
        'date_range': {
            'start_date': start_date,
            'end_date': end_date
        },
        'employee_stats': stats_list
    })