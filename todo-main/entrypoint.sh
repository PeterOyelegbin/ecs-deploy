#!/bin/sh

echo "Waiting for MySQL to be ready..."
while ! nc -z mysql 3306; do
  sleep 1
done

echo "MySQL is up! Running migrations..."
python manage.py migrate

echo "Starting Gunicorn..."
gunicorn todo.wsgi:application --bind 0.0.0.0:8000
