from django.test import TestCase
from django.utils import timezone

from web import models, scrapers, services


class MockMeetupHomepageScraper(scrapers.Scraper[list[str]]):
    def scrape(self, url: str) -> list[str]:
        return ["https://www.meetup.com/python-spokane/events/298213205/"]


class MockMeetupEventScraper(scrapers.Scraper[scrapers.MeetUpEventScraperResult]):
    EXTERNAL_ID = "298213205"

    def __init__(self) -> None:
        self._call_count = 0

    def scrape(self, url: str) -> scrapers.MeetUpEventScraperResult:
        self._call_count += 1

        if self._call_count == 1:
            return (
                models.Event(
                    name="March Meetup 2024",
                    description="TBD",
                    date_time=timezone.localtime(),
                    external_id=self.EXTERNAL_ID,
                ),
                [
                    models.Tag(value="Linux"),
                    models.Tag(value="Python"),
                    models.Tag(value="Django"),
                    models.Tag(value="Agile and Scrum"),
                    models.Tag(value="Python Web Development"),
                ],
            )

        return (
            models.Event(
                name="Intro to Dagger",
                description="Super cool intro to Dagger CI/CD!",
                date_time=timezone.localtime(),
                external_id=self.EXTERNAL_ID,
            ),
            [
                models.Tag(value="Linux"),
                models.Tag(value="Python"),
                models.Tag(value="Django"),
                models.Tag(value="Agile and Scrum"),
                models.Tag(value="Python Web Development"),
            ],
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

    def test_manually_applied_tags_are_not_overriden(self):
        # Arrange
        tags = {
            models.Tag.objects.create(value="Python"),  # Tagged on Meetup
            models.Tag.objects.create(value="MortonSalt"),  # Not tagged on Meetup
        }

        models.TechGroup.objects.create(
            name="Spokane Python User Group",
            homepage="https://www.meetup.com/Python-Spokane/",
        )

        meetup_service = services.MeetupService(
            MockMeetupHomepageScraper(),
            MockMeetupEventScraper(),
        )

        meetup_service.scrape_events_from_meetup()

        event = models.Event.objects.get()
        for tag in tags:
            event.tags.add(tag)

        # Act
        meetup_service.scrape_events_from_meetup()

        # Assert
        assert models.Event.objects.count() == 1
        event = models.Event.objects.get()

        model_tags = event.tags.all()
        assert tags.issubset(model_tags)

    def test_scraped_tags_are_attached_to_event(self):
        expected_tags = {
            models.Tag.objects.create(value="Linux"),
            models.Tag.objects.create(value="Python"),
            models.Tag.objects.create(value="Django"),
            models.Tag.objects.create(value="Agile and Scrum"),
            models.Tag.objects.create(value="Python Web Development"),
        }
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

        event = models.Event.objects.get()
        tags = event.tags

        assert tags.count() == 5
        assert set(tags.all()) == expected_tags
