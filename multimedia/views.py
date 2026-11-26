from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsSellerOrAdmin, IsMediaOwnerOrAdmin, is_admin
from .models import Media
from .serializers import MediaSerializer


class MediaViewSet(viewsets.ModelViewSet):
    """
    Archivos multimedia de productos. Ver: cualquiera. Agregar, editar o borrar: el vendedor dueño del producto o un administrador.
    """
    queryset = Media.objects.all().order_by('-created_at')
    serializer_class = MediaSerializer
    permission_classes = [IsSellerOrAdmin, IsMediaOwnerOrAdmin]  # lectura pública; escritura vendedor dueño o admin
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'media_type']
    search_fields = ['description', 'media_uri']
    ordering_fields = ['created_at']
    pagination_class = None

    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data.get('product')
        if not is_admin(user) and (product is None or product.seller_id != user.id):
            raise PermissionDenied("Solo puedes agregar archivos a tus propios productos.")
        serializer.save()
