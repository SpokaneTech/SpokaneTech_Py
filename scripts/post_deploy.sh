#!/bin/bash
set -e
cd ./src
python manage.py migrate

# `node_modules` static folder is huge so ignore it
# If `node_modules` is updated, run collectstatic manually
# python manage.py collectstatic --noinput -v=2 --ignore node_modules
