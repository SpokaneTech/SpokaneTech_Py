import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spokanetech.settings")

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "Scrape Events from Meetup": {
        "task": "web.tasks.scrape_events_from_meetup",
        "schedule": crontab(hour="0"),
    },
    "Send Events to Discord": {
        "task": "web.tasks.send_events_to_discord",
        "schedule": crontab(day_of_week="mon"),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
