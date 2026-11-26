from rest_framework import serializers
from zoco_api.serializers_mixins import SnakeCaseAliasMixin
from .models import Product, ProductCategory


class ProductSerializer(SnakeCaseAliasMixin, serializers.ModelSerializer):
    snake_case_aliases = {
        'producer_name': 'producerName',
        'is_express_delivery': 'isExpressDelivery',
        'in_stock': 'inStock',
        'image_url': 'imageUrl',
    }

    # Coerce price to float for direct Moshi/Kotlin Double deserialization
    price = serializers.FloatField()
    producerName = serializers.CharField(source='producer_name', required=True)
    isExpressDelivery = serializers.BooleanField(source='is_express_delivery', required=False, default=False)
    inStock = serializers.BooleanField(source='in_stock', required=False, default=True)
    stock = serializers.IntegerField(required=False, default=10, min_value=0)
    category = serializers.CharField(required=False, default=ProductCategory.ALL)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    imageUrl = serializers.CharField(source='image_url', required=False, allow_null=True, allow_blank=True)
    sellerId = serializers.IntegerField(source='seller_id', read_only=True)
    sellerUsername = serializers.CharField(source='seller.username', read_only=True, default=None)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'category',
            'producerName',
            'sellerId',
            'sellerUsername',
            'isExpressDelivery',
            'inStock',
            'stock',
            'imageUrl',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'sellerId', 'sellerUsername', 'created_at', 'updated_at']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.image:
            request = self.context.get('request')
            ret['imageUrl'] = request.build_absolute_uri(instance.image.url) if request else instance.image.url
        elif not ret.get('imageUrl'):
            ret['imageUrl'] = None
        return ret

    def validate_imageUrl(self, value):
        # Solo se aceptan URLs web. Rutas locales del teléfono (content://, file://) no sirven a otros usuarios;
        # la foto se sube con POST /products/{id}/image.
        if value and not value.lower().startswith(('http://', 'https://')):
            return None
        return value

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
