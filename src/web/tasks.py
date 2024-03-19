from datetime import timedelta

from discord import SyncWebhook

from django.conf import settings
from django.template import loader
from django.utils import timezone

from web.models import Event


def send_events():
    webhook = SyncWebhook.from_url(settings.DISCORD_WEBHOOK_URL)
    today = timezone.localdate()
    events = Event.objects.filter(
        date_time__gte=today,
        date_time__lt=today + timedelta(days=7),
    )
    message = loader.render_to_string("web/discord/events.md", {"events": events})
    webhook.send(message)
