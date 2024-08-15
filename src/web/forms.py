from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from web import models


class DateTimePickerInput(forms.DateTimeInput):
    """DateTime input that uses browser-native calendar widget."""

    def __init__(self, attrs=None, format=None):
        attrs = attrs or {}
        attrs["type"] = "datetime-local"
        super().__init__(attrs, format)


class TechGroupForm(forms.ModelForm):
    class Meta:
        model = models.TechGroup
        fields = [
            "name",
            "description",
            "homepage",
            "icon",
            "tags",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = "container-xs"
        self.helper.add_input(Submit("save", "Save", css_class="float-end"))


class SuggestEventForm(forms.ModelForm):
    date_time = forms.DateTimeField(widget=DateTimePickerInput)

    class Meta:
        model = models.Event
        fields = [
            "name",
            "description",
            "date_time",
            "duration",
            "location",
            "url",
            "external_id",
            "group",
            "tags",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = "container-xs"
        self.helper.add_input(Submit("suggest", "Suggest", css_class="float-end"))


class EventForm(SuggestEventForm):
    date_time = forms.DateTimeField(widget=DateTimePickerInput)

    class Meta:
        model = models.Event
        fields = SuggestEventForm.Meta.fields + ["approved_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = "container-xs"
        self.helper.add_input(Submit("save", "Save", css_class="float-end"))


class ListEventsFilter(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        queryset=models.Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
    )
