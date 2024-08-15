from __future__ import annotations

import functools

from django.db import models
from django.urls import reverse
from handyhelpers.models import HandyHelperBaseModel


class Tag(HandyHelperBaseModel):
    """A Tag that describes attributes of a Event."""

    value = models.CharField(max_length=1024, unique=True, null=False)

    class Meta:
        ordering = ["value"]

    def __str__(self) -> str:
        return self.value


class TechGroup(HandyHelperBaseModel):
    """A group that organizes events."""

    name = models.CharField(max_length=1024, unique=True)
    description = models.TextField(blank=True, null=True)
    enabled = models.BooleanField(default=True)
    homepage = models.URLField(blank=True, null=True)
    icon = models.CharField(
        max_length=256,
        blank=True,
        help_text="Emojji or Font Awesome CSS icon class(es) to represent the group.",
    )
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("web:get_tech_group", kwargs={"pk": self.pk})


class EventQuerySet(models.QuerySet):
    def filter_group_tags(self, tags: list[str]):
        return self.filter(
            models.Q(tags=None)
            & functools.reduce(
                lambda a, b: a | b,
                (models.Q(group__tags__in=tag_id) for tag_id in tags),
            ),
        )


class ApprovedEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(approved_at=None)


class Event(HandyHelperBaseModel):
    """An event on a specific day and time.

    Note: Event.objects filters out unapproved events by default. Use
    Event.all to include unapproved events if needed.
    """

    name = models.CharField(max_length=1024)
    description = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField(auto_now=False, auto_now_add=False, help_text="")
    duration = models.DurationField(
        blank=True,
        null=True,
        help_text="planned duration of this event",
    )
    location = models.CharField(
        max_length=1024,
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
    tags = models.ManyToManyField(Tag, blank=True)
    approved_at = models.DateTimeField(null=True)

    objects = ApprovedEventManager.from_queryset(EventQuerySet)()
    all = EventQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=["approved_at"]),
        ]

    def __str__(self) -> str:
        return self.name  # type: ignore

    def get_absolute_url(self) -> str:
        return reverse("web:get_event", kwargs={"pk": self.pk})


class EventbriteOrganization(models.Model):
    tech_group = models.ForeignKey(TechGroup, on_delete=models.CASCADE)
    url = models.URLField()
    eventbrite_id = models.CharField(max_length=256)
