from rest_framework import serializers
from decimal import Decimal
from .models import Order, OrderItem, OrderStatus
from products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    productId = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        required=False,
        allow_null=True
    )
    productName = serializers.CharField(source='product_name', required=False)
    unitPrice = serializers.FloatField(source='unit_price', required=False)
    subtotal = serializers.FloatField(required=False)

    class Meta:
        model = OrderItem
        fields = ['id', 'productId', 'productName', 'quantity', 'unitPrice', 'subtotal']

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'product_id' in data and 'productId' not in data:
            data['productId'] = data['product_id']
        if 'product_name' in data and 'productName' not in data:
            data['productName'] = data['product_name']
        if 'unit_price' in data and 'unitPrice' not in data:
            data['unitPrice'] = data['unit_price']
        return super().to_internal_value(data)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)
    scheduledTime = serializers.CharField(source='scheduled_time', required=False, allow_blank=True, default="")
    totalAmount = serializers.FloatField(source='total_amount', required=False)
    customerName = serializers.CharField(source='customer_name', required=False, allow_blank=True, default="")
    customerPhone = serializers.CharField(source='customer_phone', required=False, allow_blank=True, default="")
    deliveryAddress = serializers.CharField(source='delivery_address', required=False, allow_blank=True, default="")
    isExpress = serializers.BooleanField(source='is_express', required=False, default=False)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    userId = serializers.PrimaryKeyRelatedField(source='user', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'userId', 'customerName', 'customerPhone', 'deliveryAddress',
            'scheduledTime', 'totalAmount', 'status', 'isExpress', 'notes',
            'items', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'userId', 'createdAt', 'updatedAt']

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        mappings = {
            'scheduled_time': 'scheduledTime',
            'total_amount': 'totalAmount',
            'customer_name': 'customerName',
            'customer_phone': 'customerPhone',
            'delivery_address': 'deliveryAddress',
            'is_express': 'isExpress',
        }
        for snake, camel in mappings.items():
            if snake in data and camel not in data:
                data[camel] = data[snake]
        return super().to_internal_value(data)

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
            if not validated_data.get('customer_name'):
                validated_data['customer_name'] = request.user.get_full_name() or request.user.username
            if not validated_data.get('customer_phone') and hasattr(request.user, 'phone'):
                validated_data['customer_phone'] = request.user.phone
            if not validated_data.get('delivery_address') and hasattr(request.user, 'address'):
                validated_data['delivery_address'] = request.user.address

        order = Order.objects.create(**validated_data)

        calculated_total = Decimal('0.00')
        for item_data in items_data:
            product = item_data.get('product')
            quantity = item_data.get('quantity', 1)
            unit_price = item_data.get('unit_price')

            if unit_price is None and product:
                unit_price = product.price
            elif unit_price is not None:
                unit_price = Decimal(str(unit_price))
            else:
                unit_price = Decimal('0.00')

            product_name = item_data.get('product_name')
            if not product_name and product:
                product_name = product.name
            elif not product_name:
                product_name = "Producto sin especificar"

            subtotal = unit_price * quantity
            calculated_total += subtotal

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal
            )

        if not validated_data.get('total_amount') or order.total_amount == 0:
            order.total_amount = calculated_total
            order.save(update_fields=['total_amount'])

        return order
