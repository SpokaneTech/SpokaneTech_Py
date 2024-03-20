from enum import Enum
from typing import Protocol
from datetime import timedelta

from django.forms.models import model_to_dict
from django.utils import timezone

from web import models, scrapers

class Empty(Enum):
    """See https://peps.python.org/pep-0484/#support-for-singleton-types-in-unions"""
    token = 0

_empty = Empty.token


class MeetupService:

    def __init__(
        self,
        homepage_scraper: scrapers.Scraper[list[str]] | Empty = _empty,
        event_scraper: scrapers.Scraper[models.Event] | Empty = _empty,
    ) -> None:
        self.homepage_scraper: scrapers.Scraper[list[str]] = homepage_scraper if not isinstance(homepage_scraper, Empty) else scrapers.MeetupHomepageScraper()
        self.event_scraper: scrapers.Scraper[models.Event] = event_scraper if not isinstance(event_scraper, Empty) else scrapers.MeetupEventScraper()

    def scrape_events_from_meetup(self) -> None:
        """Scrape upcoming events from Meetup and save them to the database."""
        for tech_group in models.TechGroup.objects.filter(homepage__icontains="meetup.com"):
            event_urls = self.homepage_scraper.scrape(tech_group.homepage)  # type: ignore
            for event_url in event_urls:  # TODO: parallelize (with async?)
                event = self.event_scraper.scrape(event_url)
                models.Event.objects.update_or_create(
                    external_id=event.external_id,
                    defaults=model_to_dict(event, exclude=["id", "group"]),
                )


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
