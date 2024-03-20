from typing import Protocol
from datetime import timedelta

from django.utils import timezone

from web import models


class Sender(Protocol):
    def send(self, message: str, **kwargs) -> None:
        ...


class DiscordService:
    def __init__(self, sender: Sender) -> None:
        self.sender = sender

    def send_events(self) -> None:
        """Send upcoming events to the Discord server."""
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

        self.sender.send(message)
