from celery import shared_task
from discord import SyncWebhook

from django.conf import settings

from web import services


@shared_task()
def send_events_to_discord():
    """Send upcoming events to the Discord server."""
    webhook = SyncWebhook.from_url(settings.DISCORD_WEBHOOK_URL)
    service = services.DiscordService(webhook)  # type: ignore
    service.send_events()
