from django.contrib import admin
from .models import Inventory, InventoryHistory


class InventoryHistoryInline(admin.TabularInline):
    model = InventoryHistory
    extra = 0
    readonly_fields = ['reason', 'quantity_change', 'previous_stock', 'new_stock', 'performed_by', 'created_at']
    can_delete = False


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['variant', 'stock_quantity', 'reserved_quantity', 'available_stock', 'status', 'low_stock_threshold']
    list_filter = ['low_stock_threshold']
    search_fields = ['variant__title', 'variant__sku', 'variant__product__name']
    inlines = [InventoryHistoryInline]


@admin.register(InventoryHistory)
class InventoryHistoryAdmin(admin.ModelAdmin):
    list_display = ['inventory', 'reason', 'quantity_change', 'previous_stock', 'new_stock', 'performed_by', 'created_at']
    list_filter = ['reason']
    search_fields = ['inventory__variant__sku', 'notes']
    readonly_fields = ['inventory', 'reason', 'quantity_change', 'previous_stock', 'new_stock', 'performed_by', 'created_at']
