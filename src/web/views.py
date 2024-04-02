from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template import loader
from django.utils import timezone
from django.views.generic import DetailView, ListView
from handyhelpers.mixins.view_mixins import HtmxViewMixin
from handyhelpers.views.calendar import CalendarView
from handyhelpers.views.gui import HandyHelperListView, HandyHelperIndexView
from handyhelpers.views.htmx import BuildBootstrapModalView, BuildModelSidebarNav

from web.models import Event, TechGroup


class Index(HandyHelperIndexView):
    title = "Spokane Tech"
    subtitle = "Index of Spokane's Tech User Groups"
    base_template = "spokanetech/base.html"

    def __init__(self, **kwargs: Any) -> None:
        self.item_list = [
            {
                "url": tech_group.get_absolute_url(),
                "icon": tech_group.icon,
                "title": str(tech_group),
            }
            for tech_group in TechGroup.objects.all()
        ]
        super().__init__(**kwargs)


class ListEvents(HandyHelperListView):
    title = "Events"
    base_template = "spokanetech/base.html"
    template_name = "web/event_list.html"
    table = "web/partials/table/table_events.htm"

    def __init__(self, **kwargs: Any) -> None:
        self.queryset = Event.objects.filter(date_time__gte=timezone.now()).order_by("date_time")
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


class ListTechGroup(ListView):
    model = TechGroup


def list_tech_groups(request: HttpRequest) -> HttpResponse:
    groups = TechGroup.objects.all()
    return render(request, "web/list_tech_groups.html", {"groups": groups})


class BuildSidebar(BuildModelSidebarNav):
    """Get a list of upcoming Events and enabled TechGroups and render a partial to use on the sidebar navigation"""

    template_name = "spokanetech/htmx/build_sidebar.htm"

    menu_item_list = [
        {
            "queryset": Event.objects.filter(date_time__gte=timezone.now()).order_by("date_time"),
            "icon": """<i class="fa-solid fa-calendar-day"></i>""",
        },
        {
            "queryset": TechGroup.objects.filter(enabled=True).order_by("name"),
            "icon": """<i class="fa-solid fa-people-group"></i>""",
        },
    ]


class GetEventDetailsModal(BuildBootstrapModalView):
    """get details of an event and display in a modal"""

    modal_button_submit = None
    modal_title = "Event Details"

    def get(self, request, *args, **kwargs):
        context = {}
        context["object"] = Event.objects.get(pk=kwargs["pk"])
        self.modal_subtitle = context["object"]
        self.modal_body = loader.render_to_string("web/partials/modal/detail_event.htm", context=context)
        return super().get(request, *args, **kwargs)


class EventCalendarView(CalendarView):
    """Render a monthly calendar view of events"""

    title = "Spokane Tech Event Calendar"
    event_model = Event
    event_model_date_field = "date_time"
    event_detail_url = "web:get_event_details"
