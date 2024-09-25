import datetime
import zoneinfo
from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from web.models import Event


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
        assert response.url == reverse("web:get_events")

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

        response = self.client.get(reverse("web:get_events"))
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
        assert response.url == reverse("web:get_events")


class TestIndexView(TestCase):
    def setUp(self):
        super(TestIndexView, self).setUp()
        self.headers: dict[str, Any] = dict(HTTP_HX_REQUEST="true")
        self.now = timezone.now()
        self.url = reverse("web:index")

    def test_default(self):
        """verify call to GetIndexContent view via 'default' url with a non-htmx call"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/full/custom/index.html")

    def test_default_htmx(self):
        """verify call to GetIndexContent view via 'default' with a htmx call"""
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/partials/custom/index.htm")


class TestAboutView(TestCase):
    def setUp(self):
        super(TestAboutView, self).setUp()
        self.headers: dict[str, Any] = dict(HTTP_HX_REQUEST="true")
        self.now = timezone.now()
        self.url = reverse("web:about")

    def test_get(self):
        """verify call to GetAboutContent view with a non-htmx call"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/full/custom/about.html")

    def test_get_htmx(self):
        """verify call to GetAboutContent view with a htmx call"""
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/partials/custom/about.htm")


class TestCalendarView(TestCase):
    def setUp(self):
        super(TestCalendarView, self).setUp()
        self.headers: dict[str, Any] = dict(HTTP_HX_REQUEST="true")
        self.now = timezone.now()
        self.url = reverse("web:event_calendar", kwargs={"year": self.now.year, "month": self.now.month})

    def test_get(self):
        """verify call to EventCalendarView view with a non-htmx call"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/full/custom/calendar.html")

    def test_get_htmx(self):
        """verify call to EventCalendarView view with a htmx call"""
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/partials/custom/calendar.htm")


class TestGetTechEventView(TestCase):
    def setUp(self):
        super(TestGetTechEventView, self).setUp()
        self.instance = baker.make("web.Event", approved_at=timezone.localtime())
        self.headers: dict[str, Any] = dict(HTTP_HX_REQUEST="true")
        self.url = reverse("web:get_event", kwargs={"pk": self.instance.pk})

    def test_get(self):
        """verify call to GetTechEvent view with a non-htmx call"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/full/detail/event.html")

    def test_get_htmx(self):
        """verify call to GetTechEvent view with a htmx call"""
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/partials/detail/event.htm")
        self.assertIn(self.instance.name, response.content.decode("utf-8"))


class TestGetTechEventsView(TestCase):
    def setUp(self):
        super(TestGetTechEventsView, self).setUp()
        self.instance = baker.make("web.Event", approved_at=timezone.localtime())
        self.headers: dict[str, Any] = dict(HTTP_HX_REQUEST="true")

    def test_get(self):
        """verify call to GetTechEvents view with a non-htmx call"""
        url = reverse("web:get_events")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/full/list/events.html")

    def test_get_htmx_index(self):
        """verify call to GetTechEvents view with a htmx call"""
        url = reverse("web:get_events", kwargs={"display": "index"})
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/partials/marquee/event_cards.htm")
        self.assertIn(self.instance.name, response.content.decode("utf-8"))

    def test_get_htmx_list(self):
        """verify call to GetTechEvents view with a htmx call"""
        url = reverse("web:get_events", kwargs={"display": "list"})
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/partials/list/events.htm")
        self.assertIn(self.instance.name, response.content.decode("utf-8"))


class GetTechEventModalView(TestCase):
    def setUp(self):
        super(GetTechEventModalView, self).setUp()
        self.instance = baker.make("web.Event", approved_at=timezone.localtime())
        self.headers: dict[str, Any] = dict(HTTP_HX_REQUEST="true")
        self.url = reverse("web:techevent_modal", kwargs={"pk": self.instance.pk})

    def test_get_htmx(self):
        """verify call to GetTechEventModal view with a htmx call"""
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/partials/modal/event_information.htm")
        self.assertIn(self.instance.name, response.content.decode("utf-8"))


class TestGetTechGroupView(TestCase):
    def setUp(self):
        super(TestGetTechGroupView, self).setUp()
        self.instance = baker.make("web.TechGroup")
        self.headers: dict[str, Any] = dict(HTTP_HX_REQUEST="true")
        self.url = reverse("web:get_techgroup", kwargs={"pk": self.instance.pk})

    def test_get(self):
        """verify call to GetTechGroup view with a non-htmx call"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/full/detail/group.html")

    def test_get_htmx(self):
        """verify call to GetTechGroup view with a htmx call"""
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/partials/detail/group.htm")
        self.assertIn(self.instance.name, response.content.decode("utf-8"))


class TestGetTechGroupsView(TestCase):
    def setUp(self):
        super(TestGetTechGroupsView, self).setUp()
        self.instance = baker.make("web.TechGroup")
        self.headers: dict[str, Any] = dict(HTTP_HX_REQUEST="true")

    def test_get(self):
        """verify call to GetTechGroups view with a non-htmx call"""
        url = reverse("web:get_techgroups")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/full/list/groups.html")

    def test_get_htmx_index(self):
        """verify call to GetTechGroups view with a htmx call"""
        url = reverse("web:get_techgroups", kwargs={"display": "index"})
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/partials/marquee/group_cards.htm")
        self.assertIn(self.instance.name, response.content.decode("utf-8"))

    def test_get_htmx_list(self):
        """verify call to GetTechGroups view with a htmx call"""
        url = reverse("web:get_techgroups", kwargs={"display": "list"})
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/partials/list/groups.htm")
        self.assertIn(self.instance.name, response.content.decode("utf-8"))


class GetTechGroupModalView(TestCase):
    def setUp(self):
        super(GetTechGroupModalView, self).setUp()
        self.instance = baker.make("web.TechGroup")
        self.headers: dict[str, Any] = dict(HTTP_HX_REQUEST="true")
        self.url = reverse("web:techgroup_modal", kwargs={"pk": self.instance.pk})

    def test_get_htmx(self):
        """verify call to GetTechGroupModal view with a htmx call"""
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/partials/modal/group_information.htm")
        self.assertIn(self.instance.name, response.content.decode("utf-8"))
