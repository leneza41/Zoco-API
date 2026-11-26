from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsAdminOrReadOnly, is_admin
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """
    Notificaciones. Cada usuario solo ve las suyas; solo un administrador puede crearlas, editarlas o borrarlas.
    """
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    permission_classes = [IsAdminOrReadOnly]  # cada usuario lee las suyas; solo admin crea/edita/borra
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_read', 'type', 'user']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at']
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if is_admin(user):
            return qs
        return qs.filter(user=user)

    @action(detail=True, methods=['post', 'patch'], url_path='read', permission_classes=[permissions.IsAuthenticated])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post'], url_path='mark-all-read', permission_classes=[permissions.IsAuthenticated])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"message": "Todas las notificaciones han sido marcadas como leídas."})
