from datetime import datetime, timedelta

from django import template
from django.template.defaultfilters import pluralize

register = template.Library()


@register.filter(name="timedelta")
def _timedelta(duration: timedelta) -> str:
    """Format a timedelta object into a human readable string."""

    seconds = duration.seconds
    minutes = seconds // 60
    hours = minutes // 60

    result = f"{hours} hour"
    if hours > 1:
        result += "s"

    remaining_minutes = minutes % 60
    if remaining_minutes != 0:
        result += f" {remaining_minutes} minute{pluralize(remaining_minutes)}"
        if remaining_minutes > 1:
            result += "s"

    remaining_seconds = seconds % 60
    if remaining_seconds != 0:
        result += f" {remaining_seconds} second{pluralize(remaining_seconds)}"
        if remaining_seconds > 1:
            result += "1"

    return result


@register.filter(name="add_time")
def _add_time(dt: datetime, duration: timedelta) -> datetime:
    return dt + duration
