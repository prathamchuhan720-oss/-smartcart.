"""
Management command to seed realistic initial data for SmartCart.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User, UserProfile, Address
from categories.models import Category, Brand
from products.models import Product, ProductVariant
from inventory.models import Inventory, InventoryHistory
from coupons.models import Coupon
from reviews.models import Review


class Command(BaseCommand):
    help = 'Seed the database with sample products, categories, brands, users, and coupons'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Seeding SmartCart database...'))

        # 1. Create Admin User
        admin_user, created = User.objects.get_or_create(
            email='admin@smartcart.com',
            defaults={
                'username': 'admin',
                'first_name': 'SmartCart',
                'last_name': 'Admin',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_email_verified': True,
            }
        )
        if created:
            admin_user.set_password('Admin@12345')
            admin_user.save()
            UserProfile.objects.create(user=admin_user, bio="System Administrator")
            self.stdout.write(self.style.SUCCESS('Admin user created: admin@smartcart.com (Password: Admin@12345)'))
        else:
            self.stdout.write('Admin user already exists.')

        # 2. Create Demo Customer
        customer_user, created = User.objects.get_or_create(
            email='customer@smartcart.com',
            defaults={
                'username': 'john_doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': User.Role.CUSTOMER,
                'phone_number': '+91 9876543210',
                'is_email_verified': True,
            }
        )
        if created:
            customer_user.set_password('Customer@12345')
            customer_user.save()
            UserProfile.objects.create(user=customer_user, gender=UserProfile.Gender.MALE, bio="Enthusiastic online shopper")
            Address.objects.create(
                user=customer_user,
                full_name="John Doe",
                phone_number="+91 9876543210",
                street_address="42 Tech Park Avenue",
                landmark="Near Innovation Hub",
                city="Bengaluru",
                state="Karnataka",
                postal_code="560001",
                country="India",
                is_default=True,
            )
            self.stdout.write(self.style.SUCCESS('Customer user created: customer@smartcart.com (Password: Customer@12345)'))

        # 3. Create Categories
        categories_data = [
            {'name': 'Electronics', 'slug': 'electronics', 'icon': 'fa-laptop', 'description': 'Gadgets, phones, laptops and accessories'},
            {'name': 'Fashion', 'slug': 'fashion', 'icon': 'fa-tshirt', 'description': 'Clothing, shoes, and apparel'},
            {'name': 'Home & Kitchen', 'slug': 'home-kitchen', 'icon': 'fa-couch', 'description': 'Appliances, decor, and cookware'},
            {'name': 'Sports & Fitness', 'slug': 'sports-fitness', 'icon': 'fa-dumbbell', 'description': 'Gear, gym equipment, and fitness accessories'},
        ]
        cat_map = {}
        for cdata in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=cdata['slug'],
                defaults=cdata,
            )
            cat_map[cdata['slug']] = cat

        # Subcategories
        sub_cat, _ = Category.objects.get_or_create(
            slug='smartphones',
            defaults={'name': 'Smartphones', 'parent': cat_map['electronics'], 'description': 'Mobile devices and cellular phones'}
        )
        cat_map['smartphones'] = sub_cat

        sub_cat_mens, _ = Category.objects.get_or_create(
            slug='mens-wear',
            defaults={'name': "Men's Wear", 'parent': cat_map['fashion'], 'description': 'Apparel and casual wear for men'}
        )
        cat_map['mens-wear'] = sub_cat_mens

        # 4. Create Brands
        brands_data = [
            {'name': 'Apple', 'slug': 'apple', 'website': 'https://apple.com'},
            {'name': 'Samsung', 'slug': 'samsung', 'website': 'https://samsung.com'},
            {'name': 'Nike', 'slug': 'nike', 'website': 'https://nike.com'},
            {'name': 'Adidas', 'slug': 'adidas', 'website': 'https://adidas.com'},
            {'name': 'Sony', 'slug': 'sony', 'website': 'https://sony.com'},
        ]
        brand_map = {}
        for bdata in brands_data:
            br, _ = Brand.objects.get_or_create(
                slug=bdata['slug'],
                defaults=bdata,
            )
            brand_map[bdata['slug']] = br

        # 5. Create Products & Variants
        products_data = [
            {
                'name': 'iPhone 15 Pro',
                'slug': 'iphone-15-pro',
                'sku': 'APL-IP15P',
                'description': 'Titanium design with A17 Pro chip, customizable Action button, and 48MP camera.',
                'category': cat_map['smartphones'],
                'brand': brand_map['apple'],
                'base_price': Decimal('119900.00'),
                'discount_percentage': Decimal('5.00'),
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&auto=format&fit=crop&q=80',
                'variants': [
                    {'title': '128GB / Natural Titanium', 'sku': 'IP15P-128-NAT', 'size': '128GB', 'color': 'Natural Titanium', 'add_price': Decimal('0.00'), 'stock': 25},
                    {'title': '256GB / Blue Titanium', 'sku': 'IP15P-256-BLU', 'size': '256GB', 'color': 'Blue Titanium', 'add_price': Decimal('10000.00'), 'stock': 4}, # Low stock
                ]
            },
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'slug': 'samsung-galaxy-s24-ultra',
                'sku': 'SAM-S24U',
                'description': 'Galaxy AI is here. Epic camera with 100x zoom and integrated S-Pen stylus.',
                'category': cat_map['smartphones'],
                'brand': brand_map['samsung'],
                'base_price': Decimal('129999.00'),
                'discount_percentage': Decimal('10.00'),
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&auto=format&fit=crop&q=80',
                'variants': [
                    {'title': '256GB / Titanium Black', 'sku': 'S24U-256-BLK', 'size': '256GB', 'color': 'Titanium Black', 'add_price': Decimal('0.00'), 'stock': 15},
                    {'title': '512GB / Titanium Gray', 'sku': 'S24U-512-GRY', 'size': '512GB', 'color': 'Titanium Gray', 'add_price': Decimal('15000.00'), 'stock': 0}, # Out of stock
                ]
            },
            {
                'name': 'Nike Dri-FIT Legend T-Shirt',
                'slug': 'nike-dri-fit-legend-tshirt',
                'sku': 'NKE-DF-TSHIRT',
                'description': 'Classic athletic crew neck made with lightweight, sweat-wicking fabric for total comfort.',
                'category': cat_map['mens-wear'],
                'brand': brand_map['nike'],
                'base_price': Decimal('1695.00'),
                'discount_percentage': Decimal('15.00'),
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop&q=80',
                'variants': [
                    {'title': 'Small / Black', 'sku': 'NKE-TS-S-BLK', 'size': 'S', 'color': 'Black', 'add_price': Decimal('0.00'), 'stock': 40},
                    {'title': 'Medium / Black', 'sku': 'NKE-TS-M-BLK', 'size': 'M', 'color': 'Black', 'add_price': Decimal('0.00'), 'stock': 50},
                    {'title': 'Large / Black', 'sku': 'NKE-TS-L-BLK', 'size': 'L', 'color': 'Black', 'add_price': Decimal('0.00'), 'stock': 35},
                    {'title': 'Medium / White', 'sku': 'NKE-TS-M-WHT', 'size': 'M', 'color': 'White', 'add_price': Decimal('0.00'), 'stock': 20},
                ]
            },
            {
                'name': 'Sony WH-1000XM5 Noise Canceling Headphones',
                'slug': 'sony-wh-1000xm5',
                'sku': 'SNY-WH1000XM5',
                'description': 'Industry-leading noise cancellation with two processors and eight microphones for unprecedented sound.',
                'category': cat_map['electronics'],
                'brand': brand_map['sony'],
                'base_price': Decimal('29990.00'),
                'discount_percentage': Decimal('12.00'),
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80',
                'variants': [
                    {'title': 'Standard / Silver', 'sku': 'SNY-XM5-SLV', 'size': 'Standard', 'color': 'Silver', 'add_price': Decimal('0.00'), 'stock': 18},
                    {'title': 'Standard / Black', 'sku': 'SNY-XM5-BLK', 'size': 'Standard', 'color': 'Black', 'add_price': Decimal('0.00'), 'stock': 22},
                ]
            },
            {
                'name': 'Adidas Ultraboost Light Running Shoes',
                'slug': 'adidas-ultraboost-light',
                'sku': 'ADS-UB-LIGHT',
                'description': 'Experience epic energy return with the lightest Ultraboost ever made.',
                'category': cat_map['sports-fitness'],
                'brand': brand_map['adidas'],
                'base_price': Decimal('18999.00'),
                'discount_percentage': Decimal('20.00'),
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80',
                'variants': [
                    {'title': 'UK 8 / Core Black', 'sku': 'ADS-UB-8-BLK', 'size': 'UK 8', 'color': 'Core Black', 'add_price': Decimal('0.00'), 'stock': 12},
                    {'title': 'UK 9 / Cloud White', 'sku': 'ADS-UB-9-WHT', 'size': 'UK 9', 'color': 'Cloud White', 'add_price': Decimal('0.00'), 'stock': 2}, # Low stock
                ]
            }
        ]

        for pdata in products_data:
            variants = pdata.pop('variants')
            img_url = pdata.get('image_url', '')
            prod, created = Product.objects.get_or_create(
                sku=pdata['sku'],
                defaults=pdata,
            )
            if not created and img_url:
                prod.image_url = img_url
                prod.save(update_fields=['image_url'])

            for vdata in variants:
                stock_val = vdata.pop('stock')
                variant, _ = ProductVariant.objects.get_or_create(
                    sku=vdata['sku'],
                    product=prod,
                    defaults={
                        'title': vdata['title'],
                        'size': vdata['size'],
                        'color': vdata['color'],
                        'additional_price': vdata['add_price'],
                    }
                )
                inv, _ = Inventory.objects.get_or_create(
                    variant=variant,
                    defaults={
                        'stock_quantity': stock_val,
                        'low_stock_threshold': 5,
                    }
                )
                # Seed inventory history
                InventoryHistory.objects.get_or_create(
                    inventory=inv,
                    reason=InventoryHistory.ChangeReason.RESTOCK,
                    quantity_change=stock_val,
                    previous_stock=0,
                    new_stock=stock_val,
                    defaults={'notes': 'Initial system bootstrap'}
                )

        # 6. Create Coupons
        coupons_data = [
            {
                'code': 'WELCOME10',
                'description': '10% off on your order over ₹1000',
                'discount_type': Coupon.DiscountType.PERCENTAGE,
                'discount_value': Decimal('10.00'),
                'min_order_amount': Decimal('1000.00'),
                'max_discount_amount': Decimal('1500.00'),
                'start_date': timezone.now() - timezone.timedelta(days=1),
                'expiry_date': timezone.now() + timezone.timedelta(days=90),
                'usage_limit': 1000,
                'per_user_limit': 1,
                'is_active': True,
            },
            {
                'code': 'FLAT500',
                'description': 'Flat ₹500 off on purchases above ₹3000',
                'discount_type': Coupon.DiscountType.FIXED,
                'discount_value': Decimal('500.00'),
                'min_order_amount': Decimal('3000.00'),
                'start_date': timezone.now() - timezone.timedelta(days=1),
                'expiry_date': timezone.now() + timezone.timedelta(days=60),
                'usage_limit': 500,
                'per_user_limit': 2,
                'is_active': True,
            },
            {
                'code': 'EXPIRED20',
                'description': 'Past flash sale coupon',
                'discount_type': Coupon.DiscountType.PERCENTAGE,
                'discount_value': Decimal('20.00'),
                'min_order_amount': Decimal('500.00'),
                'start_date': timezone.now() - timezone.timedelta(days=30),
                'expiry_date': timezone.now() - timezone.timedelta(days=5),
                'is_active': False,
            }
        ]
        for cdata in coupons_data:
            Coupon.objects.get_or_create(code=cdata['code'], defaults=cdata)

        # 7. Add sample review
        sample_prod = Product.objects.filter(sku='NKE-DF-TSHIRT').first()
        if sample_prod:
            Review.objects.get_or_create(
                user=customer_user,
                product=sample_prod,
                defaults={
                    'rating': 5,
                    'title': 'Outstanding quality and comfort!',
                    'comment': 'The fabric is super breathable and fits true to size. High quality stitching from Nike as usual.',
                    'is_approved': True,
                    'is_verified_purchase': True,
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with all initial sample data!'))
