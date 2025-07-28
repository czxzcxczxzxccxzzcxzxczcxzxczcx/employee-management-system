from django.contrib import admin
from django.urls import path, include, re_path
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

# Swagger / OpenAPI configuration
schema_view = get_schema_view(
   openapi.Info(
      title="Employee Management System API",
      default_version='v1',
      description="API documentation for Employee Management System",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@employeems.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# URL patterns for the project
urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # API URLs
    path('api/v1/', include('employees.urls')),
    path('api/v1/', include('attendance.urls')),
    
    # Authentication URLs  
    path('api/v1/auth/token/', csrf_exempt(TokenObtainPairView.as_view()), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', csrf_exempt(TokenRefreshView.as_view()), name='token_refresh'),
    
    # Swagger URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]