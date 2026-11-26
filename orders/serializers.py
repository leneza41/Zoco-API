from django.db import transaction
from rest_framework import serializers
from decimal import Decimal
from .models import Order, OrderItem, OrderStatus
from products.models import Product
from zoco_api.serializers_mixins import SnakeCaseAliasMixin


class OrderItemSerializer(SnakeCaseAliasMixin, serializers.ModelSerializer):
    snake_case_aliases = {
        'product_id': 'productId',
        'product_name': 'productName',
        'unit_price': 'unitPrice',
    }

    productId = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        required=False,
        allow_null=True
    )
    productName = serializers.CharField(source='product_name', required=False)
    unitPrice = serializers.FloatField(source='unit_price', required=False)
    subtotal = serializers.FloatField(required=False)
    sellerUsername = serializers.CharField(source='product.seller.username', read_only=True, default=None)

    class Meta:
        model = OrderItem
        fields = ['id', 'productId', 'productName', 'quantity', 'unitPrice', 'subtotal', 'sellerUsername']


class OrderSerializer(SnakeCaseAliasMixin, serializers.ModelSerializer):
    snake_case_aliases = {
        'scheduled_time': 'scheduledTime',
        'total_amount': 'totalAmount',
        'customer_name': 'customerName',
        'customer_phone': 'customerPhone',
        'delivery_address': 'deliveryAddress',
        'is_express': 'isExpress',
    }

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

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        request = self.context.get('request')
        validated_data.pop('status', None)  # un pedido nuevo siempre inicia como pendiente
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
            if not validated_data.get('customer_name'):
                validated_data['customer_name'] = request.user.get_full_name() or request.user.username
            if not validated_data.get('customer_phone') and hasattr(request.user, 'phone'):
                validated_data['customer_phone'] = request.user.phone
            if not validated_data.get('delivery_address') and hasattr(request.user, 'address'):
                validated_data['delivery_address'] = request.user.address

        with transaction.atomic():
            # 1. Validar stock disponible para todos los productos del pedido
            requested_quantities = {}
            for item_data in items_data:
                product = item_data.get('product')
                quantity = item_data.get('quantity', 1)
                if product is not None:
                    requested_quantities[product.id] = requested_quantities.get(product.id, 0) + quantity

            locked_products = {}
            if requested_quantities:
                products_qs = Product.objects.select_for_update().filter(id__in=requested_quantities.keys())
                locked_products = {p.id: p for p in products_qs}

                stock_errors = []
                for product_id, total_qty in requested_quantities.items():
                    product = locked_products.get(product_id)
                    if product is None:
                        stock_errors.append(f"El producto con ID {product_id} no existe.")
                    elif product.stock < total_qty:
                        stock_errors.append(
                            f"Stock insuficiente para '{product.name}'. "
                            f"Disponible: {product.stock}, solicitado: {total_qty}."
                        )

                if stock_errors:
                    raise serializers.ValidationError({"items": stock_errors})

            # 2. Crear el pedido y sus items
            order = Order.objects.create(**validated_data)

            calculated_total = Decimal('0.00')
            for item_data in items_data:
                product = item_data.get('product')
                if product is not None and product.id in locked_products:
                    product = locked_products[product.id]
                quantity = item_data.get('quantity', 1)
                # El precio lo define el servidor: nunca se confía en el unitPrice del cliente.
                if product:
                    unit_price = product.price
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

            # 3. Deducir stock y sincronizar disponibilidad (in_stock)
            for product_id, total_qty in requested_quantities.items():
                product = locked_products[product_id]
                product.stock -= total_qty
                product.save(update_fields=['stock', 'in_stock', 'updated_at'])

            order.total_amount = calculated_total
            order.save(update_fields=['total_amount'])

        return order
