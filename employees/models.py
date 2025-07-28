from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser

# Department model
class Department(models.Model):
    """
    Department data model
    
    Example data:
        name: "Engineering", "Human Resources", "Marketing"
        description: "Responsible for software development"
        created_at: 2025-01-15 10:30:00+00:00
        updated_at: 2025-01-20 14:45:00+00:00
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Employee(models.Model):
    """
    Employee data model 
    
    Example data:
        first_name: "John"
        last_name: "Doe"
        email: "john.doe@company.com"
        phone_number: "+1234567890"
        address: "123 Main St"
        department: Department object
        date_joined: 2024-03-15
        employee_id: "EMP001"
        salary: 75000.00
        position: "Senior Software Developer"
        is_active: True
        created_at: 2024-03-15 09:00:00+00:00
        updated_at: 2025-01-20 16:30:00+00:00
    """
    
    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    
    # Phone number with validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17,
        help_text="Examples: '+1234567890', '1234567890', '+44123456789'"
    )
    
    # Address
    address = models.TextField()
    
    # Work Information
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name='employees',
        help_text="Employee's assigned department"
    )
    date_joined = models.DateField(help_text="Format: YYYY-MM-DD (e.g., 2024-03-15)")
    employee_id = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Unique identifier like 'EMP001', 'EMP002', etc."
    )
    
    # Optional fields
    salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Annual salary in USD (e.g., 75000.00)"
    )
    position = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Job title like 'Senior Software Developer', 'Marketing Manager'"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="False if employee has left the company"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"

    class Meta:
        ordering = ['last_name', 'first_name']

# Performance model
class Performance(models.Model):
    """
    Performance data model
    
    Example data:
        employee: Employee object
        rating: 4 (Good)
        review_date: 2025-01-15
        comments: "Excellent technical skills"
        reviewer: "Jane Smith (Manager)"
        created_at: 2025-01-15 14:30:00+00:00
        updated_at: 2025-01-15 14:30:00+00:00
    """
    
    RATING_CHOICES = [
        (1, 'Poor'),        
        (2, 'Below Average'), 
        (3, 'Average'),       
        (4, 'Good'),         
        (5, 'Excellent'),      
    ]
    
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='performances',
        help_text="Employee being reviewed"
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        help_text="Performance rating from 1 (Poor) to 5 (Excellent)"
    )
    review_date = models.DateField(help_text="Date of performance review")
    comments = models.TextField(
        blank=True,
        help_text="Detailed feedback and comments about performance"
    )
    reviewer = models.CharField(
        max_length=100,
        help_text="Name and title of the person conducting the review"
    )  
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_rating_display()} ({self.review_date})"

    class Meta:
        ordering = ['-review_date']
        unique_together = ['employee', 'review_date']