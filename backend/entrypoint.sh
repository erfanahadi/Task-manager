#!/bin/sh
# exit immediately if any command fails
set -e

# Wait for the database to be ready
echo "Waiting for database..."
until python manage.py wait_for_db; do
  echo "Database unavailable, retrying in 2 seconds..."
  sleep 2
done

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Optionally collect static files (uncomment if needed)
# python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2
