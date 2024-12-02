#!/usr/bin/env bash

set -e

chown www-data:www-data /var/log

# Ждем запуск БД

# Применяем миграции
python manage.py migrate

# Собираем статику
python manage.py collectstatic --noinput

uwsgi --strict --ini uwsgi.ini
