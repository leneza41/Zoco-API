from django.db.models import Q
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order, OrderStatus
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related('items').order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_express', 'user']
    search_fields = ['customer_name', 'customer_phone', 'delivery_address', 'notes']
    ordering_fields = ['created_at', 'total_amount', 'status']
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'ADMIN' or user.is_staff:
                return qs
            if user.role == 'SELLER':
                return qs.filter(Q(user=user) | Q(items__product__seller=user)).distinct()
            if user.role == 'BUYER':
                return qs.filter(user=user)
        return qs

    @action(detail=True, methods=['post', 'patch'], url_path='status')
    def change_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if (
            request.user.is_authenticated
            and request.user.role == 'BUYER'
            and not request.user.is_staff
            and new_status != OrderStatus.CANCELLED
        ):
            return Response(
                {"detail": "Los compradores solo pueden cancelar sus pedidos."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not new_status or new_status not in OrderStatus.values:
            return Response(
                {"error": f"Estado inválido. Opciones válidas: {list(OrderStatus.values)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        return Response(OrderSerializer(order, context={'request': request}).data)
