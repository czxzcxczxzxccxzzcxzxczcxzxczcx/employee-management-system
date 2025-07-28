from rest_framework import serializers
from .models import Attendance
from employees.models import Employee


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    hours_worked = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'employee_id',
            'date', 'status', 'status_display', 'check_in_time',
            'check_out_time', 'hours_worked', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_hours_worked(self, obj):
        return obj.hours_worked


class AttendanceCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating attendance records"""
    
    class Meta:
        model = Attendance
        fields = [
            'employee', 'date', 'status', 'check_in_time',
            'check_out_time', 'notes'
        ]
    
    def validate(self, data):
        """Validate attendance data"""
        instance = getattr(self, 'instance', None)
        employee = data.get('employee')
        date = data.get('date')
        check_in_time = data.get('check_in_time')
        check_out_time = data.get('check_out_time')
        status = data.get('status')
        
        # Check for duplicate attendance record
        if instance:
            existing = Attendance.objects.filter(
                employee=employee, date=date
            ).exclude(id=instance.id)
        else:
            existing = Attendance.objects.filter(employee=employee, date=date)
        
        if existing.exists():
            raise serializers.ValidationError(
                "Attendance record already exists for this employee on this date."
            )
        
        # Validate time logic
        if check_in_time and check_out_time:
            if check_out_time <= check_in_time:
                # Allow next day checkout (night shift)
                pass
        
        # If status is present, require check-in time
        if status == 'present' and not check_in_time:
            raise serializers.ValidationError(
                "Check-in time is required for present status."
            )
        
        return data


class AttendanceStatsSerializer(serializers.Serializer):
    """Serializer for attendance statistics"""
    employee_id = serializers.CharField()
    employee_name = serializers.CharField()
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    late_days = serializers.IntegerField()
    half_days = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()