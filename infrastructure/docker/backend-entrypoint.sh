#!/usr/bin/env sh
set -eu

cd /app/backend

role="${1:-web}"

if [ "$role" = "web" ]; then
  python manage.py migrate --noinput
  python manage.py seed_demo || true
  exec python manage.py runserver 0.0.0.0:8000
fi

if [ "$role" = "worker" ]; then
  exec celery -A config worker -l info
fi

if [ "$role" = "beat" ]; then
  exec celery -A config beat -l info
fi

exec "$@"
