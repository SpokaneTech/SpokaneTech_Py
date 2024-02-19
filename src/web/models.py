from django.db import models
from django.urls import reverse

from handyhelpers.models import HandyHelperBaseModel


class Event(HandyHelperBaseModel):
    """An event on a specific day and time."""

    name = models.CharField(max_length=64, help_text="name of this event")
    description = models.TextField(blank=True, null=True, help_text="name of this event")
    date_time = models.DateTimeField(auto_now=False, auto_now_add=False, help_text="")
    duration = models.IntegerField(blank=True, null=True, help_text="planned duration of this event")
    location = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="location where this event is being hosted",
    )
    group = models.ForeignKey("TechGroup", blank=True, null=True, on_delete=models.SET_NULL)
    # labels = models.ManyToManyField("TechnicalArea")

    # class Meta:
    #     ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.name  # type: ignore

    def get_absolute_url(self) -> str:
        return reverse("web:get_event", kwargs={"pk": self.pk})


class TechGroup(HandyHelperBaseModel):
    """A group that organizes events."""

    name = models.CharField(max_length=32, unique=True)
    description = models.TextField(blank=True, null=True)
    enabled = models.BooleanField(default=True)
    #platform = models.ForeignKey("EventPlatform", blank=True, null=True, on_delete=models.SET_NULL)
    homepage = models.URLField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("web:get_tech_group", kwargs={"pk": self.pk})