from enum import Enum

from django.forms.models import model_to_dict

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
