import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category', lookup_expr='iexact')
    producerName = django_filters.CharFilter(field_name='producer_name', lookup_expr='icontains')
    producer_name = django_filters.CharFilter(field_name='producer_name', lookup_expr='icontains')
    isExpressDelivery = django_filters.BooleanFilter(field_name='is_express_delivery')
    is_express_delivery = django_filters.BooleanFilter(field_name='is_express_delivery')
    inStock = django_filters.BooleanFilter(field_name='in_stock')
    in_stock = django_filters.BooleanFilter(field_name='in_stock')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = [
            'category', 'producer_name', 'producerName',
            'is_express_delivery', 'isExpressDelivery',
            'in_stock', 'inStock', 'min_price', 'max_price'
        ]
