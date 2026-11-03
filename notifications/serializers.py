from rest_framework import serializers
from .models import Notification, NotificationType


class NotificationSerializer(serializers.ModelSerializer):
    isRead = serializers.BooleanField(source='is_read', required=False, default=False)
    timestamp = serializers.SerializerMethodField(read_only=True)
    userId = serializers.PrimaryKeyRelatedField(source='user', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'userId', 'title', 'message', 'type', 'isRead', 'timestamp', 'created_at']
        read_only_fields = ['id', 'userId', 'timestamp', 'created_at']

    def get_timestamp(self, obj):
        return int(obj.created_at.timestamp() * 1000)

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'is_read' in data and 'isRead' not in data:
            data['isRead'] = data['is_read']
        return super().to_internal_value(data)
