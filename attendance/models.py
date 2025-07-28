from django.db import models
from employees.models import Employee

# Attendance tracking model
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def hours_worked(self):
        """Calculate hours worked if both check-in and check-out times are available"""
        if self.check_in_time and self.check_out_time:
            from datetime import datetime, timedelta
            check_in = datetime.combine(self.date, self.check_in_time)
            check_out = datetime.combine(self.date, self.check_out_time)
            
            # Handle when check out is next day
            if check_out < check_in:
                check_out += timedelta(days=1)
                
            duration = check_out - check_in
            return duration.total_seconds() / 3600  
        return None

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} ({self.get_status_display()})"

    class Meta:
        ordering = ['-date', 'employee__last_name']
        unique_together = ['employee', 'date']