from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from django.views.generic import DetailView
from handyhelpers.views.gui import HandyHelperListView, HandyHelperIndexView
from handyhelpers.views.htmx import HtmxSidebarItems

from web.models import Event, TechGroup


class Index(HandyHelperIndexView):
    title = "Spokane Tech"
    subtitle = "Index of Spokane's Tech User Groups"
    base_template = "spokanetech/base.html"

    def __init__(self, **kwargs: Any) -> None:
        self.item_list = [
            {
                "url": tech_group.get_absolute_url(),
                "icon": "fa-brands fa-python",  # TODO: add this to the TechGroup model
                "title": str(tech_group),
                "description": (tech_group.description or "")[:100],
            }
            for tech_group in
            TechGroup.objects.all()
        ]
        super().__init__(**kwargs)


class ListEvents(HandyHelperListView):
    title = "Events"
    base_template = "spokanetech/base.html"
    table = "web/partials/table/table_events.htm"

    def __init__(self, **kwargs: Any) -> None:
        self.queryset = Event.objects.filter(date_time__gte=timezone.now())
        super().__init__(**kwargs)


class DetailEvent(DetailView):
    model = Event


def list_tech_groups(request: HttpRequest) -> HttpResponse:
    groups = TechGroup.objects.all()
    return render(request, "web/list_tech_groups.html", { "groups": groups })


def get_tech_group(request: HttpRequest, pk: int) -> HttpResponse:
    group = TechGroup.objects.get(pk=pk)
    return render(request, "web/get_tech_group.html", { "group": group })


def get_event(request: HttpRequest, pk: int) -> HttpResponse:
    event = Event.objects.get(pk=pk)
    return render(request, "web/get_tech_group.html", { "event": event })


class GetTechGroups(HtmxSidebarItems):
    """Get a list of enabled TechGroups and render a partial to use on the sidebar navigation"""
    template_name = "web/partials/sidebar_items.htm"
    queryset = TechGroup.objects.filter(enabled=True)


class GetEvents(HtmxSidebarItems):
    """Get a list of upcoming Events and render a partial to use on the sidebar navigation"""
    template_name = "web/partials/sidebar_items.htm"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.queryset = Event.objects.filter(date_time__gte=timezone.now())
