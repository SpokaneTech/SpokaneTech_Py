from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from web import models


class TechGroupForm(forms.ModelForm):
    class Meta:
        model = models.TechGroup
        fields = [
            "name",
            "description",
            "homepage",
            "icon",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = "container-xs"
        self.helper.add_input(Submit("save", "save", css_class="float-end"))
