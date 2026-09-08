"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title='SmartQueue API',
        default_version='v1',
        description=(
            'SmartQueue REST API for citizen authentication, institutional services, '
            'ticket management and notifications. '
            'Use the /api/auth/register/ endpoint to create an account, '
            '/api/auth/login/ to obtain JWT tokens, /api/auth/refresh/ to rotate tokens, '
            '/api/auth/logout/ to blacklist the refresh token, and /api/auth/me/ to retrieve '
            'the authenticated user profile.'
        ),
        terms_of_service='https://example.com/terms/',
        contact=openapi.Contact(email='support@smartqueue.local'),
        license=openapi.License(name='MIT License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
