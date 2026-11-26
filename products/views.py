from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsSellerOrAdmin, IsProductOwnerOrAdmin
from .models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter


class ProductViewSet(viewsets.ModelViewSet):
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
