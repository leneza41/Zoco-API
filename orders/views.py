from django.db.models import Q
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsAdminRole, is_admin
from .models import Order, OrderStatus
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    Pedidos. Reglas por rol:
      - Todos deben iniciar sesión.
      - Comprador: ve y crea sus pedidos; solo puede cancelarlos.
      - Vendedor: ve sus pedidos y los que incluyen sus productos; solo cambia el estado de estos últimos.
      - Admin: ve y administra todos.
    Editar o borrar un pedido completo es solo para admin.
    """

    queryset = Order.objects.all().prefetch_related('items').order_by('-created_at')
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_express', 'user']
    search_fields = ['customer_name', 'customer_phone', 'delivery_address', 'notes']
    ordering_fields = ['created_at', 'total_amount', 'status']
    pagination_class = None

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsAdminRole()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if is_admin(user):
            return qs
        if user.role == 'SELLER':
            return qs.filter(Q(user=user) | Q(items__product__seller=user)).distinct()
        return qs.filter(user=user)

    @action(detail=True, methods=['post', 'patch'], url_path='status')
    def change_status(self, request, pk=None):
        order = self.get_object()
        user = request.user
        new_status = request.data.get('status')

        if not new_status or new_status not in OrderStatus.values:
            return Response(
                {"error": f"Estado inválido. Opciones válidas: {list(OrderStatus.values)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        can_manage = is_admin(user) or (
            user.role == 'SELLER' and order.items.filter(product__seller=user).exists()
        )
        if not can_manage and new_status != OrderStatus.CANCELLED:
            return Response(
                {"detail": "Solo puedes cancelar tus pedidos."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not can_manage and order.user_id != user.id:
            return Response(
                {"detail": "No puedes modificar este pedido."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        return Response(OrderSerializer(order, context={'request': request}).data)
