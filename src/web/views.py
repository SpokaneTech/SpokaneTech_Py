from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Prefetch
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from handyhelpers.mixins.view_mixins import HtmxViewMixin, FilterByQueryParamsMixin
from handyhelpers.views.calendar import HtmxCalendarView 
from handyhelpers.views.gui import (
    HandyHelperIndexView,
    HandyHelperListPlusFilterView,
    HandyHelperListView,
)
from handyhelpers.views.htmx import (ModelDetailBootstrapModalView, 
    BuildBootstrapModalView,
    HtmxOptionView, 
    HtmxOptionDetailView, 
    HtmxOptionMultiView,
    HtmxOptionMultiFilterView)

from web import forms
from web.models import Event, TechGroup



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


class CreateTechGroup(RequireStaffMixin, CreateView):
    model = TechGroup
    form_class = forms.TechGroupForm


class UpdateTechGroup(RequireStaffMixin, UpdateView):
    model = TechGroup
    form_class = forms.TechGroupForm


class EventCalendarView(HtmxCalendarView):
    """Render a monthly calendar view of events"""
    title = "Spokane Tech Event Calendar"
    event_model = Event
    event_model_date_field = "date_time"
    event_detail_url = "web:techevent_modal"
    htmx_template_name = "web/partials/custom/calendar.htm"
    template_name = "web/full/custom/calendar.html"


class GetAboutContent(HtmxOptionView):
    """Render the 'about' page"""
    htmx_template_name = "web/partials/custom/about.htm" 
    template_name = "web/full/custom/about.html"


class GetIndexContent(HtmxOptionView):
    """Render the index page"""
    htmx_template_name = "web/partials/custom/index.htm" 
    template_name = "web/full/custom/index.html"


class GetTechEvent(HtmxOptionDetailView):
    """Get details of an Event instance"""
    model = Event
    htmx_template_name = "web/partials/detail/event.htm" 
    template_name = "web/full/detail/event.html"


class GetTechEvents(HtmxOptionMultiFilterView):
    """Get a list of Event entries"""
    template_name = "web/full/list/events.html"
    htmx_index_template_name = "web/partials/marquee/event_cards.htm"
    htmx_list_template_name = "web/partials/list/events.htm"
    queryset = Event.objects.filter(date_time__gte=timezone.now())


class GetTechEventModal(ModelDetailBootstrapModalView):
    """Get details of an Event instance and display in a modal"""
    modal_button_submit = None
    modal_title = "Event Info"
    modal_template = "web/partials/modal/event_information.htm"
    model = Event


class GetTechGroup(HtmxOptionDetailView):
    """Get details of a TechGroup instance """
    model = TechGroup
    htmx_template_name = "web/partials/detail/group.htm" 
    template_name = "web/full/detail/group.html"


class GetTechGroups(HtmxOptionMultiFilterView):
    """Get a list of TechGroup entries"""
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
