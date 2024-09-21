import pathlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import freezegun
import pytest
import responses
from django.test import TestCase

from web import scrapers

BASE_DATA_DIR = pathlib.Path(__file__).parent / "data"


def mock_response(
    url: str,
    filepath: pathlib.Path,
) -> None:
    with open(filepath) as fin:
        body = fin.read()
    responses.get(url, body=body)


def mock_image_response(
    url: str,
    filepath: pathlib.Path,
) -> None:
    with open(filepath, "rb") as fin:
        body = fin.read()
    responses.get(url, body=body)


class TestMeetupHomepageScraper(TestCase):
    @freezegun.freeze_time("2024-03-18")
    @responses.activate
    def test_scraper_with_json(self):
        with open(pathlib.Path(__file__).parent / "data" / "meetup-homepage-with-json.html") as fin:
            body = fin.read()
        responses.get(
            "https://www.meetup.com/python-spokane/",
            body=body,
        )

        scraper = scrapers.MeetupHomepageScraper()
        actual = scraper.scrape("https://www.meetup.com/python-spokane/")

        expected = [
            "https://www.meetup.com/python-spokane/events/298213205/",
            "https://www.meetup.com/python-spokane/events/299750715/",
            "https://www.meetup.com/python-spokane/events/298346552/",
            "https://www.meetup.com/python-spokane/events/298346579/",
            # "https://www.meetup.com/python-spokane/events/298812750/",  # in the past
        ]
        assert actual == expected

    @freezegun.freeze_time("2024-03-18")
    @responses.activate
    def test_scraper_without_json(self):
        fin = open(pathlib.Path(__file__).parent / "data" / "meetup-homepage-with-json.html")
        body = fin.read()
        fin.close()
        responses.get(
            "https://www.meetup.com/python-spokane/",
            body=body,
        )

        scraper = scrapers.MeetupHomepageScraper()
        actual = scraper.scrape("https://www.meetup.com/python-spokane/")

        expected = [
            "https://www.meetup.com/python-spokane/events/298213205/",
            "https://www.meetup.com/python-spokane/events/299750715/",
            "https://www.meetup.com/python-spokane/events/298346552/",
            "https://www.meetup.com/python-spokane/events/298346579/",
            # "https://www.meetup.com/python-spokane/events/298812750/",  # in the past
        ]
        assert actual == expected


