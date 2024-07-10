from typing import Any

from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from handyhelpers.mixins.view_mixins import HtmxViewMixin, FilterByQueryParamsMixin
from handyhelpers.views.calendar import CalendarView
from handyhelpers.views.gui import (
    HandyHelperIndexView,
    HandyHelperListPlusFilterView,
    HandyHelperListView,
)
from handyhelpers.views.htmx import (ModelDetailBootstrapModalView, 
    HtmxOptionView, 
    HtmxOptionDetailView, 
    HtmxOptionMultiView,
    HtmxOptionMultiFilterView)

from web import forms
from web.models import Event, TechGroup


@require_http_methods(["POST"])
def set_timezone(request: HttpRequest) -> HttpResponse:
    timezone_id = request.POST["timezone"]
    request.session["timezone"] = timezone_id
    return HttpResponse()



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


class EventCalendarView(CalendarView):
    """Render a monthly calendar view of events"""
    title = "Spokane Tech Event Calendar"
    event_model = Event
    event_model_date_field = "date_time"
    event_detail_url = "web:get_event_information"


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



class GetAboutContent(HtmxOptionView):
    htmx_template_name = "web/partials/about.htm" 
    template_name = "web/full/about.html"


class GetIndexContent(HtmxOptionView):
    htmx_template_name = "web/partials/index.htm" 
    template_name = "web/full/index.html"


class GetTechEvent(HtmxOptionDetailView):
    """get details of an Event instance"""
    model = Event
    htmx_template_name = "web/partials/detail/event.htm" 
    template_name = "web/full/detail_event.html"


class GetTechEvents(HtmxOptionMultiFilterView):
    """Get a list of Event entries"""
    template_name = "web/full/list/events.html"
    htmx_index_template_name = "web/partials/marquee/event_cards.htm"
    htmx_list_template_name = "web/partials/list/events.htm"
    queryset = Event.objects.filter(date_time__gte=timezone.localtime())


class GetTechEventModal(ModelDetailBootstrapModalView):
    """get details of an Event instance and display in a modal"""
    modal_button_submit = None
    modal_title = "Event Info"
    modal_template = "web/partials/modal/event_information.htm"
    model = Event


class GetTechGroup(HtmxOptionDetailView):
    """get details of a TechGroup instance """
    model = TechGroup
    htmx_template_name = "web/partials/detail/group.htm" 
    template_name = "web/full/detail/group.html"


class GetTechGroups(HtmxOptionMultiFilterView):
    """get a list of TechGroup entries"""
    template_name = "web/full/list/groups.html"
    htmx_index_template_name = "web/partials/marquee/group_cards.htm"
    htmx_list_template_name = "web/partials/list/groups.htm"
    queryset = TechGroup.objects.filter(enabled=True)


class GetTechGroupModal(ModelDetailBootstrapModalView):
    """get details of a TechGroup instance and display in a modal"""
    modal_button_submit = None
    modal_title = "Group Info"
    modal_template = "web/partials/modal/group_information.htm"
    model = TechGroup
