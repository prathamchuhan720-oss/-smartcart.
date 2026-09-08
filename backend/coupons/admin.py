from django.contrib import admin
from .models import Coupon, CouponUsage


class CouponUsageInline(admin.TabularInline):
    model = CouponUsage
    extra = 0
    readonly_fields = ['user', 'order', 'discount_applied', 'created_at']
    can_delete = False


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'min_order_amount', 'times_used', 'usage_limit', 'is_active', 'expiry_date']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code', 'description']
    inlines = [CouponUsageInline]


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'order', 'discount_applied', 'created_at']
    search_fields = ['coupon__code', 'user__email']
