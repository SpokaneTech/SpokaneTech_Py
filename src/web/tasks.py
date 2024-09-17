from celery import shared_task
from discord import SyncWebhook
from django.conf import settings
from django_tasks import task

from web import scrapers, services


@task
def scrape():
    scrape_events_from_meetup()
    scrape_events_from_eventbrite()


@shared_task()
def scrape_events_from_meetup():
    """Scrape upcoming events from Meetup."""
    homepage_scraper = scrapers.MeetupHomepageScraper()
    event_scraper = scrapers.MeetupEventScraper()
    meetup_service = services.MeetupService(homepage_scraper, event_scraper)
    meetup_service.save_events()


@shared_task()
def scrape_events_from_eventbrite():
    """Scrape upcoming events from Eventbrite."""
    events_scraper = scrapers.EventbriteScraper()
    meetup_service = services.EventbriteService(events_scraper)
    meetup_service.save_events()


@shared_task()
def send_events_to_discord():
    """Send upcoming events to the Discord server."""
    webhook = SyncWebhook.from_url(settings.DISCORD_WEBHOOK_URL)
    service = services.DiscordService(webhook)  # type: ignore
    service.send_events()
