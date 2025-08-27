#!/usr/bin/env sh
set -e

WAIT_FOR_REDIS_HOST=${WAIT_FOR_REDIS_HOST:-redis}
WAIT_FOR_REDIS_PORT=${WAIT_FOR_REDIS_PORT:-6379}
WAIT_FOR_ZAP_HOST=${WAIT_FOR_ZAP_HOST:-zap}
WAIT_FOR_ZAP_PORT=${WAIT_FOR_ZAP_PORT:-8080}

# Wait for Redis
echo "Waiting for Redis at $WAIT_FOR_REDIS_HOST:$WAIT_FOR_REDIS_PORT..."
for i in $(seq 1 60); do
  if nc -z "$WAIT_FOR_REDIS_HOST" "$WAIT_FOR_REDIS_PORT" 2>/dev/null; then
    echo "Redis is up"; break
  fi
  sleep 1
  if [ "$i" = "60" ]; then echo "Redis not reachable"; fi
done

# Wait for ZAP
echo "Waiting for ZAP at $WAIT_FOR_ZAP_HOST:$WAIT_FOR_ZAP_PORT..."
for i in $(seq 1 120); do
  if nc -z "$WAIT_FOR_ZAP_HOST" "$WAIT_FOR_ZAP_PORT" 2>/dev/null; then
    echo "ZAP is up"; break
  fi
  sleep 1
done

python manage.py migrate --noinput
python manage.py startup_scan || true

if [ "$RUN_CELERY" = "worker" ]; then
  exec celery -A vapt_platform worker --loglevel=info
fi

exec gunicorn vapt_platform.wsgi:application --bind 0.0.0.0:8000 --workers 3


