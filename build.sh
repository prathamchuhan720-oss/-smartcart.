#!/usr/bin/env bash
# exit on error
set -o errexit

echo "===> Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "===> Collecting static files..."
python backend/manage.py collectstatic --no-input --settings=config.settings.production

echo "===> Applying database migrations..."
python backend/manage.py migrate --settings=config.settings.production

echo "===> SmartCart build completed successfully!"
