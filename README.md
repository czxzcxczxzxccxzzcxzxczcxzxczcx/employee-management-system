Employee Management System

This is a Employee Management System made using Djangos REST Framework. This application allows for viewing and modifying employee, attendance, performance, and analytical data. This system has real-time data updating with a REST API

- Working CRUD operations for modifying employee data
- Daily attendance is tracked
- Real time charts and stats using Chart.js
- JWT authentication system
- REST API with Swagger UI

Backend: Django & Django REST framework
Database: PostgreSQL
Auth: JWT
Documentation: Swagger & OpenAPI
Frontend: HTML, CSS, JavaScript
Deployment: Docker, Render
Modules: Uses Fakes to generate data

How to Install and Setup

1) Clone the Repository
```bash
git clone https://github.com/czxzcxczxzxccxzzcxzxczcxzxczcx/employee-management-system.git
cd employee-management-system
```

3) Create a virtual environment  
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4) Install required dependencies 
```bash
pip install -r requirements.txt
```

5) Create the environment variables 
```bash
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_NAME=employee_db
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

6) Start the docker database  
```bash
docker-compose up --build
```

5) Set up the database  
```bash
python manage.py migrate

python manage.py createsuperuser

python manage.py seed_data --employees 20
```

6) Then run the server 
```bash
python manage.py runserver
```

You can also set up on render by doing this

1) Clone or Fork the repo onto your github account and sign into render

2) Then create a Web Service and connect the repo

3) Next in the settings make the build command  
```bash
./build.sh
```

4) Then make set the environment variables to the database

5) you can host the database wherever you want, for this I chose render to host it.

6) Input your environment variables on render  
```bash
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_NAME=your_render_db_name
DATABASE_USER=your_render_db_user
DATABASE_PASSWORD=your_render_db_password
DATABASE_HOST=your_render_db_host
DATABASE_PORT=5432
```

6) Make sure the settings.py file in the repo allows connections from the render domain

7) If the database is properly running you should be able to load the application on render

8) to test make sure you set a superuser and seed the data 
```bash
python manage.py seed_data --employees 20
```

I have a live demo hosted here: https://employee-management-system-x2ef.onrender.com/
