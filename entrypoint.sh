#!/bin/sh

# Appliquer les migrations à chaque démarrage 
python manage.py migrate --noinput

# Collecte statique si en prod
if [ "$DJANGO_ENV" = "prod" ]; then
    python manage.py collectstatic --noinput
    exec gunicorn cinephoria_app.wsgi:application --bind 0.0.0.0:8000
else
    exec python manage.py runserver 0.0.0.0:8000
fi
