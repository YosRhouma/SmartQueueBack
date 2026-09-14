from django.urls import path

from .views import CurrentTicketAPIView, TicketCreateAPIView, TicketDetailAPIView


urlpatterns = [
    # Citizen-only endpoints for reserving and tracking a virtual ticket.
    path('', TicketCreateAPIView.as_view(), name='ticket-create'),
    path('my-current/', CurrentTicketAPIView.as_view(), name='ticket-current'),
    path('<int:pk>/', TicketDetailAPIView.as_view(), name='ticket-detail'),
]
