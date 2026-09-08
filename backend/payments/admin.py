from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'order', 'user', 'payment_method', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['transaction_id', 'razorpay_order_id', 'razorpay_payment_id', 'order__order_number', 'user__email']
    readonly_fields = ['transaction_id', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'amount', 'currency', 'created_at']
