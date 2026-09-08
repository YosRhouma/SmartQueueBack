from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .auth_docs import OPENAPI_AUTH_DESCRIPTION
from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer, UserSerializer

User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description=OPENAPI_AUTH_DESCRIPTION,
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
        operation_description='Authenticate with username/password and return JWT access and refresh tokens.',
        request_body=LoginSerializer,
        responses={200: openapi.Response('OK')}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
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
        operation_description='Return the currently authenticated user profile.',
        responses={200: openapi.Response('OK', UserSerializer)}
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
