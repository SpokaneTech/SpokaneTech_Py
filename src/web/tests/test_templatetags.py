from datetime import timedelta

from web.templatetags import web_extras


def test_timedelta_only_hours():
    duration = timedelta(hours=2)
    actual = web_extras._timedelta(duration)
    expected = "2 hours"
    assert actual == expected


def test_timedelta_hours_and_minutes():
    duration = timedelta(hours=2, minutes=30)
    actual = web_extras._timedelta(duration)
    expected = "2 hours 30 minutes"
    assert actual == expected


def test_timedelta_full():
    duration = timedelta(hours=1, minutes=2, seconds=3)
    actual = web_extras._timedelta(duration)
    expected = "1 hour 2 minutes 3 seconds"
    assert actual == expected
