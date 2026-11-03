from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'producer_name', 'is_express_delivery', 'in_stock', 'created_at')
    list_filter = ('category', 'is_express_delivery', 'in_stock', 'created_at')
    search_fields = ('name', 'description', 'producer_name')
    list_editable = ('price', 'in_stock', 'is_express_delivery')
