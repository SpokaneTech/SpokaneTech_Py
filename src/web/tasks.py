from datetime import timedelta

from celery import shared_task
from discord import SyncWebhook

from django.conf import settings
from django.utils import timezone

from web import models


@shared_task()
def send_events_to_discord():
    """Send upcoming events to the Discord server."""
    webhook = SyncWebhook.from_url(settings.DISCORD_WEBHOOK_URL)
    today = timezone.localdate()
    events = models.Event.objects.filter(
        date_time__gte=today,
        date_time__lt=today + timedelta(days=7),
    ).select_related("group").order_by("date_time")

    message = "_Here are the upcoming Spokane Tech events for this week:_\n\n"
    for event in events:
        event_url = event.url if event.url else f"https://spokanetech.org{event.get_absolute_url()}"
        event_msg = f"**{event.date_time.strftime('%A, %b %d @ %-I:%M %p')}**\n"
        if event.group:
            event_msg += f"{event.group.name} — "
        event_msg += f"[{event.name}](<{event_url}>)"
        message += event_msg + "\n\n"

    webhook.send(message)
