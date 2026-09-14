from django.urls import path

from .views import InstitutionDetailAPIView, InstitutionListAPIView, InstitutionProfileAPIView


urlpatterns = [
    path('profile/', InstitutionProfileAPIView.as_view(), name='institution-profile'),
    # Public discovery endpoints used before a citizen reserves a ticket.
    path('', InstitutionListAPIView.as_view(), name='institution-list'),
    path('<int:pk>/', InstitutionDetailAPIView.as_view(), name='institution-detail'),
]
