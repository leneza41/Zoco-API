from rest_framework import serializers
from .models import Media, MediaType
from products.models import Product


class MediaSerializer(serializers.ModelSerializer):
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

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'product_id' in data and 'productId' not in data:
            data['productId'] = data['product_id']
        if 'media_type' in data and 'mediaType' not in data:
            data['mediaType'] = data['media_type']
        if 'media_uri' in data and 'mediaUri' not in data:
            data['mediaUri'] = data['media_uri']
        if 'uri' in data and 'mediaUri' not in data:
            data['mediaUri'] = data['uri']
        return super().to_internal_value(data)
