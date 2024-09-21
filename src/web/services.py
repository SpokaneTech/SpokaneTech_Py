from datetime import timedelta
from typing import Protocol

from django.core.files.base import ContentFile
from django.forms.models import model_to_dict
from django.utils import timezone

from web import models, scrapers


class EventService:
    def save_event_from_result(
        self,
        result: scrapers.EventScraperResult,
        tech_group: models.TechGroup,
    ) -> None:
        event, tags, image_result = result
        event = self._save_event(event, tech_group)
        self._save_tags(event, tags)
        if image_result is not None:
            self._save_image(event, image_result)

    def _save_event(
        self,
        event: models.Event,
        tech_group: models.TechGroup,
    ) -> models.Event:
        event.group = tech_group
        event.approved_at = timezone.localtime()
        defaults = model_to_dict(event, exclude=["id"])
        defaults["group"] = tech_group

        del defaults["tags"]  # Can't apply Many-to-Many relationship untill after the event has been saved.
        del defaults["image"]

        updated_event, _ = models.Event.objects.update_or_create(
            external_id=event.external_id,
            defaults=defaults,
        )
        return updated_event

    def _save_tags(
        self,
        event: models.Event,
        tags: list[models.Tag],
    ) -> None:
        for tag in tags:
            tag, _ = models.Tag.objects.get_or_create(value=tag)
            event.tags.add(tag)

    def _save_image(
        self,
        event: models.Event,
        image_result: scrapers.ImageResult,
    ) -> None:
        image_name, image = image_result

        # If images are the same, don't re-upload
        has_existing_image = bool(event.image)
        if has_existing_image:
            existing_image = event.image.read()
            if existing_image == image:
                return

        file = ContentFile(image, name=image_name)
        event.image.save(image_name, file)


class MeetupService:
    def __init__(
        self,
        homepage_scraper: scrapers.Scraper[list[str]] | None = None,
        event_scraper: scrapers.Scraper[scrapers.EventScraperResult] | None = None,
        event_service: EventService | None = None,
    ) -> None:
        self.homepage_scraper: scrapers.Scraper[list[str]] = homepage_scraper or scrapers.MeetupHomepageScraper()
        self.event_scraper: scrapers.Scraper[scrapers.EventScraperResult] = (
            event_scraper or scrapers.MeetupEventScraper()
        )
        self.event_service = event_service or EventService()

    def save_events(self) -> None:
        """Scrape upcoming events from Meetup and save them to the database."""
        for tech_group in models.TechGroup.objects.filter(homepage__icontains="meetup.com"):
            event_urls = self.homepage_scraper.scrape(tech_group.homepage)  # type: ignore
            for event_url in event_urls:  # TODO: parallelize (with async?)
                result = self.event_scraper.scrape(event_url)
                self.event_service.save_event_from_result(result, tech_group)


class EventbriteService:
    events_scraper: scrapers.Scraper[list[scrapers.EventScraperResult]]

    def __init__(
        self,
        events_scraper: scrapers.Scraper[list[scrapers.EventScraperResult]] | None = None,
        event_service: EventService | None = None,
    ) -> None:
        self.events_scraper = events_scraper or scrapers.EventbriteScraper()
        self.event_service = event_service or EventService()

    def save_events(self) -> None:
        """Fetch upcoming events from Eventbrite and save them.

        Note: this uses an API and doesn't actually web scrape.
        """
        for eventbrite_organization in models.EventbriteOrganization.objects.prefetch_related("tech_group"):
            tech_group = eventbrite_organization.tech_group
            results = self.events_scraper.scrape(eventbrite_organization.eventbrite_id)
            for result in results:
                self.event_service.save_event_from_result(result, tech_group)


class Sender(Protocol):
    def send(self, message: str, **kwargs) -> None:
        """Send a message somewhere."""
        ...


class DiscordService:
    def __init__(self, sender: Sender) -> None:
        self.sender = sender

    def send_events(self) -> None:
        """Send upcoming events to the Discord server."""
        today = timezone.localtime()
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
            unix_timestamp = int(event.date_time.timestamp())
            event_msg = f"**<t:{unix_timestamp}:F>**\n"
            if event.group:
                event_msg += f"{event.group.name} — "
            event_msg += f"[{event.name}](<{event_url}>)"
            message += event_msg + "\n\n"

        self.sender.send(message)
