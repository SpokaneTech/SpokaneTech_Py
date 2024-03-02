#!/bin/bash
set -e
cd ./src
python manage.py migrate
python manage.py collectstatic --noinput
