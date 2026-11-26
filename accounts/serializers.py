from rest_framework import serializers
from django.contrib.auth import authenticate
from zoco_api.serializers_mixins import SnakeCaseAliasMixin
from .models import User, UserProfile


class UserProfileSerializer(SnakeCaseAliasMixin, serializers.ModelSerializer):
    snake_case_aliases = {'photo_url': 'photoUrl'}

    photoUrl = serializers.CharField(source='photo_url', required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'role', 'photoUrl']


class UserSerializer(SnakeCaseAliasMixin, serializers.ModelSerializer):
    snake_case_aliases = {'preferred_language': 'preferredLanguage'}

    preferredLanguage = serializers.CharField(source='preferred_language', required=False)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone', 'address', 'preferredLanguage',
            'avatar', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'role', 'is_active', 'created_at', 'updated_at']


class AdminUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ['id', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        if 'role' in validated_data:
            instance.is_staff = validated_data['role'] == 'ADMIN'
        return super().update(instance, validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    preferredLanguage = serializers.CharField(source='preferred_language', required=False, default='es')
    role = serializers.CharField(required=False, default='BUYER')

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'first_name',
            'last_name', 'role', 'phone', 'address', 'preferredLanguage'
        ]
        read_only_fields = ['id']

    def validate_role(self, value):
        # El registro público solo crea compradores. Quien quiera vender usa /auth/become-seller;
        # los administradores los crea otro administrador o se hacen con createsuperuser.
        if value != 'BUYER':
            raise serializers.ValidationError("El registro público solo crea cuentas de comprador.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['role'] = 'BUYER'
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs.get('username'), password=attrs.get('password'))
        if not user:
            raise serializers.ValidationError({"detail": "Credenciales inválidas o usuario inactivo."})
        attrs['user'] = user
        return attrs
