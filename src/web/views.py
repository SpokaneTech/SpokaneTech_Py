import calendar
import re
from datetime import date

from typing import Any
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.template import loader

from django.views.generic import DetailView, CreateView
from handyhelpers.views.gui import HandyHelperListPlusCreateView, HandyHelperIndexView
from handyhelpers.views.calendar import CalendarView
from handyhelpers.mixins.view_mixins import HtmxViewMixin
from handyhelpers.views.htmx import BuildModelSidebarNav, BuildBootstrapModalView

from web import forms
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
            for tech_group in TechGroup.objects.all()
        ]
        super().__init__(**kwargs)


class ListEvents(HandyHelperListPlusCreateView):
    title = "Events"
    base_template = "spokanetech/base.html"
    table = "web/partials/table/table_events.htm"

    allow_create_groups = "admin"

    create_form_obj = forms.SuggestEventForm
    create_form_url = reverse_lazy("web:add_event")
    create_form_title = '<b>Add Event: </b><small> </small>'
    create_form_modal = 'add_event'
    create_form_modal_size = 'modal-lg'
    create_form_modal_backdrop = 'static'
    create_form_link_title = 'Add Event'
    create_form_tool_tip = 'Add Event'
    

    def __init__(self, **kwargs: Any) -> None:
        self.queryset = Event.objects.filter(
            date_time__gte=timezone.now(),
            approved=True,
        )
        super().__init__(**kwargs)


class AddEvent(CreateView):
    http_method_names = ['post']
    form_class = forms.SuggestEventForm
    success_url = reverse_lazy("web:events")


class DetailEvent(HtmxViewMixin, DetailView):
    model = Event

    def get(self, request, *args, **kwargs):
        if self.is_htmx():
            self.template_name = "web/partials/detail_event.htm"
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(approved=True)


class DetailTechGroup(HtmxViewMixin, DetailView):
    model = TechGroup

    def get(self, request, *args, **kwargs):
        if self.is_htmx():
            self.template_name = "web/partials/detail_tech_group.htm"
        return super().get(request, *args, **kwargs)


def list_tech_groups(request: HttpRequest) -> HttpResponse:
    groups = TechGroup.objects.all()
    return render(request, "web/list_tech_groups.html", {"groups": groups})


class BuildSidebar(BuildModelSidebarNav):
    """Get a list of upcoming Events and enabled TechGroups and render a partial to use on the sidebar navigation"""

    template_name = "spokanetech/htmx/build_sidebar.htm"

    menu_item_list = [
        {
            "queryset": Event.objects.filter(date_time__gte=timezone.now(), approved=True),
            "icon": """<i class="fa-solid fa-calendar-day"></i>""",
        },
        {
            "queryset": TechGroup.objects.filter(enabled=True),
            "icon": """<i class="fa-solid fa-people-group"></i>""",
        },
    ]


class GetEventDetailsModal(BuildBootstrapModalView):
    """get details of an event and display in a modal"""

    modal_button_submit = None
    modal_title = "Event Details"

    def get(self, request, *args, **kwargs):
        context = {}
        context["object"] = Event.objects.filter(approved=True).get(pk=kwargs["pk"])
        self.modal_subtitle = context["object"]
        self.modal_body = loader.render_to_string("web/partials/modal/detail_event.htm", context=context)
        return super().get(request, *args, **kwargs)


class EventCalendarView(CalendarView):
    """Render a monthly calendar view of events"""

    title = "Spokane Tech Event Calendar"
    # event_model = Event  # TODO: this does not allow using a queryset instead of a model
    queryset = Event.objects.filter(approved=True)
    event_model_date_field = "date_time"
    event_detail_url = "web:get_event_details"

    def get(self, request, *args, **kwargs):
        """Copied from https://github.com/davidslusser/django-handyhelpers/blob/main/handyhelpers/views/calendar.py#L61."""
        mo = re.search(r"^(/[^/]+/)", request.path)
        if mo:
            calendar_url_root = mo.groups()[0]
        
        today = date.today()
        year = kwargs.get("year", today.year)
        month = kwargs.get("month", today.month)
        if year == 0:
            year = today.year
        if month == 0:
            month = today.month
        next_year, next_month = self.get_next(year, month)
        prev_year, prev_month = self.get_previous(year, month)

        today_url = f"{calendar_url_root}{today.year}/{today.month}"
        prev_month_url = f"{calendar_url_root}{prev_year}/{prev_month}"
        next_month_url = f"{calendar_url_root}{next_year}/{next_month}"
        
        cal_data = calendar.monthcalendar(year, month)

        queryset = getattr(self, "queryset", None)  # NEW CODE

        if not queryset and self.event_model:
            queryset = self.event_model.objects
        
        queryset = queryset.filter(
            **{f"{self.event_model_date_field}__year": year,
                f"{self.event_model_date_field}__month": month,
                }
            )

        context = {
            "cal_data": cal_data,
            "title": self.title,
            "year": year,
            "month": month,
            "month_name": calendar.month_name[month],
            "today": today,
            "event_list": queryset,
            "use_htmx": self.use_htmx,
            "event_detail_url": self.event_detail_url,
            "today_url": today_url,
            "prev_month_url": prev_month_url,
            "next_month_url": next_month_url,
        }
        return render(request, self.template_name, context)