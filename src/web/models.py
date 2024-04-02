from __future__ import annotations

from django.db import models
from django.urls import reverse
from handyhelpers.models import HandyHelperBaseModel


class TechGroup(HandyHelperBaseModel):
    """A group that organizes events."""

    name = models.CharField(max_length=32, unique=True)
    description = models.TextField(blank=True, null=True)
    enabled = models.BooleanField(default=True)
    # platform = models.ForeignKey("EventPlatform", blank=True, null=True, on_delete=models.SET_NULL)
    homepage = models.URLField(blank=True, null=True)
    icon = models.CharField(
        max_length=256,
        blank=True,
        help_text="Emojji or Font Awesome CSS icon class(es) to represent the group.",
    )

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("web:get_tech_group", kwargs={"pk": self.pk})


class Event(HandyHelperBaseModel):
    """An event on a specific day and time."""

    name = models.CharField(max_length=64, help_text="name of this event")
    description = models.TextField(blank=True, null=True, help_text="name of this event")
    date_time = models.DateTimeField(auto_now=False, auto_now_add=False, help_text="")
    duration = models.DurationField(blank=True, null=True, help_text="planned duration of this event")
    location = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="location where this event is being hosted",
    )
    url = models.URLField(
        blank=True,
        null=True,
        help_text="URL to the event details",
    )
    external_id = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        help_text="ID field for tracking a unique external event",
    )
    group = models.ForeignKey(TechGroup, blank=True, null=True, on_delete=models.SET_NULL)
    # labels = models.ManyToManyField("TechnicalArea")

    # class Meta:
    #     ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.name  # type: ignore

    def get_absolute_url(self) -> str:
        return reverse("web:get_event", kwargs={"pk": self.pk})
