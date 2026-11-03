from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'scheduled_time', 'total_amount', 'status', 'is_express', 'created_at')
    list_filter = ('status', 'is_express', 'created_at')
    search_fields = ('customer_name', 'customer_phone', 'delivery_address')
    list_editable = ('status',)
    inlines = [OrderItemInline]
