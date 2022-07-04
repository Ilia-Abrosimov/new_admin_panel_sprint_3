#!/bin/sh
echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"


echo "Waiting for elastic..."

    while ! nc -z $Elastic_host $ES_PORT; do
      sleep 0.1
    done

    echo "Elastic started"

python manage.py migrate movies 0001 --fake
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn --bind 0.0.0.0:8000 config.wsgi
exec "$@"