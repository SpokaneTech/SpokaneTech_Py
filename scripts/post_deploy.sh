#!/bin/bash
set -e
cd /code/src
python manage.py migrate
python manage.py collectstatic --noinput
