import os

import pytest


def pytest_runtest_setup(item):
    for _ in item.iter_markers(name="eventbrite"):
        if not os.environ.get("EVENTBRITE_API_TOKEN"):
            pytest.skip()
