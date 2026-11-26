from rest_framework import serializers
from .models import Media, MediaType
from products.models import Product
from zoco_api.serializers_mixins import SnakeCaseAliasMixin


class MediaSerializer(SnakeCaseAliasMixin, serializers.ModelSerializer):
    snake_case_aliases = {
        'product_id': 'productId',
        'media_type': 'mediaType',
        'media_uri': 'mediaUri',
        'uri': 'mediaUri',
    }

    productId = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        required=False,
        allow_null=True
    )
    mediaType = serializers.CharField(source='media_type', required=False, default=MediaType.IMAGE)
    uri = serializers.SerializerMethodField(read_only=True)
    mediaUri = serializers.CharField(source='media_uri', required=False, allow_blank=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Media
        fields = ['id', 'productId', 'file', 'uri', 'mediaUri', 'mediaType', 'description', 'createdAt']
        read_only_fields = ['id', 'uri', 'createdAt']

    def get_uri(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return obj.media_uri or ""

