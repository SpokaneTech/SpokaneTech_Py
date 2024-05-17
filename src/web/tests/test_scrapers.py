import pathlib
from datetime import datetime, timedelta

import freezegun
import responses
from django.test import TestCase
from web import models, scrapers
from zoneinfo import ZoneInfo


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
        fin = open(pathlib.Path(__file__).parent / "data" / "meetup-with-json.html")
        body = fin.read()
        fin.close()
        responses.get(
            "https://www.meetup.com/python-spokane/events/298213205/",
            body=body,
        )

        scraper = scrapers.MeetupEventScraper()
        actual, actual_tags = scraper.scrape("https://www.meetup.com/python-spokane/events/298213205/")

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

    @responses.activate
    def test_scraper_without_json(self):
        fin = open(pathlib.Path(__file__).parent / "data" / "meetup-without-json.html")
        body = fin.read()
        fin.close()
        responses.get(
            "https://www.meetup.com/python-spokane/events/298213205/",
            body=body,
        )

        scraper = scrapers.MeetupEventScraper()
        actual, actual_tags = scraper.scrape("https://www.meetup.com/python-spokane/events/298213205/")

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


class TestEventbriteScraper(TestCase):
    def test_scraper(self):
        scraper = scrapers.EventbriteScraper()
        result = scraper.scrape("72020528223")
        actual: models.Event = result[0][0]
        assert actual.name == "Spring Cyber - Training Series"
        assert actual.description and actual.description.startswith(
            "<div>Deep Dive into Pen Testing with white hacker Casey Davis"
        )
        assert actual.date_time == datetime(2024, 5, 23, 16, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
        assert actual.duration == timedelta(hours=1, minutes=30)
        assert actual.location == "2818 North Sullivan Road #Suite 100, Spokane Valley, WA 99216"
        assert actual.url == "https://www.eventbrite.com/e/spring-cyber-training-series-tickets-860181354587"
        assert actual.external_id == "860181354587"
