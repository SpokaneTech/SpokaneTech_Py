from typing import Any

from django import forms

from web import models, widgets


class SuggestEventForm(forms.ModelForm):
    """
    Form for a non-admin user to suggest a new event.
    
    The created event is not approved and requires review from an admin.
    """

    date_time = forms.DateTimeField(widget=widgets.DateTimePickerInput())
    duration = forms.CharField(widget=forms.TimeInput(attrs={"type": "time"}))

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
        ]

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        cleaned_data["duration"] += ":00"  # add seconds to hh:mm input
        return cleaned_data