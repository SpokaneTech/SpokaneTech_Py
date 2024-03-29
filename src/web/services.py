from typing import Protocol
from datetime import timedelta

from django.forms.models import model_to_dict
from django.utils import timezone

from web import models, scrapers


class MeetupService:
    def __init__(
        self,
        homepage_scraper: scrapers.Scraper[list[str]] | None = None,
        event_scraper: scrapers.Scraper[models.Event] | None = None,
    ) -> None:
        self.homepage_scraper: scrapers.Scraper[list[str]] = homepage_scraper or scrapers.MeetupHomepageScraper()
        self.event_scraper: scrapers.Scraper[models.Event] = event_scraper or scrapers.MeetupEventScraper()

    def scrape_events_from_meetup(self) -> None:
        """Scrape upcoming events from Meetup and save them to the database."""
        for tech_group in models.TechGroup.objects.filter(homepage__icontains="meetup.com"):
            event_urls = self.homepage_scraper.scrape(tech_group.homepage)  # type: ignore
            for event_url in event_urls:  # TODO: parallelize (with async?)
                event = self.event_scraper.scrape(event_url)
                event.group = tech_group
                defaults = model_to_dict(event, exclude=["id"])
                defaults["group"] = tech_group
                models.Event.objects.update_or_create(
                    external_id=event.external_id,
                    defaults=defaults,
                )


class Sender(Protocol):
    def send(self, message: str, **kwargs) -> None:
        """Send a message somewhere."""
        ...


class DiscordService:
    def __init__(self, sender: Sender) -> None:
        self.sender = sender

    def send_events(self) -> None:
        """Send upcoming events to the Discord server."""
        today = timezone.localdate()
        events = (
            models.Event.objects.filter(
                date_time__gte=today,
                date_time__lt=today + timedelta(days=7),
            )
            .select_related("group")
            .order_by("date_time")
        )

        message = "_Here are the upcoming Spokane Tech events for this week:_\n\n"
        for event in events:
            event_url = event.url if event.url else f"https://spokanetech.org{event.get_absolute_url()}"
            event_msg = f"**{event.date_time.strftime('%A, %b %d @ %-I:%M %p')}**\n"
            if event.group:
                event_msg += f"{event.group.name} — "
            event_msg += f"[{event.name}](<{event_url}>)"
            message += event_msg + "\n\n"

        self.sender.send(message)
