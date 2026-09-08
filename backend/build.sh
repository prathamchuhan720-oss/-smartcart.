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

echo "===> SmartCart build completed successfully!"
