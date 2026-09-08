from datetime import timedelta
from decimal import Decimal
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from rest_framework import views, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from core.permissions import IsAdminUser
from accounts.models import User
from products.models import Product
from orders.models import Order, OrderItem
from inventory.models import Inventory
from categories.models import Category


@extend_schema(tags=['Admin'])
class AdminDashboardStatsView(views.APIView):
    """
    Comprehensive KPIs and summary statistics for the Admin Dashboard.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Revenue calculations (only counting paid / confirmed orders)
        paid_orders = Order.objects.filter(payment_status=Order.PaymentStatus.PAID)
        total_revenue = paid_orders.aggregate(val=Sum('total_amount'))['val'] or Decimal('0.00')
        today_revenue = paid_orders.filter(created_at__gte=today_start).aggregate(val=Sum('total_amount'))['val'] or Decimal('0.00')
        monthly_revenue = paid_orders.filter(created_at__gte=month_start).aggregate(val=Sum('total_amount'))['val'] or Decimal('0.00')

        # Order status counts
        all_orders = Order.objects.all()
        total_orders = all_orders.count()
        pending_orders = all_orders.filter(status=Order.OrderStatus.PENDING).count()
        processing_orders = all_orders.filter(status=Order.OrderStatus.PROCESSING).count()
        delivered_orders = all_orders.filter(status=Order.OrderStatus.DELIVERED).count()
        cancelled_orders = all_orders.filter(status=Order.OrderStatus.CANCELLED).count()

        # Customer & Product counts
        total_customers = User.objects.filter(role=User.Role.CUSTOMER).count()
        total_products = Product.objects.count()

        # Stock counts
        low_stock_count = Inventory.objects.filter(
            stock_quantity__gt=0,
            stock_quantity__lte=F('low_stock_threshold')
        ).count()
        out_of_stock_count = Inventory.objects.filter(stock_quantity=0).count()

        return Response({
            'kpis': {
                'total_revenue': float(total_revenue),
                'today_revenue': float(today_revenue),
                'monthly_revenue': float(monthly_revenue),
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'processing_orders': processing_orders,
                'delivered_orders': delivered_orders,
                'cancelled_orders': cancelled_orders,
                'total_customers': total_customers,
                'total_products': total_products,
                'low_stock_count': low_stock_count,
                'out_of_stock_count': out_of_stock_count,
            }
        })


@extend_schema(tags=['Admin'])
class AdminAnalyticsChartsView(views.APIView):
    """
    Data series for dashboard charts:
    - Daily revenue (past 14 days)
    - Monthly revenue (past 12 months)
    - Top 5 selling products
    - Revenue by category
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        now = timezone.now()
        two_weeks_ago = now - timedelta(days=14)

        # 1. Daily Sales
        daily_sales = (
            Order.objects.filter(
                payment_status=Order.PaymentStatus.PAID,
                created_at__gte=two_weeks_ago
            )
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(revenue=Sum('total_amount'), order_count=Count('id'))
            .order_by('date')
        )

        daily_data = [
            {
                'date': str(item['date']),
                'revenue': float(item['revenue'] or 0),
                'orders': item['order_count']
            } for item in daily_sales
        ]

        # 2. Top Selling Products
        top_products = (
            OrderItem.objects.filter(order__payment_status=Order.PaymentStatus.PAID)
            .values('product_name')
            .annotate(units_sold=Sum('quantity'), total_sales=Sum('subtotal'))
            .order_by('-units_sold')[:5]
        )

        # 3. Revenue by Category
        category_revenue = (
            OrderItem.objects.filter(
                order__payment_status=Order.PaymentStatus.PAID,
                product__category__isnull=False
            )
            .values(category_name=F('product__category__name'))
            .annotate(total=Sum('subtotal'))
            .order_by('-total')[:6]
        )

        return Response({
            'daily_sales': daily_data,
            'top_products': list(top_products),
            'category_revenue': [
                {'category': item['category_name'], 'revenue': float(item['total'] or 0)}
                for item in category_revenue
            ]
        })


@extend_schema(tags=['Admin'])
class AdminRecentOrdersView(views.APIView):
    """
    Recent orders list for quick overview on dashboard.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
        data = [
            {
                'id': ord.id,
                'order_number': ord.order_number,
                'customer_name': ord.user.full_name,
                'customer_email': ord.user.email,
                'status': ord.status,
                'payment_status': ord.payment_status,
                'total_amount': float(ord.total_amount),
                'items_count': ord.items.count(),
                'created_at': ord.created_at.strftime('%Y-%m-%d %H:%M'),
            }
            for ord in recent_orders
        ]
        return Response(data)
