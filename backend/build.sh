#!/usr/bin/env bash
# exit on error
set -o errexit

echo "===> Upgrading pip..."
pip install --upgrade pip

echo "===> Installing requirements..."
if [ -f "requirements.txt" ]; then
    echo "Found requirements.txt in current directory"
    pip install -r requirements.txt
elif [ -f "backend/requirements.txt" ]; then
    echo "Found requirements.txt in backend directory"
    pip install -r backend/requirements.txt
else
    echo "Error: requirements.txt not found!"
    exit 1
fi

echo "===> Collecting static files and applying migrations..."
if [ -f "manage.py" ]; then
    python manage.py collectstatic --no-input --settings=config.settings.production
    python manage.py migrate --settings=config.settings.production
elif [ -f "backend/manage.py" ]; then
    python backend/manage.py collectstatic --no-input --settings=config.settings.production
    python backend/manage.py migrate --settings=config.settings.production
fi

echo "===> Ensuring admin superuser exists..."
python -c "
import os, sys
sys.path.append('backend') if os.path.isdir('backend') else None
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Created superuser: {username}')
else:
    u = User.objects.get(username=username)
    u.set_password(password)
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print(f'Updated superuser password: {username}')
"

echo "===> SmartCart build completed successfully!"

