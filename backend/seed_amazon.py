import os
import sys
from decimal import Decimal

sys.path.append(r"C:\Users\pratham\.gemini\antigravity\scratch\smartcart\backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django
django.setup()

from categories.models import Category, Brand
from products.models import Product, ProductImage, ProductVariant
from inventory.models import Inventory

AMAZON_PRODUCTS = [
    {
        "name": "Apple MacBook Air 13.6-inch M3 Chip (16GB RAM, 512GB SSD) - Space Grey",
        "sku": "AMZN-APL-MBA-M3-01",
        "category": "Laptops & Computers",
        "category_icon": "fas fa-laptop",
        "brand": "Apple",
        "base_price": Decimal("114900.00"),
        "discount_percentage": Decimal("10.00"),
        "rating": Decimal("4.80"),
        "reviews": 1420,
        "is_featured": True,
        "description": "Strikingly thin design. Fast performance with Apple M3 chip with 8-core CPU and 10-core GPU. Up to 18 hours of battery life. Liquid Retina display with 500 nits of brightness. MagSafe 3 charging port.",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80",
        "stock": 45
    },
    {
        "name": "Echo Dot (5th Gen) Smart Speaker with Alexa - Charcoal",
        "sku": "AMZN-ECHO-DOT-5-02",
        "category": "Smart Home",
        "category_icon": "fas fa-home",
        "brand": "Amazon",
        "base_price": Decimal("4499.00"),
        "discount_percentage": Decimal("22.00"),
        "rating": Decimal("4.60"),
        "reviews": 8940,
        "is_featured": True,
        "description": "Best sounding Echo Dot yet: Enjoy an improved audio experience compared to any previous Echo Dot with Alexa for clearer vocals, deeper bass and vibrant sound in any room. Control smart lights, play music, and check news hands-free.",
        "image_url": "https://images.unsplash.com/photo-1543512214-318c7553f230?w=800&auto=format&fit=crop&q=80",
        "stock": 120
    },
    {
        "name": "Apple AirPods Pro (2nd Generation) with USB-C Charging Case",
        "sku": "AMZN-APL-APP2-03",
        "category": "Audio & Headphones",
        "category_icon": "fas fa-headphones",
        "brand": "Apple",
        "base_price": Decimal("24900.00"),
        "discount_percentage": Decimal("15.00"),
        "rating": Decimal("4.90"),
        "reviews": 5670,
        "is_featured": True,
        "description": "Up to 2x more Active Noise Cancellation. Transparency mode lets outside sound in. Adaptive Audio dynamically blends noise control for your environment. Spatial Audio with dynamic head tracking. Dust, sweat, and water resistant.",
        "image_url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800&auto=format&fit=crop&q=80",
        "stock": 85
    },
    {
        "name": "Sony PlayStation 5 Slim Console (Disc Edition)",
        "sku": "AMZN-SNY-PS5-SLIM-04",
        "category": "Gaming & Consoles",
        "category_icon": "fas fa-gamepad",
        "brand": "Sony",
        "base_price": Decimal("54990.00"),
        "discount_percentage": Decimal("8.00"),
        "rating": Decimal("4.90"),
        "reviews": 3280,
        "is_featured": True,
        "description": "Slim design with 1TB SSD storage. Harness the power of a custom CPU, GPU, and SSD with Integrated I/O that rewrite the rules of what a PlayStation console can do. Marvel at incredible graphics with ray tracing and 4K TV gaming.",
        "image_url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=800&auto=format&fit=crop&q=80",
        "stock": 30
    },
    {
        "name": "Kindle Paperwhite (16 GB) - 6.8 inch display with adjustable warm light",
        "sku": "AMZN-KNDL-PW-16G-05",
        "category": "E-Readers & Tablets",
        "category_icon": "fas fa-tablet-alt",
        "brand": "Amazon",
        "base_price": Decimal("14999.00"),
        "discount_percentage": Decimal("12.00"),
        "rating": Decimal("4.70"),
        "reviews": 4310,
        "is_featured": True,
        "description": "Now with a 6.8 inch display and thinner borders, adjustable warm light, up to 10 weeks of battery life, and 20% faster page turns. Purpose-built for reading with a flush-front design and 300 ppi glare-free display that reads like real paper.",
        "image_url": "https://images.unsplash.com/photo-1592496001020-d31bd830651f?w=800&auto=format&fit=crop&q=80",
        "stock": 60
    },
    {
        "name": "Fire TV Stick 4K Max streaming device with Wi-Fi 6 & Alexa Voice Remote",
        "sku": "AMZN-FTV-STICK-4K-06",
        "category": "Smart Home",
        "category_icon": "fas fa-home",
        "brand": "Amazon",
        "base_price": Decimal("6499.00"),
        "discount_percentage": Decimal("25.00"),
        "rating": Decimal("4.60"),
        "reviews": 7120,
        "is_featured": False,
        "description": "Cinematic experience: Watch in vibrant 4K Ultra HD with support for Dolby Vision, HDR10+, and immersive Dolby Atmos audio. Seamless Wi-Fi 6 streaming and lightning-fast app start.",
        "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800&auto=format&fit=crop&q=80",
        "stock": 150
    },
    {
        "name": "Logitech MX Master 3S Wireless Performance Mouse",
        "sku": "AMZN-LOGI-MXM3S-07",
        "category": "Computer Accessories",
        "category_icon": "fas fa-mouse",
        "brand": "Logitech",
        "base_price": Decimal("10995.00"),
        "discount_percentage": Decimal("18.00"),
        "rating": Decimal("4.80"),
        "reviews": 6890,
        "is_featured": False,
        "description": "Any-surface tracking - now 8K DPI: Use MX Master 3S cordless computer mouse to work on any surface - even glass. Quiet clicks offer a satisfying feel with 90% less click noise. MagSpeed electromagnetic scrolling.",
        "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800&auto=format&fit=crop&q=80",
        "stock": 90
    },
    {
        "name": "Apple Watch Series 9 (GPS 45mm) - Midnight Aluminum Case with Sport Band",
        "sku": "AMZN-APL-AW9-45-08",
        "category": "Wearable Tech",
        "category_icon": "fas fa-clock",
        "brand": "Apple",
        "base_price": Decimal("44900.00"),
        "discount_percentage": Decimal("11.00"),
        "rating": Decimal("4.80"),
        "reviews": 2450,
        "is_featured": True,
        "description": "Powered by the S9 SiP chip, enabling a super-bright display and magical new way to interact with Apple Watch without touching the screen (Double Tap). Advanced health, safety, and activity tracking.",
        "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&auto=format&fit=crop&q=80",
        "stock": 40
    },
    {
        "name": "Bose QuietComfort Ultra Wireless Noise Cancelling Headphones",
        "sku": "AMZN-BOSE-QCU-09",
        "category": "Audio & Headphones",
        "category_icon": "fas fa-headphones",
        "brand": "Bose",
        "base_price": Decimal("35900.00"),
        "discount_percentage": Decimal("14.00"),
        "rating": Decimal("4.70"),
        "reviews": 1820,
        "is_featured": False,
        "description": "World-class noise cancellation, world-class comfort. Bose Immersive Audio pushes the boundary of what it means to listen, taking what you're hearing out of your head and placing it in front of you.",
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&auto=format&fit=crop&q=80",
        "stock": 55
    },
    {
        "name": "Samsung 55-inch The Frame QLED 4K Smart TV",
        "sku": "AMZN-SMSG-FRAME-55-10",
        "category": "TV & Entertainment",
        "category_icon": "fas fa-tv",
        "brand": "Samsung",
        "base_price": Decimal("89990.00"),
        "discount_percentage": Decimal("20.00"),
        "rating": Decimal("4.60"),
        "reviews": 1150,
        "is_featured": True,
        "description": "Art Mode turns your TV into artwork when you are not watching TV. Matte Display virtually eliminates glare. 100% Color Volume with Quantum Dot technology for billion shades of true-to-life color.",
        "image_url": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&auto=format&fit=crop&q=80",
        "stock": 25
    },
    {
        "name": "Instant Pot Duo 7-in-1 Electric Pressure Cooker (6 Quart)",
        "sku": "AMZN-INST-POT-6Q-11",
        "category": "Kitchen & Dining",
        "category_icon": "fas fa-utensils",
        "brand": "Instant Brands",
        "base_price": Decimal("9999.00"),
        "discount_percentage": Decimal("30.00"),
        "rating": Decimal("4.70"),
        "reviews": 14200,
        "is_featured": False,
        "description": "7-in-1 functionality: pressure cook, slow cook, rice cooker, yogurt maker, steamer, sauté pan and food warmer. Quick one-touch cooking with 13 customizable Smart Programs. Over 10 safety features.",
        "image_url": "https://images.unsplash.com/photo-1588854337236-6889d631faa8?w=800&auto=format&fit=crop&q=80",
        "stock": 80
    },
    {
        "name": "Dyson V15 Detect Cordless Vacuum Cleaner",
        "sku": "AMZN-DYSN-V15-12",
        "category": "Home & Cleaning",
        "category_icon": "fas fa-broom",
        "brand": "Dyson",
        "base_price": Decimal("62900.00"),
        "discount_percentage": Decimal("12.00"),
        "rating": Decimal("4.80"),
        "reviews": 3100,
        "is_featured": True,
        "description": "Laser reveals invisible microscopic dust on hard floors. Piezo sensor continuously sizes and counts dust particles, automatically increasing suction power when needed. Up to 60 minutes of run time.",
        "image_url": "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=800&auto=format&fit=crop&q=80",
        "stock": 35
    },
    {
        "name": "Stanley Quencher H2.0 FlowState Stainless Steel Tumbler (40 oz)",
        "sku": "AMZN-STNL-40OZ-13",
        "category": "Sports & Outdoors",
        "category_icon": "fas fa-tint",
        "brand": "Stanley",
        "base_price": Decimal("3999.00"),
        "discount_percentage": Decimal("10.00"),
        "rating": Decimal("4.80"),
        "reviews": 18450,
        "is_featured": False,
        "description": "Double-wall vacuum insulation keeps drinks ice-cold for 48 hours or hot for 7 hours. Advanced FlowState lid features a rotating cover with three positions. Ergonomic handle and car cup-holder compatible.",
        "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800&auto=format&fit=crop&q=80",
        "stock": 200
    },
    {
        "name": "Nespresso Vertuo Pop Coffee and Espresso Machine by De'Longhi",
        "sku": "AMZN-NESP-VPOP-14",
        "category": "Kitchen & Dining",
        "category_icon": "fas fa-utensils",
        "brand": "Nespresso",
        "base_price": Decimal("15999.00"),
        "discount_percentage": Decimal("25.00"),
        "rating": Decimal("4.60"),
        "reviews": 4890,
        "is_featured": False,
        "description": "Brews a wide range of coffee styles: 5 cup sizes at the touch of a button (espresso 1.35 oz, double espresso 2.7 oz, gran lungo 5 oz, mug 7.7 oz, cold brew). Centrifusion technology delivers velvety crema.",
        "image_url": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=800&auto=format&fit=crop&q=80",
        "stock": 70
    },
    {
        "name": "Canon EOS R50 Mirrorless Camera with 18-45mm Lens Kit",
        "sku": "AMZN-CNN-R50-15",
        "category": "Cameras & Photography",
        "category_icon": "fas fa-camera",
        "brand": "Canon",
        "base_price": Decimal("67990.00"),
        "discount_percentage": Decimal("15.00"),
        "rating": Decimal("4.70"),
        "reviews": 1670,
        "is_featured": True,
        "description": "Compact and lightweight 24.2 MP APS-C CMOS sensor camera. Dual Pixel CMOS AF II with subject detection for people, animals, and vehicles. Uncropped 4K video recording up to 30p oversampled from 6K.",
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&auto=format&fit=crop&q=80",
        "stock": 28
    }
]

def seed_amazon_products():
    print("Seeding Amazon top products...")
    created_count = 0
    updated_count = 0

    for item in AMAZON_PRODUCTS:
        # Category
        category, _ = Category.objects.get_or_create(
            name=item["category"],
            defaults={"icon": item["category_icon"], "description": f"Shop the best {item['category']} on SmartCart"}
        )
        
        # Brand
        brand, _ = Brand.objects.get_or_create(
            name=item["brand"],
            defaults={"description": f"Official {item['brand']} products"}
        )

        # Product
        product, created = Product.objects.update_or_create(
            sku=item["sku"],
            defaults={
                "name": item["name"],
                "category": category,
                "brand": brand,
                "base_price": item["base_price"],
                "discount_percentage": item["discount_percentage"],
                "average_rating": item["rating"],
                "total_reviews": item["reviews"],
                "is_featured": item["is_featured"],
                "is_active": True,
                "description": item["description"],
                "image_url": item["image_url"]
            }
        )

        # Ensure primary ProductImage
        pimg, _ = ProductImage.objects.get_or_create(
            product=product,
            is_primary=True,
            defaults={
                "image_url": item["image_url"],
                "alt_text": item["name"]
            }
        )
        if not pimg.image_url:
            pimg.image_url = item["image_url"]
            pimg.save()

        # Variant & Inventory
        variant, _ = ProductVariant.objects.get_or_create(
            product=product,
            title="Standard",
            sku=f"{item['sku']}-STD",
            defaults={"additional_price": Decimal("0.00"), "is_active": True}
        )

        inventory, _ = Inventory.objects.get_or_create(
            variant=variant,
            defaults={"stock_quantity": item["stock"], "low_stock_threshold": 5}
        )
        inventory.stock_quantity = item["stock"]
        inventory.save()

        if created:
            created_count += 1
        else:
            updated_count += 1

    total = Product.objects.count()
    print(f"Done! Created: {created_count}, Updated: {updated_count}. Total catalog products: {total}")

if __name__ == "__main__":
    seed_amazon_products()
