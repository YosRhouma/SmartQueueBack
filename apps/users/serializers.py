from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
import json

User = get_user_model()


class CitizenProfileSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    dateOfBirth = serializers.DateField(source='date_of_birth')
    profilePicture = serializers.ImageField(source='profile_picture', required=False, allow_empty_file=False)
    Localisation = serializers.JSONField(write_only=True)

    class Meta:
        from .models import CitizenProfile
        model = CitizenProfile
        fields = (
            'firstName', 'lastName', 'phone', 'email', 'cin', 'dateOfBirth', 'gender',
            'profilePicture', 'Localisation',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['Localisation'] = {'governorate': instance.governorate, 'address': instance.address}
        return data

    def validate_Localisation(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError('Localisation must be valid JSON.')
        if not isinstance(value, dict):
            raise serializers.ValidationError('Localisation must be a JSON object.')
        required = {'governorate', 'address'}
        missing = required - value.keys()
        if missing:
            raise serializers.ValidationError(f"Missing fields: {', '.join(sorted(missing))}.")
        return value

    def create(self, validated_data):
        localisation = validated_data.pop('Localisation')
        validated_data['governorate'] = localisation['governorate']
        validated_data['address'] = localisation['address']
        return super().create(validated_data)

    def update(self, instance, validated_data):
        localisation = validated_data.pop('Localisation', None)
        if localisation:
            instance.governorate = localisation['governorate']
            instance.address = localisation['address']
        return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'role', 'date_joined'
        )
        read_only_fields = ('id', 'date_joined')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password',
            'role'
        )

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return email

    def validate(self, attrs):
        username = attrs.get('username', '').strip()
        email = attrs.get('email', '').strip()
        if username.lower() == email.lower():
            raise serializers.ValidationError({'username': 'Username and email must be different fields.'})
        attrs['username'] = username
        attrs['email'] = email.lower()
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(email__iexact=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': 'Invalid email or password.'})

        if not user.check_password(attrs['password']) or not user.is_active:
            raise serializers.ValidationError({'detail': 'Invalid email or password.'})

        refresh = RefreshToken.for_user(user)
        data = {}
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = UserSerializer(user).data
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, help_text='Refresh token to blacklist during logout.')

    def validate(self, attrs):
        try:
            refresh = RefreshToken(attrs['refresh'])
            refresh.blacklist()
        except TokenError:
            raise serializers.ValidationError('Invalid or expired refresh token.')
        except Exception:
            raise serializers.ValidationError('Unable to blacklist refresh token.')
        return attrs
