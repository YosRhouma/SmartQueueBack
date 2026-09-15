from django.urls import path

from .views import CurrentTicketAPIView, TicketCreateAPIView, TicketDetailAPIView, UserTicketsAPIView


urlpatterns = [
    # Citizen-only endpoints for reserving and tracking a virtual ticket.
    path('', TicketCreateAPIView.as_view(), name='ticket-create'),
    path('my-current/', CurrentTicketAPIView.as_view(), name='ticket-current'),
    path('my-tickets/', UserTicketsAPIView.as_view(), name='ticket-list'),
    path('<int:pk>/', TicketDetailAPIView.as_view(), name='ticket-detail'),
]
