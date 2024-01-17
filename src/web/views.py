from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from web.models import Event, TechGroup

def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse(b"Hello spug.")


def events(request: HttpRequest) -> HttpResponse:
    events = Event.objects.all()
    return HttpResponse("<br>".join(e.name for e in events))


def list_tech_groups(request: HttpRequest) -> HttpResponse:
    groups = TechGroup.objects.all()
    return render(request, "web/list_tech_groups.html", { "groups": groups })


def get_tech_group(request: HttpRequest, pk: int) -> HttpResponse:
    group = TechGroup.objects.get(pk=pk)
    return render(request, "web/get_tech_group.html", { "group": group })