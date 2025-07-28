from rest_framework import serializers
from .models import Department, Employee, Performance

# Serializer for the Department model
class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'employee_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_employee_count(self, obj):
        return obj.employees.filter(is_active=True).count()

# Serializer for the Employee model
class EmployeeListSerializer(serializers.ModelSerializer):
    """Simplified serializer for employee list views"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'first_name', 'last_name',
            'email', 'department_name', 'position', 'is_active', 'date_joined'
        ]

# Serializer for employee detail views
class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for employee detail views"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    full_name = serializers.CharField(read_only=True)
    performance_count = serializers.SerializerMethodField()
    attendance_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone_number', 'address', 'department', 'department_name',
            'date_joined', 'position', 'salary', 'is_active',
            'performance_count', 'attendance_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'full_name']
    
    def get_performance_count(self, obj):
        return obj.performances.count()
    
    def get_attendance_count(self, obj):
        return obj.attendances.count()

# Serializer for creating and updating employees
class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating employees"""
    
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name', 'email', 'phone_number',
            'address', 'department', 'date_joined', 'position', 'salary', 'is_active'
        ]
    
    # Validates unique employee_id
    def validate_employee_id(self, value):
        instance = getattr(self, 'instance', None)
        if instance and instance.employee_id == value:
            return value
        
        if Employee.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("Employee ID already exists.")
        return value


# Serializer for the Performance model
class PerformanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    rating_display = serializers.CharField(source='get_rating_display', read_only=True)
    
    class Meta:
        model = Performance
        fields = [
            'id', 'employee', 'employee_name', 'employee_id',
            'rating', 'rating_display', 'review_date', 'comments',
            'reviewer', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

# Serializer for creating and updating performance records
class PerformanceCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating performance records"""
    
    class Meta:
        model = Performance
        fields = ['employee', 'rating', 'review_date', 'comments', 'reviewer']
    
    # Validates unique data
    def validate(self, data):
        instance = getattr(self, 'instance', None)
        employee = data.get('employee')
        review_date = data.get('review_date')
        
        if instance:
            # For updates
            existing = Performance.objects.filter(
                employee=employee, review_date=review_date
            ).exclude(id=instance.id)
        else:
            # For creation
            existing = Performance.objects.filter(
                employee=employee, review_date=review_date
            )
        
        if existing.exists():
            raise serializers.ValidationError(
                "Performance record already exists for this employee on this date."
            )
        
        return data