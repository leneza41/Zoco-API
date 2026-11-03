from rest_framework import serializers
from .models import Product, ProductCategory


class ProductSerializer(serializers.ModelSerializer):
    # Coerce price to float for direct Moshi/Kotlin Double deserialization
    price = serializers.FloatField()
    producerName = serializers.CharField(source='producer_name', required=True)
    isExpressDelivery = serializers.BooleanField(source='is_express_delivery', required=False, default=False)
    inStock = serializers.BooleanField(source='in_stock', required=False, default=True)
    category = serializers.CharField(required=False, default=ProductCategory.ALL)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    imageUrl = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'category',
            'producerName',
            'isExpressDelivery',
            'inStock',
            'imageUrl',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'imageUrl']

    def get_imageUrl(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def to_internal_value(self, data):
        # Support both camelCase and snake_case inputs seamlessly
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'producer_name' in data and 'producerName' not in data:
            data['producerName'] = data['producer_name']
        if 'is_express_delivery' in data and 'isExpressDelivery' not in data:
            data['isExpressDelivery'] = data['is_express_delivery']
        if 'in_stock' in data and 'inStock' not in data:
            data['inStock'] = data['in_stock']
        return super().to_internal_value(data)

    def validate_category(self, value):
        valid_cats = [choice[0] for choice in ProductCategory.choices]
        if value not in valid_cats:
            # Fallback to ALL if unknown category is sent
            return ProductCategory.ALL
        return value
