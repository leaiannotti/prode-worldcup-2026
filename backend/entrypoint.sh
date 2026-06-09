#!/bin/sh
set -e

echo "Running database migrations..."
flask db upgrade 2>/dev/null || {
    echo "Migration failed, stamping current state and retrying..."
    flask db stamp head
    flask db upgrade
}

echo "Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 "app:create_app()"
