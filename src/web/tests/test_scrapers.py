from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pathlib

import freezegun
import responses

from django.test import TestCase

from web import scrapers


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
        actual = scraper.scrape("https://www.meetup.com/python-spokane/events/298213205/")

        assert actual.name == "Dagger with Spokane Tech 🚀"
        assert actual.description and actual.description.startswith("Join us for our monthly SPUG meetup!")
        assert actual.date_time == datetime(2024, 3, 19, 18, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
        assert actual.duration == timedelta(hours=1, minutes=30)
        assert actual.location == "1720 W 4th Ave Unit B, Spokane, WA"
        assert actual.url == "https://www.meetup.com/python-spokane/events/298213205/"
        assert actual.external_id == "298213205"

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
        actual = scraper.scrape("https://www.meetup.com/python-spokane/events/298213205/")

        assert actual.name == "Dagger with Spokane Tech 🚀"
        assert actual.description and actual.description.startswith("Join us for our monthly SPUG meetup!")
        assert actual.date_time == datetime(2024, 3, 19, 18, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
        assert actual.duration == timedelta(hours=1, minutes=30)
        assert actual.location == "1720 W 4th Ave Unit B, Spokane, WA"
        assert actual.url == "https://www.meetup.com/python-spokane/events/298213205/"
        assert actual.external_id == "298213205"


class TestEventbriteScraper(TestCase):

    def test_scraper(self):
        scraper = scrapers.EventbriteScraper()
        scraper.scrape("72020528223")

    def test_blah(self):
        from eventbrite.models import EventbriteObject

        scraper = scrapers.EventbriteScraper()
        client = scraper.client
        user_response: EventbriteObject = client.get_user()  # type: ignore
        user_id = user_response.id
        events_response = client.get_user_events(user_id)
        pass
    


    def test_manual(self):
        import os
        import requests

        organization_id = "72020528223"  # actually 1773924472233
        headers = {
            'Authorization': f'Bearer {os.environ["EVENTBRITE_API_TOKEN"]}'
        }
        # response = requests.get(f'https://www.eventbriteapi.com/v3/organizations/{organization_id}/events/', headers=headers)

        user_url = "/users/me/?expand=assortment"
        response = requests.get("https://www.eventbriteapi.com/v3" + user_url, headers=headers)

        response_body = response.content
        print(response_body)
