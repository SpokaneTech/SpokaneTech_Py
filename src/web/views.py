from typing import Any

from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, UpdateView
from handyhelpers.mixins.view_mixins import HtmxViewMixin
from handyhelpers.views.calendar import CalendarView
from handyhelpers.views.gui import (
    HandyHelperListPlusFilterView,
    HandyHelperListView,
    HandyHelperIndexView,
)
from handyhelpers.views.htmx import BuildBootstrapModalView, BuildModelSidebarNav

from web import forms
from web.models import Event, TechGroup


@require_http_methods(["POST"])
def set_timezone(request: HttpRequest) -> HttpResponse:
    timezone_id = request.POST["timezone"]
    request.session["timezone"] = timezone_id
    return HttpResponse()


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


class CanEditMixin:
    """Add can_edit to the template context."""

    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        can_edit = self.can_edit(request.user)
        super().setup(request, *args, can_edit=can_edit, **kwargs)  # type: ignore

    def can_edit(self, user) -> bool:
        return user.is_authenticated and user.is_staff


class RequireStaffMixin(UserPassesTestMixin):
    """Check that the user is a staff member before rendering the view."""

    request: HttpRequest

    def test_func(self) -> bool | None:
        user = self.request.user
        return user.is_authenticated and user.is_staff  # type: ignore


class ListEvents(CanEditMixin, HtmxViewMixin, HandyHelperListPlusFilterView):
    title = "Events"
    base_template = "spokanetech/base.html"
    template_name = "web/event_list.html"

    filter_form_obj = forms.ListEventsFilter

    def __init__(self, **kwargs: Any) -> None:
        self.queryset = Event.objects.filter(date_time__gte=timezone.now()).order_by("date_time")
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        if self.is_htmx():
            self.template_name = "web/partials/event_list.htm"
        return super().get(request, *args, **kwargs)


class DetailEvent(HtmxViewMixin, DetailView):
    model = Event

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)  # type: ignore
        user = self.request.user
        context["can_edit"] = user.is_authenticated and user.is_staff  # type: ignore
        return context

    def get(self, request, *args, **kwargs):
        if self.is_htmx():
            self.template_name = "web/partials/detail_event.htm"
        return super().get(request, *args, **kwargs)


class CreateEvent(RequireStaffMixin, CreateView):
    model = Event
    form_class = forms.EventForm


class UpdateEvent(RequireStaffMixin, UpdateView):
    model = Event
    form_class = forms.EventForm


class DetailTechGroup(HtmxViewMixin, DetailView):
    model = TechGroup

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["can_edit"] = user.is_authenticated and user.is_staff  # type: ignore
        return context

    def get(self, request, *args, **kwargs):
        if self.is_htmx():
            self.template_name = "web/partials/detail_tech_group.htm"
        return super().get(request, *args, **kwargs)


class ListTechGroup(CanEditMixin, HtmxViewMixin, HandyHelperListView):
    title = "Tech Groups"
    base_template = "spokanetech/base.html"
    template_name = "web/techgroup_list.html"

    def __init__(self, **kwargs: Any) -> None:
        self.queryset = TechGroup.objects.filter(enabled=True)
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        if self.is_htmx():
            self.template_name = "web/partials/techgroup_list.htm"
        return super().get(request, *args, **kwargs)


class CreateTechGroup(RequireStaffMixin, CreateView):
    model = TechGroup
    form_class = forms.TechGroupForm


class UpdateTechGroup(RequireStaffMixin, UpdateView):
    model = TechGroup
    form_class = forms.TechGroupForm


class BuildSidebar(BuildModelSidebarNav):
    """Get a list of upcoming Events and enabled TechGroups and render a partial to use on the sidebar navigation"""

    template_name = "spokanetech/htmx/build_sidebar.htm"

    menu_item_list = [
        {
            "queryset": Event.objects.filter(date_time__gte=timezone.now()).order_by("date_time"),
            "list_all_url": reverse_lazy("web:list_events"),
            "icon": """<i class="fa-solid fa-calendar-day"></i>""",
        },
        {
            "queryset": TechGroup.objects.filter(enabled=True).order_by("name"),
            "list_all_url": reverse_lazy("web:list_tech_groups"),
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
