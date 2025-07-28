from django.shortcuts import render
from django.http import HttpResponse
from employees.models import Employee, Department

# Serves the dashboard template with data
def dashboard_view(request):
    # Get data from the database
    total_employees = Employee.objects.count()
    total_departments = Department.objects.count()
    recent_employees = Employee.objects.filter(
        date_joined__gte='2025-06-26'  # Last 30 days
    ).count()
    
    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'recent_employees': recent_employees,
        'server_message': 'Hello from Django server! 🖥️',
        'current_time': '2025-07-26 12:15:00'  # Could use timezone.now()
    }
    
    return render(request, 'dashboard.html', context)