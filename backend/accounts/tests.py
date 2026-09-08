from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from categories.models import Category, Brand
from products.models import Product, ProductVariant
from inventory.models import Inventory
from cart.models import Cart, CartItem
from coupons.models import Coupon
from orders.models import Order


class SmartCartAPITestCase(APITestCase):
    def setUp(self):
        # 1. Users
        self.customer = User.objects.create_user(
            email='alice@example.com',
            username='alice',
            password='Password123!',
            first_name='Alice',
            last_name='Smith',
            role=User.Role.CUSTOMER,
        )
        self.admin = User.objects.create_user(
            email='boss@smartcart.com',
            username='boss',
            password='AdminPassword123!',
            role=User.Role.ADMIN,
            is_staff=True,
        )

        # 2. Category & Brand
        self.category = Category.objects.create(name='Footwear', slug='footwear')
        self.brand = Brand.objects.create(name='Puma', slug='puma')

        # 3. Product & Variant & Inventory
        self.product = Product.objects.create(
            name='Puma Nitro Running Shoes',
            slug='puma-nitro-running-shoes',
            sku='PMA-NITRO-01',
            description='Top grade foam cushioning.',
            category=self.category,
            brand=self.brand,
            base_price=Decimal('5000.00'),
            discount_percentage=Decimal('10.00'),
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            title='UK 9 / Black',
            sku='PMA-NITRO-UK9-BLK',
            size='UK 9',
            color='Black',
            additional_price=Decimal('0.00'),
        )
        self.inventory = Inventory.objects.create(
            variant=self.variant,
            stock_quantity=10,
            low_stock_threshold=3,
        )

    def test_user_registration(self):
        url = reverse('auth-register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!',
            'first_name': 'New',
            'last_name': 'User',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertEqual(User.objects.filter(email='newuser@example.com').count(), 1)

    def test_user_login(self):
        url = reverse('auth-login')
        data = {
            'email': 'alice@example.com',
            'password': 'Password123!',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['email'], 'alice@example.com')

    def test_product_listing(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that results contains our product
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertTrue(len(results) >= 1)

    def test_add_to_cart_and_stock_validation(self):
        # Authenticate customer
        self.client.force_authenticate(user=self.customer)
        url = reverse('cart-item-create')

        # Add 2 items (valid)
        response = self.client.post(url, {'variant_id': self.variant.id, 'quantity': 2}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Attempt to add 100 items (exceeds 10 stock)
        response_excess = self.client.post(url, {'variant_id': self.variant.id, 'quantity': 100}, format='json')
        self.assertEqual(response_excess.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_permissions(self):
        # Customer cannot view admin stats
        self.client.force_authenticate(user=self.customer)
        admin_url = reverse('admin-dashboard-stats')
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admin CAN view admin stats
        self.client.force_authenticate(user=self.admin)
        response_admin = self.client.get(admin_url)
        self.assertEqual(response_admin.status_code, status.HTTP_200_OK)
        self.assertIn('kpis', response_admin.data)
