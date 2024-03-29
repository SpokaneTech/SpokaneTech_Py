from django.forms import widgets


class DateTimePickerInput(widgets.DateTimeInput):
    """DateTime input that uses browser-native calendar widget."""

    def __init__(self, attrs=None, format=None):
        attrs = attrs or {}
        attrs["type"] = "datetime-local"
        super().__init__(attrs, format)

