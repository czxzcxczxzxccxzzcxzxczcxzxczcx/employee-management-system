from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
import random
from datetime import datetime, timedelta, date
from employees.models import Department, Employee, Performance
from attendance.models import Attendance


class Command(BaseCommand):
    help = 'Seed the database with fake employee data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--employees',
            type=int,
            default=50,
            help='Number of employees to create (default: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        fake = Faker()
        num_employees = options['employees']
        
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Attendance.objects.all().delete()
            Performance.objects.all().delete()
            Employee.objects.all().delete()
            Department.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        try:
            with transaction.atomic():
                # Creates departments
                self.stdout.write('Creating departments...')
                departments = self.create_departments(fake)
                
                # Creates employees
                self.stdout.write(f'Creating {num_employees} employees...')
                employees = self.create_employees(fake, departments, num_employees)
                
                # Creates performance records
                self.stdout.write('Creating performance records...')
                self.create_performance_records(fake, employees)
                
                # Creates attendance records
                self.stdout.write('Creating attendance records...')
                self.create_attendance_records(fake, employees)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully seeded database with:\n'
                        f'- {len(departments)} departments\n'
                        f'- {len(employees)} employees\n'
                        f'- Performance records for all employees\n'
                        f'- Attendance records for the last 60 days'
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error seeding database: {str(e)}')
            )

    def create_departments(self, fake):
        dept_names = [
            'Human Resources', 'Information Technology', 'Finance',
            'Marketing', 'Sales', 'Operations', 'Customer Service',
            'Research & Development', 'Legal', 'Administration'
        ]
        
        departments = []
        for name in dept_names:
            dept, created = Department.objects.get_or_create(
                name=name,
                defaults={'description': fake.text(max_nb_chars=200)}
            )
            departments.append(dept)
        
        return departments

    def create_employees(self, fake, departments, num_employees):
        positions = [
            'Software Engineer', 'Senior Developer', 'Team Lead', 'Manager',
            'Analyst', 'Coordinator', 'Specialist', 'Assistant', 'Director',
            'Consultant', 'Associate', 'Executive', 'Supervisor'
        ]
        
        employees = []
        for i in range(num_employees):
            # Generates employee ID
            employee_id = f"EMP{str(i+1).zfill(4)}"
            
            # Checks unique email
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@company.com"
            
            # Checks if email exists
            counter = 1
            original_email = email
            while Employee.objects.filter(email=email).exists():
                email = f"{original_email.split('@')[0]}{counter}@company.com"
                counter += 1
            
            employee = Employee.objects.create(
                employee_id=employee_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=fake.phone_number()[:15], 
                address=fake.address(),
                department=random.choice(departments),
                date_joined=fake.date_between(start_date='-2y', end_date='today'),
                position=random.choice(positions),
                salary=fake.pydecimal(left_digits=6, right_digits=2, positive=True),
                is_active=random.choice([True, True, True, False]) 
            )
            employees.append(employee)
        
        return employees

    def create_performance_records(self, fake, employees):
        for employee in employees:
            if not employee.is_active:
                continue
                
            # Create 1-3 performance records per employee
            num_records = random.randint(1, 3)
            
            for _ in range(num_records):
                # Generate random review date in the past year
                review_date = fake.date_between(start_date='-1y', end_date='today')
                
                # Check if performance record already exists for this date
                if Performance.objects.filter(employee=employee, review_date=review_date).exists():
                    continue
                
                Performance.objects.create(
                    employee=employee,
                    rating=random.randint(1, 5),
                    review_date=review_date,
                    comments=fake.text(max_nb_chars=300),
                    reviewer=fake.name()
                )

    def create_attendance_records(self, fake, employees):
        """Create attendance records for the last 60 days"""
        end_date = date.today()
        start_date = end_date - timedelta(days=60)
        
        current_date = start_date
        while current_date <= end_date:
            # Skip weekends for most employees
            # Monday = 0, Sunday = 6
            if current_date.weekday() < 5:  
                for employee in employees:
                    if not employee.is_active:
                        continue
                    
                    # Skip some days randomly 
                    if random.random() < 0.05:  
                        continue
                    
                    # checks if the current date is before the employee's join date
                    if current_date < employee.date_joined:
                        continue
                    
                    # Check if attendance record already exists
                    if Attendance.objects.filter(employee=employee, date=current_date).exists():
                        continue
                    
                    # Determine status with weights
                    status_choices = ['present', 'absent', 'late', 'half_day']
                    status_weights = [0.85, 0.05, 0.08, 0.02] 
                    status = random.choices(status_choices, weights=status_weights)[0]
                    
                    # Generate times based on status
                    check_in_time = None
                    check_out_time = None
                    
                    if status in ['present', 'late', 'half_day']:
                        # Generate check-in time
                        if status == 'late':
                            # Late arrival
                            check_in_hour = random.randint(9, 11)  
                        else:
                            # Normal arrival
                            check_in_hour = random.randint(8, 9)  
                        
                        check_in_minute = random.randint(0, 59)
                        check_in_time = datetime.strptime(
                            f"{check_in_hour:02d}:{check_in_minute:02d}", "%H:%M"
                        ).time()
                        
                        # Generate check-out time
                        if status == 'half_day':
                            # Half day
                            checkout_hour = random.randint(13, 15)  
                        else:
                            # Full day
                            checkout_hour = random.randint(17, 19)  
                        
                        checkout_minute = random.randint(0, 59)
                        check_out_time = datetime.strptime(
                            f"{checkout_hour:02d}:{checkout_minute:02d}", "%H:%M"
                        ).time()
                    
                    Attendance.objects.create(
                        employee=employee,
                        date=current_date,
                        status=status,
                        check_in_time=check_in_time,
                        check_out_time=check_out_time,
                        notes=fake.sentence() if random.random() < 0.2 else ''  
                    )
            
            current_date += timedelta(days=1)
