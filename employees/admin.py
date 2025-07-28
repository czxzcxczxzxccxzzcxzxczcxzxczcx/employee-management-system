from django.contrib import admin
from .models import Department, Employee, Performance

# Department admin
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'employee_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    # Counts active employees in the department
    def employee_count(self, obj):
        return obj.employees.filter(is_active=True).count()
    employee_count.short_description = 'Active Employees'


# Employee admin
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'email', 'department','position', 'is_active', 'date_joined']
    list_filter = ['department', 'is_active', 'date_joined', 'position']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id']
    list_editable = ['is_active']
    ordering = ['last_name', 'first_name']
    date_hierarchy = 'date_joined'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address')
        }),
        ('Work Information', {
            'fields': ('employee_id', 'department', 'position', 'date_joined', 'salary')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    # Returns full name
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'


# Performance admin
@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'rating', 'review_date', 'reviewer', 'created_at']
    list_filter = ['rating', 'review_date', 'reviewer']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering = ['-review_date']
    date_hierarchy = 'review_date'
    
    fieldsets = (
        ('Review Information', {
            'fields': ('employee', 'rating', 'review_date', 'reviewer')
        }),
        ('Comments', {
            'fields': ('comments',)
        }),
    )