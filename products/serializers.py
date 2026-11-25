from rest_framework import serializers
from .models import Product, ProductCategory


class ProductSerializer(serializers.ModelSerializer):
    # Coerce price to float for direct Moshi/Kotlin Double deserialization
    price = serializers.FloatField()
    producerName = serializers.CharField(source='producer_name', required=True)
    isExpressDelivery = serializers.BooleanField(source='is_express_delivery', required=False, default=False)
    inStock = serializers.BooleanField(source='in_stock', required=False, default=True)
    stock = serializers.IntegerField(required=False, default=10, min_value=0)
    category = serializers.CharField(required=False, default=ProductCategory.ALL)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    imageUrl = serializers.CharField(source='image_url', required=False, allow_null=True, allow_blank=True)

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
            'stock',
            'imageUrl',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if not ret.get('imageUrl') and instance.image:
            request = self.context.get('request')
            ret['imageUrl'] = request.build_absolute_uri(instance.image.url) if request else instance.image.url
        elif ret.get('imageUrl') == "":
            ret['imageUrl'] = None
        return ret

    def to_internal_value(self, data):
        # Support both camelCase and snake_case inputs seamlessly
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'producer_name' in data and 'producerName' not in data:
            data['producerName'] = data['producer_name']
        if 'is_express_delivery' in data and 'isExpressDelivery' not in data:
            data['isExpressDelivery'] = data['is_express_delivery']
        if 'in_stock' in data and 'inStock' not in data:
            data['inStock'] = data['in_stock']
        if 'image_url' in data and 'imageUrl' not in data:
            data['imageUrl'] = data['image_url']
        return super().to_internal_value(data)

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value

    def validate_category(self, value):
        valid_cats = [choice[0] for choice in ProductCategory.choices]
        if value not in valid_cats:
            # Fallback to ALL if unknown category is sent
            return ProductCategory.ALL
        return value
