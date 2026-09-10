from django.urls import path

from .views import InstitutionProfileAPIView


urlpatterns = [
    path('profile/', InstitutionProfileAPIView.as_view(), name='institution-profile'),
]
