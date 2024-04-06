from typing import Callable

import pytz
from django.http import HttpRequest, HttpResponse
from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if timezone_id := request.session.get("timezone"):
            timezone.activate(pytz.timezone(timezone_id))

        return self.get_response(request)
