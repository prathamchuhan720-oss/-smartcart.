"""
Base Django settings for SmartCart project.

Shared settings used by all environments (development, production).
Environment-specific overrides go in development.py / production.py.
"""
import os
from datetime import timedelta
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
)

# Read .env file if it exists
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(str(env_file))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# --------------------------------------------------------------------------
# Application definition
# --------------------------------------------------------------------------

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'corsheaders',
    'drf_spectacular',
]

LOCAL_APPS = [
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'products.apps.ProductsConfig',
    'categories.apps.CategoriesConfig',
    'cart.apps.CartConfig',
    'wishlist.apps.WishlistConfig',
    'orders.apps.OrdersConfig',
    'payments.apps.PaymentsConfig',
    'inventory.apps.InventoryConfig',
    'reviews.apps.ReviewsConfig',
    'coupons.apps.CouponsConfig',
    'analytics.apps.AnalyticsConfig',
    'notifications.apps.NotificationsConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# --------------------------------------------------------------------------
# Middleware
# --------------------------------------------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# --------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------
# Configured in environment-specific settings files.
# See development.py and production.py

# --------------------------------------------------------------------------
# Password validation
# --------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------------------------------------------------------
# Custom User Model
# --------------------------------------------------------------------------

AUTH_USER_MODEL = 'accounts.User'

# --------------------------------------------------------------------------
# Internationalization
# --------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)
# --------------------------------------------------------------------------

STATIC_URL = env('STATIC_URL', default='/static/')
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# --------------------------------------------------------------------------
# Media files (User uploads)
# --------------------------------------------------------------------------

MEDIA_URL = env('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / 'media'

# --------------------------------------------------------------------------
# Default primary key field type
# --------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------------------------------
# Django REST Framework
# --------------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'core.renderers.SmartCartJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}

# --------------------------------------------------------------------------
# Simple JWT Configuration
# --------------------------------------------------------------------------

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=env.int('ACCESS_TOKEN_LIFETIME_MINUTES', default=30)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=env.int('REFRESH_TOKEN_LIFETIME_DAYS', default=7)
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# --------------------------------------------------------------------------
# CORS Configuration
# --------------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=['http://localhost:3000', 'http://127.0.0.1:3000']
)
CORS_ALLOW_CREDENTIALS = True

# --------------------------------------------------------------------------
# DRF Spectacular (OpenAPI/Swagger)
# --------------------------------------------------------------------------

SPECTACULAR_SETTINGS = {
    'TITLE': 'SmartCart E-Commerce API',
    'DESCRIPTION': 'A production-style e-commerce backend API with full product management, cart, orders, payments, and admin dashboard.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/',
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'Auth', 'description': 'Authentication & user management'},
        {'name': 'Products', 'description': 'Product catalog'},
        {'name': 'Categories', 'description': 'Product categories'},
        {'name': 'Cart', 'description': 'Shopping cart operations'},
        {'name': 'Wishlist', 'description': 'Wishlist management'},
        {'name': 'Orders', 'description': 'Order management'},
        {'name': 'Payments', 'description': 'Payment processing'},
        {'name': 'Reviews', 'description': 'Product reviews & ratings'},
        {'name': 'Coupons', 'description': 'Coupon management'},
        {'name': 'Admin', 'description': 'Admin dashboard & analytics'},
    ],
}

# --------------------------------------------------------------------------
# Email Configuration
# --------------------------------------------------------------------------

EMAIL_BACKEND = env(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')

# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'smartcart': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
