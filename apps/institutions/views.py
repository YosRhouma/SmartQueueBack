from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.users.models import User
from .models import Institution
from .serializers import InstitutionProfileSerializer


INSTITUTION_PROFILE_FORM_PARAMETERS = [
    openapi.Parameter('officialName', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, default='SmartQueue Tunis'),
    openapi.Parameter('description', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, default='Queue management services.'),
    openapi.Parameter('logo', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False, description='Select an image file.'),
    openapi.Parameter('sector', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, default='Public service'),
    openapi.Parameter('website', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, default='https://example.com'),
    openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, default='contact@example.com'),
    openapi.Parameter('phone', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, default='+216 71 000 000'),
    openapi.Parameter('Localisation', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, default='{"governorate":"Tunis","address":"10 Avenue Habib Bourguiba","postalCode":"1000"}', description='JSON object.'),
    openapi.Parameter('Horaire', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, default='{"openingHours":"08:00:00","closingHours":"17:00:00","workingDays":["Monday","Tuesday","Wednesday","Thursday","Friday"],"isCurrentlyOpen":true}', description='JSON object.'),
]


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Institutions'],
    operation_description='Return the authenticated institution\'s complete organisation profile.',
    responses={200: InstitutionProfileSerializer, 404: 'Institution profile not found.'},
))
@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Institutions'],
    operation_description=(
        'Create an institution profile for the authenticated account. This endpoint requires '
        'the `institution` role. `Localisation` contains governorate, address and postalCode; '
        '`Horaire` contains openingHours, closingHours, workingDays and isCurrentlyOpen.'
    ),
    manual_parameters=INSTITUTION_PROFILE_FORM_PARAMETERS,
    responses={201: InstitutionProfileSerializer, 400: 'Profile already exists or invalid data.', 403: 'Institution role required.'},
))
@method_decorator(name='put', decorator=swagger_auto_schema(
    tags=['Institutions'], operation_description='Replace the authenticated institution profile.', manual_parameters=INSTITUTION_PROFILE_FORM_PARAMETERS,
))
@method_decorator(name='delete', decorator=swagger_auto_schema(
    tags=['Institutions'],
    operation_description='Delete the authenticated institution profile.',
    responses={204: 'Institution profile deleted.', 404: 'Institution profile not found.'},
))
class InstitutionProfileAPIView(generics.RetrieveDestroyAPIView, generics.CreateAPIView):
    serializer_class = InstitutionProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user.institution

    def get(self, request, *args, **kwargs):
        try:
            return self.retrieve(request, *args, **kwargs)
        except Institution.DoesNotExist:
            return Response({'detail': 'Institution profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        if request.user.role != User.Role.INSTITUTION:
            return Response({'detail': 'Only institution accounts can create an institution profile.'}, status=status.HTTP_403_FORBIDDEN)
        if Institution.objects.filter(owner=request.user).exists():
            return Response({'detail': 'Institution profile already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        try:
            profile = self.get_object()
        except Institution.DoesNotExist:
            return Response({'detail': 'Institution profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        try:
            self.get_object().delete()
        except Institution.DoesNotExist:
            return Response({'detail': 'Institution profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'detail': 'Institution profile deleted.'}, status=status.HTTP_200_OK)
