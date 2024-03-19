from celery import shared_task

from web import scrapers,   services


@shared_task()
def scrape_events_from_meetup():
    """Scrape upcoming events from Meetup."""
    homepage_scraper = scrapers.MeetupHomepageScraper()
    event_scraper = scrapers.MeetupEventScraper()
    meetup_service = services.MeetupService(homepage_scraper, event_scraper)
    meetup_service.scrape_events_from_meetup()
