from django.test import TestCase
from django.utils import timezone

from web import models, scrapers, services


class MockMeetupHomepageScraper(scrapers.Scraper[list[str]]):
    def scrape(self, url: str) -> list[str]:
        return ["https://www.meetup.com/python-spokane/events/298213205/"]


class MockMeetupEventScraper(scrapers.Scraper[models.Event]):

    EXTERNAL_ID = "298213205"

    def __init__(self) -> None:
        self._call_count = 0

    def scrape(self, url: str) -> models.Event:
        self._call_count += 1
        
        if self._call_count == 1:
            return models.Event(
                name = "March Meetup 2024",
                description = "TBD",
                date_time = timezone.localtime(),
                external_id = self.EXTERNAL_ID,
            )
        
        return models.Event(
            name = "Intro to Dagger",
            description = "Super cool intro to Dagger CI/CD!",
            date_time = timezone.localtime(),
            external_id = self.EXTERNAL_ID,
        )


class TestMeetupService(TestCase):

    def test_updates_event_instead_of_creating_new_one(self):
        # Arrange
        models.TechGroup.objects.create(
            name="Spokane Python User Group",
            homepage="https://www.meetup.com/Python-Spokane/",
        )
    
        meetup_service = services.MeetupService(
            MockMeetupHomepageScraper(),
            MockMeetupEventScraper(),
        )

        # Act
        meetup_service.scrape_events_from_meetup()
        meetup_service.scrape_events_from_meetup()

        # Assert
        assert models.Event.objects.count() == 1
        
        event = models.Event.objects.get()
        assert event.name == "Intro to Dagger"
        assert event.description == "Super cool intro to Dagger CI/CD!"
        assert event.external_id == MockMeetupEventScraper.EXTERNAL_ID


