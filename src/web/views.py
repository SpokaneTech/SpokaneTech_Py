from django.http import HttpRequest, HttpResponse

from web.models import Event


# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "web/index.html")


def events(request: HttpRequest) -> HttpResponse:
    events = Event.objects.all()
    return HttpResponse("<br>".join(e.name for e in events))
