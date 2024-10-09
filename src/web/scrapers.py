import functools
import json
import pathlib
import re
import urllib.parse
import zoneinfo
from datetime import datetime, timedelta
from typing import Any, Protocol, TypeAlias, TypeVar

import eventbrite.access_methods
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from django.conf import settings
from django.utils import timezone
from eventbrite import Eventbrite

from web import models

ST = TypeVar("ST", covariant=True)


# monkeypatch eventbrite module
# TODO: make our own eventbrite package that is up to date
def get_venue(self, id, **data):
    return self.get("/venues/{0}/".format(id), data=data)


def get_event_description(self, id, **data):
    return self.get("/events/{0}/description/".format(id), data=data)


setattr(eventbrite.access_methods.AccessMethodsMixin, "get_venue", get_venue)
setattr(eventbrite.access_methods.AccessMethodsMixin, "get_event_description", get_event_description)


class Scraper(Protocol[ST]):
    def scrape(self, url: str) -> ST:
        """Scrape the URL and return a typed object."""
        ...


ImageResult: TypeAlias = tuple[str, bytes]
EventScraperResult: TypeAlias = tuple[models.Event, list[models.Tag], ImageResult | None]


class ScraperMixin:
    def _get_image(self, image_url: str) -> ImageResult:
        image_name = self._parse_image_name(image_url)
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        image = response.content
        return image_name, image

    def _parse_image_name(self, image_url: str) -> str:
        return image_url.rsplit("/", maxsplit=1)[-1].split("?", maxsplit=1)[0]


class MeetupScraperMixin(ScraperMixin):
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
            filtered_event_containers: list[Tag] = [event for event in events if self._filter_event_tag(event)]  # type: ignore
            event_urls: list[str] = [event_container["href"] for event_container in filtered_event_containers]  # type: ignore

        return [url for url in event_urls if self._filter_repeating_events(url)]

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

    def _filter_repeating_events(self, url: str) -> bool:
        # For repeating events, future ones (i.e. not the next one)
        # have alphanumeric event urls. Whereas on-off events,
        # previous and next repeating events have numeric event urls.
        return bool(re.search(r"events/(\d*)/", url))


class MeetupEventScraper(MeetupScraperMixin, Scraper[EventScraperResult]):
    """Scrape an Event from a Meetup details page."""

    DURATION_PATTERN = re.compile(r"1?\d:\d{2} [AP]M to 1?\d:\d{2} [AP]M")

    def scrape(self, url: str) -> EventScraperResult:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        try:
            apollo_state = self._parse_apollo_state(soup)
            event_json = self._parse_events_json(apollo_state)[0]
        except LookupError:
            event_json = {}

        try:
            name = event_json["title"]
            description = event_json["description"]
            date_time = datetime.fromisoformat(event_json["dateTime"])
            end_time = datetime.fromisoformat(event_json["endTime"])
            duration = end_time - date_time
            location_data = apollo_state[event_json["venue"]["__ref"]]
            location = f"{location_data['address']}, {location_data['city']}, {location_data['state']}"
            external_id = event_json["id"]
        except (TypeError, KeyError):
            name = self._parse_name(soup)
            description = self._parse_description(soup)
            date_time = self._parse_date_time(soup)
            duration = self._parse_duration(soup)
            location = self._parse_location(soup)
            external_id = self._parse_external_id(url)

        try:
            event_photo = event_json["featuredEventPhoto"]["__ref"]
            image_url = apollo_state[event_photo].get("highResUrl", apollo_state[event_photo]["baseUrl"])
        except (TypeError, KeyError):
            image_url = self._parse_image(soup)

        image_result = None
        if image_url:
            image_result = self._get_image(image_url)

        tags = self._parse_tags(soup)
        event = models.Event(
            name=name,
            description=description,
            date_time=date_time,
            duration=duration,
            location=location,
            external_id=external_id,
            url=url,
        )
        return (event, tags, image_result)

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
        time: Tag | None = soup.find("time")  # type: ignore
        if not time:
            raise ValueError("could not find time")
        dt: str = time["datetime"]  # type: ignore
        return datetime.fromisoformat(dt)

    def _parse_duration(self, soup: BeautifulSoup) -> timedelta:
        time: Tag | None = soup.find("time")  # type: ignore
        if not time:
            raise ValueError("could not find time")
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

    def _parse_image(self, soup: BeautifulSoup) -> str | None:
        picture = soup.find(attrs={"data-testid": "event-description-image"})
        if not picture:
            return None
        img: Tag | None = picture.find("img")  # type: ignore
        if not img:
            return None
        src: str = img["src"]  # type: ignore
        return src


