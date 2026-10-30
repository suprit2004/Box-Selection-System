from django.contrib import admin
from .models import Product, ShippingBox, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'length', 'width', 'height', 'weight', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'sku')
    ordering = ('name',)


@admin.register(ShippingBox)
class ShippingBoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'internal_length', 'internal_width', 'internal_height', 'max_weight', 'cost', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('cost', 'name')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product', 'quantity', 'unit_weight')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'status', 'recommended_box', 'total_weight', 'total_volume', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'packing_notes')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at')
