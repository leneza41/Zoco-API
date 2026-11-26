from rest_framework import generics, status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import User, UserProfile
from .permissions import IsAdminRole
from .serializers import (
    UserSerializer,
    AdminUserSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    LoginSerializer,
)
from .utils import DEFAULT_USERNAMES, ensure_default_users


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user, context=self.get_serializer_context()).data
        return Response({
            "token": token.key,
            "user": user_data,
            "message": "Usuario registrado exitosamente."
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        if username in DEFAULT_USERNAMES and not User.objects.filter(username=username).exists():
            ensure_default_users()

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user, context={'request': request}).data
        return Response({
            "token": token.key,
            "user": user_data,
            "message": "Inicio de sesión exitoso."
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        return Response({"message": "Sesión cerrada exitosamente."}, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class BecomeSellerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        user.role = 'SELLER'
        producer_name = (request.data.get('producerName') or request.data.get('first_name') or '').strip()
        if producer_name and not (user.first_name or '').strip():
            user.first_name = producer_name
        user.save()
        return Response({
            "user": UserSerializer(user, context={'request': request}).data,
            "message": "Ahora eres vendedor en Zoco."
        }, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    http_method_names = ['get', 'patch', 'put', 'post', 'head', 'options']

    @action(
        detail=True,
        methods=['post', 'patch'],
        url_path='role',
        permission_classes=[permissions.IsAuthenticated, IsAdminRole],
    )
    def change_role(self, request, pk=None):
        user = self.get_object()
        new_role = request.data.get('role')
        if new_role not in ('BUYER', 'SELLER', 'ADMIN'):
            return Response(
                {"error": "Rol inválido. Opciones válidas: BUYER, SELLER, ADMIN."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.role = new_role
        user.is_staff = (new_role == 'ADMIN')
        user.save(update_fields=['role', 'is_staff', 'updated_at'])
        return Response(
            UserSerializer(user, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


class UserProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(id=1)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(id=1)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        return self.put(request)