class EventbriteScraper(ScraperMixin, Scraper[list[EventScraperResult]]):
    def __init__(self, api_token: str | None = None):
        self.client = Eventbrite(api_token or settings.EVENTBRITE_API_TOKEN)
        self._location_by_venue_id: dict[str, str] = {}

    def scrape(self, organization_id: str) -> list[EventScraperResult]:
        response = self.client.get_organizer_events(
            organization_id,
            status="live",
            expand="logo",
        )
        if not str(response.status_code).startswith("2"):
            raise ValueError(response.status_code, response.reason)
        results = [self.map_to_event(eventbrite_event) for eventbrite_event in response["events"]]
        return results

    def map_to_event(self, eventbrite_event: dict) -> EventScraperResult:
        name = eventbrite_event["name"]["text"]
        start = datetime.fromisoformat(eventbrite_event["start"]["utc"])
        end = datetime.fromisoformat(eventbrite_event["end"]["utc"])
        duration = end - start
        external_id = eventbrite_event["id"]
        url = eventbrite_event["url"]
        venue_id = eventbrite_event["venue_id"]
        location = self._get_venue_location(venue_id)

        try:
            # full event description
            description = self.client.get_event_description(external_id)["description"]  # type: ignore
        except requests.RequestException:
            # short description
            description = eventbrite_event["description"]["html"]

        try:
            image_url = eventbrite_event["logo"]["original"]["url"]
            image_result = self._get_image(image_url)
        except (KeyError, requests.HTTPError):
            try:
                image_url = eventbrite_event["logo"]["url"]
                image_result = self._get_image(image_url)
            except KeyError:
                image_result = None

        event = models.Event(
            name=name,
            description=description,
            date_time=start,
            duration=duration,
            location=location,
            external_id=external_id,
            url=url,
        )

        # tags: list[models.Tag] = []
        # category_id = eventbrite_event.get("category_id") or ""
        # subcategory_id = eventbrite_event.get("subcategory_id") or ""
        # category_name, subcategory_name = self._get_categories(category_id, subcategory_id)
        # if category_name:
        #     tags.append(models.Tag(value=category_name))
        # if subcategory_name:
        #     tags.append(models.Tag(value=subcategory_name))

        return event, [], image_result

    @functools.lru_cache
    def _get_venue_location(self, venue_id: str) -> str:
        venue_response = self.client.get_venue(venue_id)  # type: ignore
        address = venue_response["address"]
        address_1 = address["address_1"]
        address_2 = address["address_2"]
        street_address = f"{address_1} {address_2}" if address_2 else address_1
        city = address["city"]
        region = address["region"]
        postal_code = address["postal_code"]
        location = f"{street_address}, {city}, {region} {postal_code}"
        return location

    # TODO: determine if we want to use categories as tags
    # @functools.lru_cache
    # def _get_categories(self, category_id: str, subcategory_id: str) -> tuple[str, str]:
    #     category_response = self.client.get_category(category_id)
    #     category_name = category_response["name"]
    #     try:
    #         subcategories = category_response["subcategories"]
    #         subcategory = [subcategory for subcategory in subcategories if subcategory["id"] == subcategory_id][0]
    #         subcategory_name = subcategory["name"]
    #     except LookupError:
    #         subcategory_name = "'"
    #     return category_name, subcategory_name
