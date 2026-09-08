"""
Production-specific Django settings for SmartCart.

Overrides base settings for deployment:
- Configurable DEBUG (default False)
- Automatic PostgreSQL via DATABASE_URL with SQLite fallback
- Dynamic ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS for cloud providers
- WhiteNoise for compressed static file serving
- Production security headers
"""
from .base import *  # noqa: F401, F403
from .base import env, MIDDLEWARE, BASE_DIR

# --------------------------------------------------------------------------
# Debug - False by default in production
# --------------------------------------------------------------------------

DEBUG = env.bool('DEBUG', default=False)

# --------------------------------------------------------------------------
# Allowed Hosts & CSRF Trusted Origins
# --------------------------------------------------------------------------

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
    '*',
    'localhost',
    '127.0.0.1',
    '.onrender.com',
    '.railway.app',
    '.pythonanywhere.com',
])

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'https://*.onrender.com',
    'https://*.railway.app',
    'https://*.pythonanywhere.com',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
])

CORS_ALLOW_ALL_ORIGINS = env.bool('CORS_ALLOW_ALL_ORIGINS', default=True)

# --------------------------------------------------------------------------
# Database - PostgreSQL if DATABASE_URL provided, else SQLite fallback
# --------------------------------------------------------------------------

if env('DATABASE_URL', default=None):
    DATABASES = {
        'default': env.db('DATABASE_URL')
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --------------------------------------------------------------------------
# Security
# --------------------------------------------------------------------------

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --------------------------------------------------------------------------
# WhiteNoise for static files
# --------------------------------------------------------------------------

if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    insert_idx = MIDDLEWARE.index('django.middleware.common.CommonMiddleware') if 'django.middleware.common.CommonMiddleware' in MIDDLEWARE else 0
    MIDDLEWARE.insert(insert_idx, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

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
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
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
    },
}
