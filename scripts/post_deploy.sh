#!/bin/bash
set -e
cd ./src
python manage.py migrate
