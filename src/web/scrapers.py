import json
import pathlib
import re
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Protocol, TypeAlias, TypeVar

import requests
import zoneinfo
from bs4 import BeautifulSoup, Tag
from django.utils import timezone

from web import models

ST = TypeVar("ST", covariant=True)


class Scraper(Protocol[ST]):
    def scrape(self, url: str) -> ST:
        """Scrape the URL and return a typed object."""
        ...


MeetUpEventScraperResult: TypeAlias = tuple[models.Event, list[models.Tag]]


class MeetupScraperMixin:
    """Common Meetup scraping functionality."""

    def _parse_apollo_state(self, soup: BeautifulSoup) -> dict:
        next_data = soup.find_all(attrs={"id": "__NEXT_DATA__"})[0].text
        next_data = json.loads(next_data)
        apollo_state: dict[str, Any] = next_data["props"]["pageProps"]["__APOLLO_STATE__"]
        return apollo_state

    def _parse_events_json(self, apollo_state: dict) -> list[dict]:
        event_keys = [key for key in apollo_state.keys() if key.split(":")[0] == "Event"]
        return [apollo_state[key] for key in event_keys]


class MeetupHomepageScraper(MeetupScraperMixin, Scraper[list[str]]):
    """Scrape a list of upcoming events from a Meetup group's home page."""

    def __init__(self) -> None:
        self.event_scraper = MeetupEventScraper()

        naive_now = datetime.now()
        self._now = timezone.localtime()
        # See https://gist.github.com/ajosephau/2a22698faaf6206ce195c7aa78e48247
        self._timezones_by_abbreviation = {
            zoneinfo.ZoneInfo(tz).tzname(naive_now): tz for tz in zoneinfo.available_timezones()
        }

    def scrape(self, url: str) -> list[str]:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        try:
            apollo_state = self._parse_apollo_state(soup)
        except LookupError:
            apollo_state = {}

        if apollo_state:
            event_urls = self._parse_event_urls_from_state(apollo_state)
        else:
            upcoming_section = soup.find_all(id="upcoming-section")[0]
            events = upcoming_section.find_all_next(id=re.compile(r"event-card-"))
            filtered_event_containers = [event for event in events if self._filter_event_tag(event)]
            event_urls = [event_container["href"] for event_container in filtered_event_containers]

        return event_urls

    def _parse_event_urls_from_state(self, apollo_state: dict) -> list[str]:
        events = self._parse_events_json(apollo_state)
        future_events = [event for event in events if datetime.fromisoformat(event["dateTime"]) > self._now]
        future_events = sorted(future_events, key=lambda event: datetime.fromisoformat(event["dateTime"]))
        future_event_urls = [event["eventUrl"] for event in future_events]
        return future_event_urls

    def _filter_event_tag(self, event: Tag) -> bool:
        time: str = event.find_all("time")[0].text
        time, tz_abbrv = time.rsplit(maxsplit=1)
        tz = self._timezones_by_abbreviation[tz_abbrv]
        tz = zoneinfo.ZoneInfo(tz)
        event_datetime = datetime.strptime(time, "%a, %b %d, %Y, %I:%M %p").astimezone(tz)
        return event_datetime > self._now


class MeetupEventScraper(MeetupScraperMixin, Scraper[MeetUpEventScraperResult]):
    """Scrape an Event from a Meetup details page."""

    DURATION_PATTERN = re.compile(r"1?\d:\d{2} [AP]M to 1?\d:\d{2} [AP]M")

    def scrape(self, url: str) -> MeetUpEventScraperResult:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        try:
            apollo_state = self._parse_apollo_state(soup)
            event_json = self._parse_events_json(apollo_state)[0]
        except LookupError:
            event_json = {}

        if event_json:
            name = event_json["title"]
            description = event_json["description"]
            date_time = datetime.fromisoformat(event_json["dateTime"])
            end_time = datetime.fromisoformat(event_json["endTime"])
            duration = end_time - date_time
            location_data = apollo_state[event_json["venue"]["__ref"]]
            location = f"{location_data['address']}, {location_data['city']}, {location_data['state']}"
            external_id = event_json["id"]
        else:
            name = self._parse_name(soup)
            description = self._parse_description(soup)
            date_time = self._parse_date_time(soup)
            duration = self._parse_duration(soup)
            location = self._parse_location(soup)
            external_id = self._parse_external_id(url)

        tags = self._parse_tags(soup)
        return (
            models.Event(
                name=name,
                description=description,
                date_time=date_time,
                duration=duration,
                location=location,
                external_id=external_id,
                url=url,
            ),
            tags,
        )

    def _parse_name(self, soup: BeautifulSoup) -> str:
        name: str = soup.find_all("h1")[0].text
        name = " ".join(name.split())
        return name

    def _parse_description(self, soup: BeautifulSoup) -> str:
        description: str = soup.find_all(attrs={"id": "event-details"})[0].text
        description = description.lstrip()
        if description.startswith("Details"):
            description = description[len("Details") :].lstrip()
        return description

    def _parse_date_time(self, soup: BeautifulSoup) -> datetime:
        return datetime.fromisoformat(soup.find_all("time")[0]["datetime"])

    def _parse_duration(self, soup: BeautifulSoup) -> timedelta:
        time: Tag = soup.find_all("time")[0]
        matches = self.DURATION_PATTERN.findall(time.text)
        if not matches:
            raise ValueError("Could not find duration from:", time.text)
        start_time, end_time = matches[0].split(" to ")
        start_time = datetime.strptime(start_time, "%I:%M %p")
        end_time = datetime.strptime(end_time, "%I:%M %p")
        return end_time - start_time

    def _parse_location(self, soup: BeautifulSoup) -> str:
        location: str = soup.find_all(attrs={"data-testid": "location-info"})[0].text
        location = " ".join((line.strip() for line in location.splitlines()))
        location = location.replace(" · ", ", ")
        return location

    def _parse_external_id(self, url: str) -> str:
        parsed_url = urllib.parse.urlparse(url).path
        external_id = pathlib.PurePosixPath(urllib.parse.unquote(parsed_url)).parts[-1]
        return external_id

    def _parse_tags(self, soup: BeautifulSoup) -> list[models.Tag]:
        tags = soup.find_all("a", id=re.compile("topics-link-"))
        tags = [re.sub(r"\s+", " ", t.text) for t in tags]  # Some tags have newlines & extra spaces
        return [models.Tag(value=t) for t in tags]
