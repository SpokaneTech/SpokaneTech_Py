flower: sleep 5 && python -m celery --workdir ./src -A spokanetech.celery flower
worker: python -m celery --workdir ./src -A spokanetech.celery worker -B -l INFO --events
