from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .auth_docs import OPENAPI_AUTH_DESCRIPTION
from .serializers import CitizenProfileSerializer, RegisterSerializer, LoginSerializer, LogoutSerializer, UserSerializer
from .models import CitizenProfile

User = get_user_model()

CITIZEN_PROFILE_FORM_PARAMETERS = [
    openapi.Parameter('firstName', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, default='foulen'),
    openapi.Parameter('lastName', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, default='Ben foulen'),
    openapi.Parameter('phone', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, default='+216 22 222 222'),
    openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, default='foulen.benfoulen@example.com'),
    openapi.Parameter('cin', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, default='12345678'),
    openapi.Parameter('dateOfBirth', openapi.IN_FORM, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, required=True, default='1998-05-14'),
    openapi.Parameter('gender', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, default='male'),
    openapi.Parameter('profilePicture', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False, description='Select an image file.'),
    openapi.Parameter('Localisation', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True, default='{"governorate":"Tunis","address":"10 Avenue Habib Bourguiba, Tunis"}', description='JSON object.'),
]


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=['Authentication'],
        request_body=RegisterSerializer,
        responses={201: openapi.Response('Created', UserSerializer)}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_description='Authenticate with username/password and return JWT access and refresh tokens.',
        request_body=LoginSerializer,
        responses={200: openapi.Response('OK')}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenRefreshAPIView(TokenRefreshView):
    """Keep the refresh endpoint in the Authentication section of Swagger."""

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_description='Exchange a valid refresh token for a new access token.',
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_description='Blacklist the refresh token used for logout. Send Authorization: Bearer <access_token> and refresh in the body.',
        request_body=LogoutSerializer,
        responses={200: openapi.Response('OK')}
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'detail': 'Logout successful.'}, status=status.HTTP_200_OK)


class MeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_description='Return the currently authenticated user profile.',
        responses={200: openapi.Response('OK', UserSerializer)}
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Citizens'],
    operation_description='Return the authenticated citizen\'s personal profile.',
    responses={200: CitizenProfileSerializer, 404: 'Citizen profile not found.'},
    security=[{'Bearer': []}],
))
@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Citizens'],
    operation_description=(
        'Create the authenticated citizen\'s profile. This endpoint is available only to '
        'accounts with the `citizen` role. `Localisation` must contain `governorate` and `address`.'
    ),
    manual_parameters=CITIZEN_PROFILE_FORM_PARAMETERS,
    responses={201: CitizenProfileSerializer, 400: 'Profile already exists or invalid data.', 403: 'Citizen role required.'},
    security=[{'Bearer': []}],
))
@method_decorator(name='put', decorator=swagger_auto_schema(
    tags=['Citizens'], operation_description='Replace the authenticated citizen\'s profile.', manual_parameters=CITIZEN_PROFILE_FORM_PARAMETERS,
    security=[{'Bearer': []}],
))
@method_decorator(name='delete', decorator=swagger_auto_schema(
    tags=['Citizens'],
    operation_description='Delete the authenticated citizen\'s personal profile.',
    responses={204: 'Citizen profile deleted.', 404: 'Citizen profile not found.'},
    security=[{'Bearer': []}],
))
class CitizenProfileAPIView(generics.RetrieveDestroyAPIView, generics.CreateAPIView):
    serializer_class = CitizenProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user.citizen_profile

    def get(self, request, *args, **kwargs):
        try:
            return self.retrieve(request, *args, **kwargs)
        except CitizenProfile.DoesNotExist:
            return Response({'detail': 'Citizen profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        if request.user.role != User.Role.CITIZEN:
            return Response({'detail': 'Only citizen accounts can create a citizen profile.'}, status=status.HTTP_403_FORBIDDEN)
        if CitizenProfile.objects.filter(user=request.user).exists():
            return Response({'detail': 'Citizen profile already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        try:
            profile = self.get_object()
        except CitizenProfile.DoesNotExist:
            return Response({'detail': 'Citizen profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        try:
            self.get_object().delete()
        except CitizenProfile.DoesNotExist:
            return Response({'detail': 'Citizen profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'detail': 'Citizen profile deleted.'}, status=status.HTTP_200_OK)
