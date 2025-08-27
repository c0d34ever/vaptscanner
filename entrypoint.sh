#!/usr/bin/env sh
set -e

python manage.py migrate --noinput

if [ "$RUN_CELERY" = "worker" ]; then
  exec celery -A vapt_platform worker --loglevel=info
fi

exec gunicorn vapt_platform.wsgi:application --bind 0.0.0.0:8000 --workers 3