class TestMeetupEventScraper(TestCase):
    @responses.activate
    def test_scraper_with_json(self):
        # Arrange
        with open(pathlib.Path(__file__).parent / "data" / "meetup-with-json.html") as fin:
            body = fin.read()
        responses.get(
            "https://www.meetup.com/python-spokane/events/298213205/",
            body=body,
        )

        with open(pathlib.Path(__file__).parent / "data" / "meetup-image.jpeg", "rb") as fin:
            body = fin.read()
        responses.get(
            "https://secure.meetupstatic.com/photos/event/1/0/a/e/highres_519844270.jpeg",
            body=body,
        )

        # Act
        scraper = scrapers.MeetupEventScraper()
        actual, actual_tags, actual_image_result = scraper.scrape(
            "https://www.meetup.com/python-spokane/events/298213205/"
        )

        assert actual.name == "Dagger with Spokane Tech 🚀"
        assert actual.description and actual.description.startswith("Join us for our monthly SPUG meetup!")
        assert actual.date_time == datetime(2024, 3, 19, 18, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
        assert actual.duration == timedelta(hours=1, minutes=30)
        assert actual.location == "1720 W 4th Ave Unit B, Spokane, WA"
        assert actual.url == "https://www.meetup.com/python-spokane/events/298213205/"
        assert actual.external_id == "298213205"

        assert len(actual_tags) == 5
        assert {t.value for t in actual_tags} == {
            "Linux",
            "Python",
            "Django",
            "Python Web Development",
            "Agile and Scrum",
        }

        assert actual_image_result
        assert actual_image_result[0] == "highres_519844270.jpeg"
        assert len(actual_image_result[1]) > 0

    @responses.activate
    def test_scraper_without_json(self):
        # Arrange
        mock_response(
            "https://www.meetup.com/python-spokane/events/298213205/",
            BASE_DATA_DIR / "meetup-without-json.html",
        )
        mock_image_response(
            "https://secure.meetupstatic.com/photos/event/1/0/a/e/600_519844270.webp?w=750",
            BASE_DATA_DIR / "meetup-image.webp",
        )

        # Act
        scraper = scrapers.MeetupEventScraper()
        actual, actual_tags, actual_image_result = scraper.scrape(
            "https://www.meetup.com/python-spokane/events/298213205/"
        )

        # Assert
        assert actual.name == "Dagger with Spokane Tech 🚀"
        assert actual.description and actual.description.startswith("Join us for our monthly SPUG meetup!")
        assert actual.date_time == datetime(2024, 3, 19, 18, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
        assert actual.duration == timedelta(hours=1, minutes=30)
        assert actual.location == "1720 W 4th Ave Unit B, Spokane, WA"
        assert actual.url == "https://www.meetup.com/python-spokane/events/298213205/"
        assert actual.external_id == "298213205"
        assert len(actual_tags) == 5
        assert {t.value for t in actual_tags} == {
            "Linux",
            "Python",
            "Django",
            "Python Web Development",
            "Agile and Scrum",
        }

        assert actual_image_result
        assert actual_image_result[0] == "600_519844270.webp"
        assert len(actual_image_result[1]) > 0


@pytest.mark.eventbrite
class TestEventbriteScraper(TestCase):
    """
    The Eventbrite API requires a (free) API token,
    rather than requiring that each contributer maintain their own token,
    theses tests are not included in by default.

    To run them, set the `EVENTBRITE_API_TOKEN` envrionment variable.
    """

    @responses.activate
    def test_scraper(self):
        # Arrange
        mock_response(
            "https://www.eventbriteapi.com/v3/organizers/72020528223/events/",
            BASE_DATA_DIR / "eventbrite" / "organizer_events.json",
        )
        mock_response(
            "https://www.eventbriteapi.com/v3/venues/214450569/?expand=none",
            BASE_DATA_DIR / "eventbrite" / "event_venue.json",
        )
        mock_response(
            "https://www.eventbriteapi.com/v3/events/909447069667/description/",
            BASE_DATA_DIR / "eventbrite" / "event_description.json",
        )
        mock_image_response(
            "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F843746309%2F530357704049%2F1%2Foriginal.20240906-164727?auto=format%2Ccompress&q=75&sharp=10&s=09370c02bd3ab62907337f2e1ca8a61d",
            BASE_DATA_DIR / "eventbrite" / "event_image.jpg",
        )

        # Act
        scraper = scrapers.EventbriteScraper()
        organization_id = "72020528223"
        result = scraper.scrape(organization_id)

        # Assert
        event, tags, image_result = result[0]
        assert event.name == "3rd Annual - INCH360 Regional Cybersecurity Conference"
        assert event.description
        assert event.description.startswith("<div>Full Day of Panels, Speakers and Vendors on Cybersecurity,")
        assert event.date_time == datetime(2024, 10, 2, 8, 30, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
        assert event.duration == timedelta(hours=7, minutes=30)
        assert event.location == "702 East Desmet Avenue, Spokane, WA 99202"
        assert (
            event.url
            == "https://www.eventbrite.com/e/3rd-annual-inch360-regional-cybersecurity-conference-tickets-909447069667"
        )
        assert event.external_id == "909447069667"

        assert not tags

        assert image_result
        assert (
            image_result[0]
            == "https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F843746309%2F530357704049%2F1%2Foriginal.20240906-164727"
        )
        assert len(image_result[1]) > 0
