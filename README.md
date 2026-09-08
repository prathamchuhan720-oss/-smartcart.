# 🛒 SmartCart – E-Commerce Backend & Admin Dashboard

A production-style, full-featured e-commerce platform built with Django, Django REST Framework, PostgreSQL, and React.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.1-green)
![DRF](https://img.shields.io/badge/DRF-3.15-red)
![React](https://img.shields.io/badge/React-18-61DAFB)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Project Overview

SmartCart is a comprehensive e-commerce backend with an admin dashboard, designed as an internship-level project demonstrating:

- Clean architecture with modular Django apps
- RESTful API design with proper validation
- JWT-based authentication and role-based authorization
- Complex database relationships
- Server-side business logic (pricing, stock, coupons)
- Production-ready configuration

## ✨ Features

### Customer Features
- User registration, login, profile management
- Product browsing with search, filter, and sort
- Shopping cart with real-time stock validation
- Wishlist management
- Coupon/discount system
- Order placement with address selection
- Payment integration (Razorpay sandbox)
- Order tracking and history
- Product reviews and ratings

### Admin Features
- Dashboard with sales analytics
- Product, category, and brand management
- Order management with status updates
- Inventory tracking (low-stock, out-of-stock alerts)
- Coupon management
- Review moderation
- Sales reports and charts

### Advanced
- Product recommendation engine
- Product variants (size, color)
- Inventory history tracking

## 🏗 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.13, Django 5.1, DRF 3.15 |
| Database | PostgreSQL 16 (SQLite for dev) |
| Auth | JWT (Simple JWT) |
| API Docs | Swagger/OpenAPI (drf-spectacular) |
| Frontend | React 18, Axios, Chart.js/Recharts |
| Deployment | Gunicorn, WhiteNoise, Docker |

## 📁 Project Structure

```
smartcart/
├── backend/
│   ├── manage.py
│   ├── config/             # Django project settings
│   │   └── settings/       # Split settings (base/dev/prod)
│   ├── core/               # Shared utilities & base models
│   ├── accounts/           # User auth, profiles, addresses
│   ├── products/           # Product catalog
│   ├── categories/         # Category & brand management
│   ├── cart/               # Shopping cart
│   ├── wishlist/           # Wishlist
│   ├── orders/             # Order management
│   ├── payments/           # Payment processing
│   ├── inventory/          # Stock management
│   ├── reviews/            # Reviews & ratings
│   ├── coupons/            # Discount coupons
│   ├── analytics/          # Admin analytics & reports
│   ├── notifications/      # User notifications
│   ├── requirements/       # Split requirements
│   └── .env.example
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── hooks/
│       └── context/
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+ (optional, SQLite works for development)
- Node.js 18+ (for frontend)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/smartcart.git
cd smartcart/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### API Documentation
Once the server is running:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Django Admin**: http://localhost:8000/admin/

### Frontend Setup (Phase 11)
```bash
cd frontend
npm install
npm start
```

## 🔑 Environment Variables

See [.env.example](backend/.env.example) for all available environment variables.

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Dev key (change in prod!) |
| `DEBUG` | Debug mode | `True` |
| `DATABASE_URL` | PostgreSQL connection | SQLite fallback |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | `localhost:3000` |
| `RAZORPAY_KEY_ID` | Razorpay API key | - |
| `RAZORPAY_KEY_SECRET` | Razorpay secret | - |

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run with pytest (verbose)
pytest

# Run with coverage
pytest --cov --cov-report=html
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | User registration |
| `/api/auth/login/` | POST | JWT login |
| `/api/auth/refresh/` | POST | Refresh JWT token |
| `/api/products/` | GET | List products |
| `/api/products/<id>/` | GET | Product detail |
| `/api/cart/` | GET | View cart |
| `/api/cart/items/` | POST | Add to cart |
| `/api/orders/` | POST | Create order |
| `/api/orders/` | GET | Order history |
| `/api/wishlist/` | GET | View wishlist |
| `/api/payments/create/` | POST | Create payment |
| `/api/admin/dashboard/` | GET | Admin dashboard |
| `/api/docs/` | GET | Swagger documentation |

## 🐳 Docker

```bash
# Start PostgreSQL only
docker-compose up -d db

# Start full stack
docker-compose up -d
```

## 📈 Development Phases

1. ✅ Project setup & environment
2. ⬜ Database models
3. ⬜ Authentication
4. ⬜ Product & category APIs
5. ⬜ Cart & wishlist
6. ⬜ Orders & checkout
7. ⬜ Payment integration
8. ⬜ Inventory management
9. ⬜ Reviews & coupons
10. ⬜ Admin dashboard APIs
11. ⬜ React frontend
12. ⬜ Analytics & recommendations
13. ⬜ Testing
14. ⬜ Security review
15. ⬜ Deployment

## 📝 License

This project is for educational purposes. MIT License.
