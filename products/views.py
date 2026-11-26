from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from zoco_api.uploads import ImageUploadSerializer
from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsSellerOrAdmin, IsProductOwnerOrAdmin
from .models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter


class ProductViewSet(viewsets.ModelViewSet):
    """
    Catálogo de productos.
     - Ver: cualquiera (también sin sesión).
     - Crear: vendedores y administradores.
     - Editar, borrar y subir foto: el vendedor dueño del producto o un administrador.
    """
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'producer_name']
    ordering_fields = ['price', 'created_at', 'name']
    # Disable pagination on products list so Android Retrofit receives List<ProductDto>
    pagination_class = None

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsSellerOrAdmin()]
        return [permissions.IsAuthenticated(), IsProductOwnerOrAdmin()]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    @action(detail=True, methods=['post'], url_path='image', parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        """Sube la fotografía del producto (multipart, campo 'image'). Solo el vendedor dueño o un admin."""
        product = self.get_object()  # aplica IsProductOwnerOrAdmin
        uploaded = ImageUploadSerializer(data=request.data)
        uploaded.is_valid(raise_exception=True)
        if product.image:
            product.image.delete(save=False)
        product.image = uploaded.validated_data['image']
        product.image_url = None
        product.save()
        return Response(self.get_serializer(product).data)
