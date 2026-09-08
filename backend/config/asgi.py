"""
ASGI config for SmartCart project.

Exposes the ASGI callable as a module-level variable named ``application``.
For more information see:
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

application = get_asgi_application()
