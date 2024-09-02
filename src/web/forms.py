from typing import Any

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
    date_time = forms.DateTimeField(
        widget=DateTimePickerInput,
        label="Start",
    )
    end_time = forms.DateTimeField(
        widget=DateTimePickerInput,
        label="End",
    )

    instance: models.Event

    class Meta:
        model = models.Event
        fields = [
            "name",
            "description",
            "date_time",
            "end_time",
            "location",
            "url",
            "external_id",
            "image",
            "group",
            "tags",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = "container-xs"
        self.helper.add_input(Submit("suggest", "Suggest", css_class="float-end"))

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        start = cleaned_data["date_time"]
        end = cleaned_data["end_time"]
        if start > end:
            self.add_error("date_time", "Start time is after end time.")
        return cleaned_data

    def save(self, commit: bool = True) -> Any:
        self.instance.duration = self.cleaned_data["end_time"] - self.cleaned_data["date_time"]
        return super().save(commit)


class EventForm(SuggestEventForm):
    class Meta:
        model = models.Event
        fields = SuggestEventForm.Meta.fields + ["approved_at"]


class ListEventsFilter(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        queryset=models.Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
    )
