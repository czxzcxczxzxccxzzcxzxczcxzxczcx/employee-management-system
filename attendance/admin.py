from django.contrib import admin
from .models import Attendance

# Attendance admin
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'date', 'status', 'check_in_time',
        'check_out_time', 'hours_worked_display', 'created_at'
    ]
    list_filter = ['status', 'date', 'employee__department']
    search_fields = [
        'employee__first_name', 'employee__last_name',
        'employee__employee_id'
    ]
    ordering = ['-date', 'employee__last_name']
    date_hierarchy = 'date'
    list_editable = ['status']
    
    fieldsets = (
        ('Employee & Date', {
            'fields': ('employee', 'date', 'status')
        }),
        ('Time Tracking', {
            'fields': ('check_in_time', 'check_out_time')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )

    # Displays hours worked
    def hours_worked_display(self, obj):
        hours = obj.hours_worked
        if hours is not None:
            return f"{hours:.2f} hours"
        return "-"
    hours_worked_display.short_description = 'Hours Worked'