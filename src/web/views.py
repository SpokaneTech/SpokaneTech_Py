from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from django.views.generic import DetailView
from handyhelpers.views.gui import HandyHelperListView, HandyHelperIndexView
from handyhelpers.mixins.view_mixins import HtmxViewMixin
from handyhelpers.views.htmx import BuildModelSidebarNav

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


class DetailEvent(HtmxViewMixin, DetailView):
    model = Event

    def get(self, request, *args, **kwargs):
        if self.is_htmx():
            self.template_name = "web/partials/detail_event.htm"
        return super().get(request, *args, **kwargs)


class DetailTechGroup(HtmxViewMixin, DetailView):
    model = TechGroup

    def get(self, request, *args, **kwargs):
        if self.is_htmx():
            self.template_name = "web/partials/detail_tech_group.htm"
        return super().get(request, *args, **kwargs)


def list_tech_groups(request: HttpRequest) -> HttpResponse:
    groups = TechGroup.objects.all()
    return render(request, "web/list_tech_groups.html", { "groups": groups })


class BuildSidebar(BuildModelSidebarNav):
    """Get a list of upcoming Events and enabled TechGroups and render a partial to use on the sidebar navigation"""
    menu_item_list = [
        {"queryset": Event.objects.filter(date_time__gte=timezone.now()),
         "icon": """<i class="fa-solid fa-calendar-day"></i>""",
         },
        {"queryset": TechGroup.objects.filter(enabled=True),
         "icon": """<i class="fa-solid fa-people-group"></i>""",
         },
    ]
