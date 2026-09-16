"""
URL configuration for config project.
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import permissions
from apps.tickets.views import CallNextTicketAPIView, InstitutionQueueAPIView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title='SmartQueue API',
        default_version='v1',
        description=(
            'SmartQueue REST API. Endpoints are grouped in Swagger as **Authentication**, '
            '**Citizens**, and **Institutions**. First create an account through Authentication, '
            'then use its JWT access token to create and manage the role-specific profile.'
        ),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/institutions/', include('apps.institutions.urls')),
    path('api/tickets/', include('apps.tickets.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    # A queue belongs directly to an institution, not to a service.
    path('api/institutions/<int:pk>/queue/', InstitutionQueueAPIView.as_view(), name='institution-queue'),
    path('api/institutions/queue/next/', CallNextTicketAPIView.as_view(), name='institution-queue-next'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
