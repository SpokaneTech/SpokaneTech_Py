import datetime
import zoneinfo
from typing import Any

import freezegun
import pytest
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from web.models import Event, TechGroup


@pytest.mark.django_db
def test_list_tech_groups(client: Client):
    # Arrange
    tech_group = TechGroup(
        name="List Tech Groups Test",
        description="List Tech Groups Test",
        enabled=True,
        homepage="https://spokanetech.org/",
    )
    tech_group.save()

    # Act
    url = reverse("web:list_tech_groups")
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert response.context["queryset"].get().pk == tech_group.pk


@pytest.mark.django_db
def test_get_tech_group(client: Client):
    # Arrange
    tech_group = TechGroup(
        name="Get Tech Groups Test",
        description="Get Tech Groups Test",
        enabled=True,
        homepage="https://spokanetech.org/",
    )
    tech_group.save()

    # Act
    url = reverse("web:get_tech_group", args=[tech_group.pk])
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert response.context["object"].pk == tech_group.pk


@freezegun.freeze_time("2024-03-17")
@pytest.mark.django_db
def test_set_timezone_and_timezone_middleware(client: Client):
    # Arrange
    date_time = datetime.datetime.fromisoformat("2024-03-19T01:00:00Z")
    baker.make("web.Event", date_time=date_time, approved_at=date_time)

    # Act
    client.post(reverse("web:set_timezone"), {"timezone": "America/Los_Angeles"})
    response = client.get(reverse("web:list_events"))

    # Assert
    soup = BeautifulSoup(response.content, "lxml")
    date_time_tag = soup.find(attrs={"data-testid": "date_time"})
    assert date_time_tag is not None
    actual = date_time_tag.text.strip()
    assert actual == "Monday, March 18, 2024 at 6:00 PM"


class TestEventDetailModal(TestCase):
    """test GetEventDetailsModal view"""

    def setUp(self):
        super(TestEventDetailModal, self).setUp()
        self.object = baker.make("web.Event", approved_at=timezone.localtime())
        self.headers: dict[str, Any] = dict(HTTP_HX_REQUEST="true")
        self.referrer = reverse("web:index")
        self.url = reverse("web:get_event_details", kwargs={"pk": self.object.pk})

    def test_get(self):
        """verify modal content can be rendered"""
        response = self.client.get(self.url, HTTP_REFERER=self.referrer, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/partials/modal/detail_event.htm")

    def test_non_htmx_call(self):
        """verify 400 response if non-htmx request is used"""
        response = self.client.get(self.url, HTTP_REFERER=self.referrer)
        self.assertEqual(response.status_code, 400)


class TestCreateEvent(TestCase):
    def test_suggest_event_redirects_and_sets_unapproved(self):
        # Act
        response = self.client.post(
            reverse("web:add_event"),
            {
                "name": "Event",
                "description": "",
                "date_time": "2024-04-08T07:00",
                "end_time": "2024-04-08T08:00",
                "approved_at": "",
                "location": "",
                "url": "",
                "external_id": "",
                "group": "",
            },
        )

        # Assert
        assert response.status_code == 302
        assert response.url == reverse("web:list_events")

        actual = Event.all.get()
        assert actual.approved_at is None


class TestUpdateEvent(TestCase):
    def test_update_event_sets_right_date_time(self):
        # Arrange
        object: Event = baker.make(Event, approved_at=timezone.localtime())

        timezone_str = "America/Los_Angeles"

        user_cls = get_user_model()
        user = user_cls()
        user.is_staff = True  # type: ignore
        user.save()

        # set user TZ
        self.client.post(reverse("web:set_timezone"), {"timezone": timezone_str})
        response = self.client.get(reverse("web:list_events"))
        assert response.status_code == 200

        # Act
        self.client.force_login(user)
        response = self.client.post(
            reverse("web:update_event", args=(object.pk,)),
            {
                "name": object.name,
                "description": "",
                "date_time": "2024-04-08T07:00",
                "end_time": "2024-04-08T08:00",
                "approved_at": "2024-04-08T07:00",
                "location": "",
                "url": "",
                "external_id": "",
                "group": "",
            },
        )

        # Assert
        assert response.status_code == 302

        object.refresh_from_db()
        tz_zoneinfo = zoneinfo.ZoneInfo(timezone_str)
        assert object.date_time == datetime.datetime(2024, 4, 8, 7, tzinfo=tz_zoneinfo)

    def test_update_event_remove_approved_at_redirects_to_list(self):
        # Arrange
        object: Event = baker.make(Event, approved_at=timezone.localtime())

        user_cls = get_user_model()
        user = user_cls()
        user.is_staff = True  # type: ignore
        user.save()

        # Act
        self.client.force_login(user)
        response = self.client.post(
            reverse("web:update_event", args=(object.pk,)),
            {
                "name": object.name,
                "description": "",
                "date_time": "2024-04-08T07:00",
                "end_time": "2024-04-08T08:00",
                "approved_at": "",
                "location": "",
                "url": "",
                "external_id": "",
                "group": "",
            },
        )

        # Assert
        assert response.status_code == 302
        assert response.url == reverse("web:list_events")


class TestEventCalendarView(TestCase):
    """test EventCalendarView view"""

    def setUp(self):
        super(TestEventCalendarView, self).setUp()
        self.object = baker.make("web.Event", approved_at=timezone.localtime())
        self.headers: dict[str, Any] = dict(HTTP_HX_REQUEST="true")
        self.referrer = reverse("web:index")
        self.now = timezone.now()
        self.url = reverse("web:event_calendar", kwargs={"year": self.now.year, "month": self.now.month})

    def test_get(self):
        """verify page content can be rendered"""
        response = self.client.get(self.url, HTTP_REFERER=self.referrer, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "handyhelpers/partials/calendar.htm")
        self.assertIn(self.object.name, response.content.decode("utf-8"))
        self.assertIn(f"/events/{self.object.pk}/details", response.content.decode("utf-8"))


class TestEventListView(TestCase):
    def setUp(self):
        super().setUp()
        now = timezone.localtime()
        self.tag = baker.make("web.Tag")
        self.group = baker.make("web.TechGroup")
        self.group.tags.set([self.tag])
        self.object = baker.make(
            "web.Event",
            group=self.group,
            date_time=now + datetime.timedelta(seconds=1),
            approved_at=now,
        )
        self.url = reverse("web:list_events")

    def test_filter_on_group_tags(self):
        response = self.client.get(self.url + f"?tags={self.tag.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.object.name, response.content.decode("utf-8"))

    def test_does_not_include_unapproved_events(self):
        self.object.approved_at = None
        self.object.save()
        response = self.client.get(self.url + f"?tags={self.tag.pk}")
        self.assertNotIn(self.object.name, response.content.decode("utf-8"))
