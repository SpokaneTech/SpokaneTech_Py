from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from handyhelpers.views.htmx import GenericHtmxView

# import models
from web.models import Event, TechGroup


# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "web/index.html")


def events(request: HttpRequest) -> HttpResponse:
    events = Event.objects.all()
    return HttpResponse("<br>".join(e.name for e in events))


def list_tech_groups(request: HttpRequest) -> HttpResponse:
    groups = TechGroup.objects.all()
    return render(request, "web/list_tech_groups.html", { "groups": groups })


def get_tech_group(request: HttpRequest, pk: int) -> HttpResponse:
    group = TechGroup.objects.get(pk=pk)
    return render(request, "web/get_tech_group.html", { "group": group })


def get_event(request: HttpRequest, pk: int) -> HttpResponse:
    event = Event.objects.get(pk=pk)
    return render(request, "web/get_tech_group.html", { "event": event })


class GetTechGroups(GenericHtmxView):
    """Get a list of enabled TechGroups and render a partial to use on the sidebar navigation"""
    template_name = "web/partials/sidebar_items.htm"
    queryset = TechGroup.objects.filter(enabled=True)


class GetEvents(GenericHtmxView):
    """Get a list of upcoming Events and render a partial to use on the sidebar navigation"""
    template_name = "web/partials/sidebar_items.htm"
    queryset = Event.objects.filter(date_time__gte=timezone.now())
