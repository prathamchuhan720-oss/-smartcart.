from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['variant', 'quantity', 'unit_price', 'subtotal']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'total_items', 'subtotal', 'created_at', 'updated_at']
    search_fields = ['user__email', 'session_key']
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'variant', 'quantity', 'unit_price', 'subtotal']
    search_fields = ['cart__user__email', 'variant__title', 'variant__sku']
