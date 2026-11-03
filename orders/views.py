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
        # If user is authenticated and not staff, can see own orders or orders where user is seller
        user = self.request.user
        if user.is_authenticated and not user.is_staff and user.role == 'BUYER':
            return qs.filter(user=user)
        return qs

    @action(detail=True, methods=['post', 'patch'], url_path='status')
    def change_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if not new_status or new_status not in OrderStatus.values:
            return Response(
                {"error": f"Estado inválido. Opciones válidas: {list(OrderStatus.values)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        return Response(OrderSerializer(order, context={'request': request}).data)
