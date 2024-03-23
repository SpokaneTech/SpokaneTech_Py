import os

from celery import Celery
from celery.schedules import crontab

from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spokanetech.settings")

if settings.CELERY_ENABLED:
    app = Celery("core")
    app.config_from_object("django.conf:settings", namespace="CELERY")
    app.autodiscover_tasks()

    app.conf.beat_schedule = {
        "Scrape Events from Meetup": {
            "task": "web.tasks.scrape_events_from_meetup",
            "schedule": crontab(hour="0", minute="0"),
        },
        "Send Events to Discord": {
            "task": "web.tasks.send_events_to_discord",
            "schedule": crontab(day_of_week="mon", hour="0", minute="0"),
        },
    }
