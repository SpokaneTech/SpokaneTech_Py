from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from web.models import Event

def index(request: HttpRequest) -> HttpResponse:
    return render(request, "web/index.html")

def events(request: HttpRequest) -> HttpResponse:
    events = Event.objects.all()
    return HttpResponse("<br>".join(e.name for e in events))
