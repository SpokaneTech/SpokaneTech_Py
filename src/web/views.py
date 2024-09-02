from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, UpdateView
from handyhelpers.mixins.view_mixins import HtmxViewMixin
from handyhelpers.views.calendar import CalendarView
from handyhelpers.views.gui import (
    HandyHelperIndexView,
    HandyHelperListPlusFilterView,
    HandyHelperListView,
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
    filter_form_url = reverse_lazy("web:filter_list_view")

    def __init__(self, **kwargs: Any) -> None:
        self.queryset = (
            Event.objects.filter(date_time__gte=timezone.localtime())
            .select_related("group")
            .prefetch_related("tags", "group__tags")
        )
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        if self.is_htmx():
            self.template_name = "web/partials/event_list.htm"
        return super().get(request, *args, **kwargs)

    def filter_by_query_params(self):
        """Include events that don't have any tags of their own but their group tags match."""
        queryset = super().filter_by_query_params()
        if queryset is None:
            return None

        if tags := self.request.GET.getlist("tags"):
            events_with_group_tags_queryset = Event.objects.filter(
                date_time__gte=timezone.localtime()
            ).filter_group_tags(tags)  # type: ignore
            queryset = queryset | events_with_group_tags_queryset

        queryset = queryset.order_by("date_time")
        return queryset


class DetailEvent(HtmxViewMixin, DetailView):
    model = Event

    def __init__(self, **kwargs: Any) -> None:
        self.queryset = Event.objects.select_related("group").prefetch_related("tags", "group__tags")
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)  # type: ignore
        user = self.request.user
        context["can_edit"] = user.is_authenticated and user.is_staff  # type: ignore
        return context

    def get(self, request, *args, **kwargs):
        if self.is_htmx():
            self.template_name = "web/partials/detail_event.htm"
        return super().get(request, *args, **kwargs)


class CreateEvent(CreateView):
    model = Event

    def get_form_class(self):
        return (
            forms.EventForm
            if self.request.user.is_authenticated and self.request.user.is_staff
            else forms.SuggestEventForm
        )

    def get_success_url(self) -> str:
        if self.object.approved_at is None:
            messages.info(
                self.request,
                "Thank you for suggesting an event. A Spokane Tech admin will "
                "review it and approve it if it meets our "
                "<a href='https://docs.spokanetech.org/CODE_OF_CONDUCT/' target='_blank'>"
                "code of conduct.</a>",
                extra_tags="safe",
            )
            return reverse("web:list_events")
        return super().get_success_url()


class UpdateEvent(RequireStaffMixin, UpdateView):
    model = Event
    form_class = forms.EventForm

    object: Event  # only populated if form successful

    def get_success_url(self) -> str:
        if self.object.approved_at is None:
            return reverse("web:list_events")
        return super().get_success_url()


class DetailTechGroup(HtmxViewMixin, DetailView):
    model = TechGroup

    def __init__(self, **kwargs: Any) -> None:
        self.queryset = TechGroup.objects.prefetch_related("event_set")
        super().__init__(**kwargs)

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
            "queryset": Event.objects.filter(date_time__gte=timezone.localtime()).order_by("date_time"),
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


class FilterListView(View):
    """apply filters, as provided via queryparameters, to a list view that uses the FilterByQueryParamsMixin"""

    def post(self, request, *args, **kwargs):
        """process POST request

        **This handles multiple values for the same filter key
        which Handy Helpers does not currently do.**
        """
        redirect_url = self.request.META["HTTP_REFERER"]
        form_parameters = self.request.POST

        # build filtered URL
        filter_url = f"{redirect_url.split('?')[0]}?"
        for key in form_parameters:
            # remove csrf token from POST parameters
            if key == "csrfmiddlewaretoken":
                continue

            values = form_parameters.getlist(key)
            for value in values:
                filter_url += f"{key}={value}&"

        return redirect(filter_url)
