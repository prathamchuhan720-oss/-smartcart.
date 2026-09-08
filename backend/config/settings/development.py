"""
Development-specific Django settings for SmartCart.

Overrides base settings for local development:
- DEBUG enabled
- SQLite fallback if PostgreSQL unavailable  
- Django Debug Toolbar
- Console email backend
"""
from .base import *  # noqa: F401, F403
from .base import env, BASE_DIR, INSTALLED_APPS, MIDDLEWARE

# --------------------------------------------------------------------------
# Debug
# --------------------------------------------------------------------------

DEBUG = True

# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------
# Use PostgreSQL if DATABASE_URL is set, otherwise fall back to SQLite.

if env('DATABASE_URL', default=''):
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
# Django Debug Toolbar
# --------------------------------------------------------------------------

try:
    import debug_toolbar  # noqa: F401
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(
        MIDDLEWARE.index('django.middleware.common.CommonMiddleware') + 1,
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    INTERNAL_IPS = ['127.0.0.1']
except ImportError:
    pass

# --------------------------------------------------------------------------
# Email
# --------------------------------------------------------------------------

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --------------------------------------------------------------------------
# CORS - Allow all in development
# --------------------------------------------------------------------------

CORS_ALLOW_ALL_ORIGINS = True

# --------------------------------------------------------------------------
# Throttle rates - More lenient in development
# --------------------------------------------------------------------------

REST_FRAMEWORK_DEV_OVERRIDES = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/hour',
        'user': '10000/hour',
    },
}

# Merge dev overrides into REST_FRAMEWORK
from .base import REST_FRAMEWORK  # noqa: E402
REST_FRAMEWORK.update(REST_FRAMEWORK_DEV_OVERRIDES)
