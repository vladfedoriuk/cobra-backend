#!/bin/bash

find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

python manage.py migrate

if [ "$1" = "run_cobra_dev" ]; then
  python manage.py runserver 0.0.0.0:8000
fi

if [ "$1" = "run_celery_dev" ]; then
	celery --app=cobra worker --loglevel=info --logfile=logs/celery.log
fi
