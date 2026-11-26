from rest_framework import generics, status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from zoco_api.uploads import ImageUploadSerializer
from rest_framework.authtoken.models import Token
from .models import User, UserProfile
from .permissions import IsAdminRole, IsAdminOrReadOnly
from .serializers import (
    UserSerializer,
    AdminUserSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    LoginSerializer,
)


class RegisterView(generics.CreateAPIView):
    """
    Registro público. Siempre crea una cuenta de COMPRADOR (ver RegisterSerializer).
    Quien quiera vender usa después /auth/become-seller; los administradores no se registran.
    """
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
    """
    Inicio de sesión: devuelve el token y los datos del usuario (incluido su rol).
    No crea cuentas: si el usuario no existe, responde 400.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
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
    """
    Cierra la sesión borrando el token del usuario.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        return Response({"message": "Sesión cerrada exitosamente."}, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Datos de la cuenta del usuario que hace la petición (GET/PUT/PATCH en /auth/me).
    El usuario no puede cambiar su propio rol aquí.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AvatarView(APIView):
    """Sube la foto de perfil del usuario autenticado (multipart, campo 'image')."""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded = ImageUploadSerializer(data=request.data)
        uploaded.is_valid(raise_exception=True)
        user = request.user
        if user.avatar:
            user.avatar.delete(save=False)
        user.avatar = uploaded.validated_data['image']
        user.save()
        return Response({
            "user": UserSerializer(user, context={'request': request}).data,
            "message": "Foto de perfil actualizada."
        }, status=status.HTTP_200_OK)


class BecomeSellerView(APIView):
    """
    Un comprador pide ser vendedor. Los administradores no pueden usarlo (recibirían 403).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role == 'ADMIN' or user.is_staff:
            return Response(
                {"detail": "Los administradores no pueden cambiar a vendedor."},
                status=status.HTTP_403_FORBIDDEN,
            )
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
    """
    Gestión de usuarios y roles. SOLO administradores.
    """
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
    """
    Perfil general de la comunidad (un solo registro). Lo puede leer cualquier usuario con sesión; solo un administrador lo modifica.
    """
    permission_classes = [IsAdminOrReadOnly]

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
