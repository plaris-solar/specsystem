#!/usr/bin/env bash
# start-server.sh
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    python manage.py createsuperuser --no-input
fi

if [ -f /app/ext/static/config/nginx.conf ]; then
    cp /app/ext/static/config/nginx.conf /etc/nginx
fi

if [ -f /app/ext/static/config/settings_local.py ]; then
    cp /app/ext/static/config/settings_local.py /app/proj/
fi

gunicorn proj.wsgi --bind 0.0.0.0:8010 --workers 3 &
nginx -g "daemon off;"