#! /usr/bin/sh
python ./simple_project/manage.py manage.py createsuperuser --noinput --username admin --email admin@example.com
python ./simple_project/manage.py runserver
python ./etl/main.py
